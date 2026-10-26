#!/usr/bin/env bash
# (Re)create the simulated model servers with empty prefix caches, so every router starts from the same state.
# Usage: scripts/deploy-servers.sh [REPLICAS]   (default 4)
set -euo pipefail
. "$(dirname "$0")/lib.sh"
require_context
cd "$ROOT"

export REPLICAS="${1:-4}"
manifests="$(envsubst '${RENDER_IMAGE} ${SIM_IMAGE} ${MODEL} ${REPLICAS}' < deploy/model-servers.yaml)"
kubectl -n "$NS" delete deployment sim --ignore-not-found --wait=true >/dev/null 2>&1 || true

# The simulators tokenize through the render server at startup and exit if it is not answering yet, so it comes
# first: everything but the sim Deployment, then the sims once render is ready.
without_sim="$(printf '%s\n' "$manifests" | python3 -c '
import sys, yaml
docs = [d for d in yaml.safe_load_all(sys.stdin) if d and not (d["kind"] == "Deployment" and d["metadata"]["name"] == "sim")]
print(yaml.safe_dump_all(docs))')"
printf '%s\n' "$without_sim" | kubectl apply -f - >/dev/null
if ! kubectl -n "$NS" rollout status deployment/render --timeout=900s >/dev/null; then
  echo "the render server did not become ready:" >&2
  kubectl -n "$NS" logs deployment/render --tail=60 >&2 || true
  kubectl -n "$NS" logs deployment/render --previous --tail=60 >&2 || true
  exit 1
fi
printf '%s\n' "$manifests" | kubectl apply -f - >/dev/null
kubectl -n "$NS" rollout status deployment/sim --timeout=300s >/dev/null
# A CI run once found a pod not ready a second after the rollout reported done, so wait on every pod's own Ready
# condition before counting them.
kubectl -n "$NS" wait --for=condition=Ready pod -l app=sim --timeout=120s >/dev/null || kubectl -n "$NS" get pods -l app=sim -o wide >&2
ready="$(kubectl -n "$NS" get pods -l app=sim -o jsonpath='{range .items[*]}{.status.containerStatuses[0].ready}{"\n"}{end}' | grep -c true)"
[ "$ready" = "$REPLICAS" ] || { echo "only $ready of $REPLICAS model servers are ready" >&2; exit 1; }
echo "model servers ready: $REPLICAS simulated vLLM pods (${SIM_IMAGE%@*}), tokenizer ${MODEL}"
