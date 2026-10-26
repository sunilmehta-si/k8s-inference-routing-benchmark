# Everyday commands. Python 3.10+ with the package installed (pip install -e .).
PY ?= python3
# MODE: round-robin, load-aware, prefix-aware or prefix-load-aware
MODE ?= prefix-load-aware
WORKLOAD ?= chat-rag-mix
SPEEDUP ?= 2

.PHONY: test trace cluster clean

test:  ## run the unit tests
	$(PY) -W error::SyntaxWarning -m unittest discover -s tests -t .

trace:  ## generate the workload's trace into runs/ and summarise it
	$(PY) -m inference_routing_bench trace generate workloads/$(WORKLOAD).yaml -o runs/$(WORKLOAD).jsonl
	$(PY) -m inference_routing_bench trace stats runs/$(WORKLOAD).jsonl

cluster:  ## replay WORKLOAD through MODE on a local kind cluster (context kind-irb only); results in runs/
	scripts/cluster-up.sh
	scripts/deploy-servers.sh 4
	if [ "$(MODE)" != "round-robin" ]; then scripts/install-router.sh $(MODE); fi
	scripts/run.sh $(MODE) $(WORKLOAD) runs $(SPEEDUP)

clean:
	rm -rf runs
