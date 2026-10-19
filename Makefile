.PHONY: run setup contributors check replay

run:            ## start the dashboard on http://127.0.0.1:8765
	python3 server/app.py

setup:          ## build every lane from public sources into build/ (needs HARNESS_DIR, see docs/setup.md)
	scripts/setup.sh

contributors:   ## refresh web/data/contributors.json from provably.fast
	python3 scripts/fetch_contributors.py

check:          ## syntax checks + hook self-tests
	python3 -m py_compile server/app.py server/race.py scripts/fetch_contributors.py
	node --check web/app.js
	python3 -c "import json; json.load(open('races.json')); json.load(open('web/data/contributors.json')); json.load(open('web/data/sample-run.json'))"
	bash .claude/hooks/clean-attribution-guard.test.sh
	bash -n scripts/setup.sh

replay:         ## open the labelled replay of the recorded sample run
	xdg-open "http://127.0.0.1:8765/?replay" >/dev/null 2>&1 || echo "open http://127.0.0.1:8765/?replay"
