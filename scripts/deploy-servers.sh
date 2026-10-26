#!/usr/bin/env bash
# (Re)create the simulated model servers with empty prefix caches, so every router starts from the same state.
# Usage: scripts/deploy-servers.sh [REPLICAS]   (default 4)
set -euo pipefail
. "$(dirname "$0")/lib.sh"
require_context
cd "$ROOT"

export REPLICAS="${1:-4}"
kubectl -n "$NS" delete deployment sim --ignore-not-found --wait=true >/dev/null 2>&1 || true
envsubst '${RENDER_IMAGE} ${SIM_IMAGE} ${MODEL} ${REPLICAS}' < deploy/model-servers.yaml | kubectl apply -f - >/dev/null
kubectl -n "$NS" rollout status deployment/render --timeout=600s >/dev/null
kubectl -n "$NS" rollout status deployment/sim --timeout=300s >/dev/null
ready="$(kubectl -n "$NS" get pods -l app=sim -o jsonpath='{range .items[*]}{.status.containerStatuses[0].ready}{"\n"}{end}' | grep -c true)"
[ "$ready" = "$REPLICAS" ] || { echo "only $ready of $REPLICAS model servers are ready" >&2; exit 1; }
echo "model servers ready: $REPLICAS simulated vLLM pods (${SIM_IMAGE%@*}), tokenizer ${MODEL}"
