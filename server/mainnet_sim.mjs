// Price one Falcon-signed transaction on Starknet mainnet, for the original and the record account,
// WITHOUT broadcasting anything. For each account class: declare it (signed by a funded account), deploy
// a Falcon account from it and send one Falcon-signed invoke (a 0 STRK transfer), all in one
// starknet_simulateTransactions batch on the latest block with SKIP_FEE_CHARGE (nothing is paid) and
// validation ON (the Falcon signature is really verified on-chain). Fees are gas used x block prices.
//
// Configuration (JSON on argv[2]; see docs/setup.md, "Mainnet price"):
//   env        .env holding PQ_RPC, PQ_FUNDER_ADDRESS, PQ_FUNDER_PRIVATE_KEY (kept outside this repo)
//   rpc        optional RPC override that accepts multi-MB declare payloads
//   side_rpc   optional { side: url | "env" }: a separate RPC per side, so both simulate at once
//   cli        an OpenZeppelin pq-accounts/cli checkout with node_modules and dist built
//   falcon_py  a falcon.py checkout; falcon_key  a Falcon key file (any key: nothing is broadcast)
//   sides      { "original": "<tree>", "record": "<tree>" } trees with pq_accounts built in target/dev
// Prints one JSON object on stdout.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { createHash } from "node:crypto";

// How many 136-byte SHAKE-256 blocks Falcon's hash-to-point squeezes for (message, salt): 8 or 9 for
// almost every signature, and the main driver of verification gas, so both sides are priced on
// signatures of the same block count.
function shakeBlocks(messageHash, saltA, saltB) {
  const le = (v, n) => Buffer.from(BigInt(v).toString(16).padStart(n * 2, "0"), "hex").reverse();
  const stream = createHash("shake256", { outputLength: 136 * 14 })
    .update(Buffer.concat([le(saltA, 20), le(saltB, 20), le(messageHash, 32)])).digest();
  let accepted = 0, used = 0;
  while (accepted < 512) {
    if ((stream[2 * used] << 8 | stream[2 * used + 1]) < 61445) accepted++;
    used++;
  }
  return Math.ceil(used / 68);
}

const cfg = JSON.parse(readFileSync(process.argv[2], "utf8"));
const sn = await import(`${cfg.cli}/node_modules/starknet/dist/index.mjs`);
const { RpcProvider, Account, hash } = sn;
const { resolveScheme } = await import(`${cfg.cli}/dist/schemes/registry.js`);
const { falconSignerMaterial } = await import(`${cfg.cli}/dist/options.js`);

const env = Object.fromEntries(readFileSync(cfg.env, "utf8").split("\n")
  .filter((l) => l.includes("=") && !l.startsWith("#"))
  .map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1).trim()]));
const provider = new RpcProvider({ nodeUrl: cfg.rpc || env.PQ_RPC });
const chainId = await provider.getChainId();
const block = await provider.getBlock("latest");
const fri = (p) => BigInt(p.price_in_fri);
const prices = { l1: fri(block.l1_gas_price), l2: fri(block.l2_gas_price), l1d: fri(block.l1_data_gas_price) };
// Price ceilings come from the live block prices (twice the price, rounded up to a power of two), so
// they are never hard-coded and change only when the market moves a lot; while they hold, the
// transaction hashes repeat and the Falcon signatures can be reused from a private cache. The fee
// reported is always the gas used times this block's live prices.
const ceil = (now) => { let c = 1n; while (c < now * 2n) c <<= 1n; return c; };
const bounds = {
  l1_gas: { max_amount: 10n ** 7n, max_price_per_unit: ceil(prices.l1) },
  l2_gas: { max_amount: 10n ** 12n, max_price_per_unit: ceil(prices.l2) },
  l1_data_gas: { max_amount: 10n ** 7n, max_price_per_unit: ceil(prices.l1d) },
};
const common = { version: "0x3", chainId, cairoVersion: "1", resourceBounds: bounds, tip: 0n, paymasterData: [],
  accountDeploymentData: [], nonceDataAvailabilityMode: "L1", feeDataAvailabilityMode: "L1" };
const boundsKey = Object.values(bounds).map((b) => b.max_price_per_unit.toString(16)).join("-");

const funder = new Account({ provider, address: env.PQ_FUNDER_ADDRESS, signer: env.PQ_FUNDER_PRIVATE_KEY });
const funderNonce = BigInt(await provider.getNonceForAddress(env.PQ_FUNDER_ADDRESS, "latest"));
const scheme = resolveScheme("falcon-512-shake", true);
const material = falconSignerMaterial(cfg.falcon_py, cfg.falcon_key);
const STRK = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d";
const cachePath = cfg.cache ?? `${dirname(cfg.falcon_key)}/mainnet-sim-cache.json`;
let cache = {};
try { cache = JSON.parse(readFileSync(cachePath, "utf8")); } catch { /* first run */ }
if (!cache.publicKey) cache.publicKey = (await scheme.publicKey({ signer: material })).map(String);
const constructorCalldata = scheme.constructorCalldata(cache.publicKey);
const falconSigner = await scheme.createStarknetSigner({ signer: material });

/** Falcon signer that reuses a cached signature for an identical transaction (same key). */
function cachedSigner(key) {
  return {
    getPubKey: () => falconSigner.getPubKey?.(),
    signMessage: (...a) => falconSigner.signMessage(...a),
    signDeclareTransaction: (...a) => falconSigner.signDeclareTransaction(...a),
    async signDeployAccountTransaction(details) {
      const k = `${key}:deploy`;
      if (!cache[k]) cache[k] = (await falconSigner.signDeployAccountTransaction(details)).map(String);
      return cache[k];
    },
    async signTransaction(calls, details) {
      return (await falconSigner.signTransaction(calls, details)).map(String);
    },
  };
}

const out = { network: "mainnet", block: block.block_number, timestamp: block.timestamp,
  prices_fri: Object.fromEntries(Object.entries(prices).map(([k, v]) => [k, v.toString()])), sides: {} };
const step = (r) => {
  const t = r.transaction_trace ?? {};
  const res = t.execution_resources ?? {};
  const l2 = BigInt(res.l2_gas ?? 0), l1 = BigInt(res.l1_gas ?? 0), l1d = BigInt(res.l1_data_gas ?? 0);
  const fee = l2 * prices.l2 + l1 * prices.l1 + l1d * prices.l1d;
  const reverted = t.execute_invocation?.revert_reason ?? null;
  return { l2_gas: Number(l2), l1_data_gas: Number(l1d), fee_strk: Number(fee) / 1e18, reverted };
};

let salt = 1n;
let targetBlocks = null;
const pending = [];
for (const [side, tree] of Object.entries(cfg.sides)) {
  const base = `${tree}/target/dev/pq_accounts_Falcon512ShakeAccount`;
  const sierra = JSON.parse(readFileSync(`${base}.contract_class.json`, "utf8"));
  const casm = JSON.parse(readFileSync(`${base}.compiled_contract_class.json`, "utf8"));
  const classHash = hash.computeContractClassHash(sierra);
  const addressSalt = "0x" + (salt++).toString(16);
  const address = hash.calculateContractAddressFromHash(addressSalt, classHash, constructorCalldata, 0);
  const key = `${chainId}:${classHash}:${addressSalt}:${boundsKey}`;
  const account = new Account({ provider, address, signer: cachedSigner(key), cairoVersion: "1" });
  const declare = await funder.buildDeclarePayload({ contract: sierra, casm }, { ...common, walletAddress: funder.address, nonce: funderNonce });
  const deploy = await account.buildAccountDeployPayload({ classHash, addressSalt, constructorCalldata, contractAddress: address },
    { ...common, walletAddress: address, nonce: 0n });
  const calls = [{ contractAddress: STRK, entrypoint: "transfer", calldata: [env.PQ_FUNDER_ADDRESS, "0", "0"] }];
  const invokeDetails = { ...common, walletAddress: address, nonce: 1n };
  const txHash = hash.calculateInvokeTransactionHash({ ...invokeDetails, senderAddress: address,
    compiledCalldata: sn.transaction.getExecuteCalldata(calls, "1"), version: "0x3",
    nonceDataAvailabilityMode: sn.stark.intDAM("L1"), feeDataAvailabilityMode: sn.stark.intDAM("L1") });
  // Reuse a cached invoke signature when it has the wanted SHAKE block count; otherwise draw new ones
  // (the signer picks a fresh random salt each time) until both sides match.
  const ik = `${key}:invoke`;
  let invoke = await account.buildInvocation(calls, invokeDetails);
  if (cache[ik] && (targetBlocks === null || cache[ik].blocks === targetBlocks)) {
    invoke.signature = cache[ik].signature;
  } else {
    for (let tries = 0; tries < 12; tries++) {
      const sig = invoke.signature.map(String);
      const blocks = shakeBlocks(txHash, sig[29], sig[30]);
      cache[ik] = { signature: sig, blocks };
      if (targetBlocks === null || blocks === targetBlocks) break;
      invoke = await account.buildInvocation(calls, invokeDetails);
    }
  }
  if (targetBlocks === null) targetBlocks = cache[ik].blocks;
  const url = cfg.side_rpc?.[side] === "env" ? env.PQ_RPC : cfg.side_rpc?.[side];
  const sideProvider = url ? new RpcProvider({ nodeUrl: url }) : provider;
  const blocks = cache[ik].blocks;
  const run = () => sideProvider.getSimulateTransaction([
    { type: "DECLARE", ...common, nonce: funderNonce, ...declare },
    { type: "DEPLOY_ACCOUNT", ...common, nonce: 0n, ...deploy },
    { type: "INVOKE", ...common, nonce: 1n, ...invoke },
  ], { blockIdentifier: "latest", skipValidate: false, skipFeeCharge: true }).then((sim) => {
    const list = Array.isArray(sim) ? sim : sim.simulated_transactions;
    out.sides[side] = { class_hash: classHash, shake_blocks: blocks, declare: step(list[0]), deploy_account: step(list[1]), invoke: step(list[2]) };
  });
  // Sides on their own RPC run at once; sides sharing one RPC run one after the other (public RPCs
  // refuse two multi-MB requests at once).
  if (url) pending.push(run()); else await run();
}
await Promise.all(pending);
out.sides = { original: out.sides.original, record: out.sides.record };
writeFileSync(cachePath, JSON.stringify(cache), { mode: 0o600 });
process.stdout.write(JSON.stringify(out) + "\n");
