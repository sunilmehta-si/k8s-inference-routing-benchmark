#!/usr/bin/env bash
# Replay a workload through one router from a Job inside the cluster, reading every model server's counters before
# and after, and write the result (and every request's measurements) under OUT.
# Usage: scripts/run.sh MODE WORKLOAD OUT [SPEEDUP]
#   MODE      round-robin (the plain Service) or a router installed by scripts/install-router.sh
#   WORKLOAD  a spec in workloads/, e.g. chat-rag-mix
set -euo pipefail
. "$(dirname "$0")/lib.sh"
require_context
cd "$ROOT"

mode="${1:?usage: run.sh MODE WORKLOAD OUT [SPEEDUP]}"; workload="${2:?workload}"; out="${3:?output directory}"; speedup="${4:-1}"
[ -f "workloads/$workload.yaml" ] || { echo "no workload workloads/$workload.yaml" >&2; exit 2; }
mkdir -p "$out"

if [ "$mode" = round-robin ]; then
  url="http://sim.$NS.svc:8000"
  description="Kubernetes Service: kube-proxy spreads connections over the pods, blind to load and prompt."
else
  # The chart names the Service after the release (router): router-epp, with the proxy listening on 8081.
  kubectl -n "$NS" get svc router-epp -o jsonpath='{.spec.ports[*].port}' | grep -qw 8081 \
    || { echo "no router-epp Service listening on 8081; is the router installed?" >&2; exit 1; }
  url="http://router-epp.$NS.svc:8081"
  description="llm-d Router ${ROUTER_VERSION}, standalone Envoy + endpoint picker, scoring: $(grep -m1 '^#' "deploy/router/$mode.yaml" | sed 's/^# *//')"
fi

scrape=()
while read -r pod ip; do
  scrape+=("--scrape" "$pod=http://$ip:8000/metrics")
done < <(kubectl -n "$NS" get pods -l app=sim -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.podIP}{"\n"}{end}')
[ "${#scrape[@]}" -gt 0 ] || { echo "no model server pods" >&2; exit 1; }

replicas="$(kubectl -n "$NS" get deployment sim -o jsonpath='{.spec.replicas}')"
cluster="$(python3 - "$replicas" <<'PY'
import json, os, sys, yaml
docs = yaml.safe_load_all(open("deploy/model-servers.yaml"))
cfg = next(yaml.safe_load(d["data"]["config.yaml"]) for d in docs if d and d.get("kind") == "ConfigMap")
print(json.dumps({"kind_node_image": os.environ["KIND_NODE_IMAGE"], "router": os.environ["ROUTER_VERSION"],
                  "model_server": {"image": os.environ["SIM_IMAGE"].split("@")[0], "replicas": int(sys.argv[1]),
                                   "tokenizer": os.environ["MODEL"], "config": cfg}}))
PY
)"

job="irb-$mode"
kubectl -n "$NS" delete job "$job" --ignore-not-found --wait=true >/dev/null
kubectl -n "$NS" apply -f - >/dev/null <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: $job
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 3600
  template:
    spec:
      restartPolicy: Never
      securityContext: {runAsNonRoot: true, runAsUser: 10001, seccompProfile: {type: RuntimeDefault}}
      containers:
        - name: client
          image: irb-client:dev
          imagePullPolicy: Never
          env:
            - {name: CLUSTER_JSON, value: '$(printf '%s' "$cluster" | sed "s/'/''/g")'}
          command: ["sh", "-c"]
          args:
            - |
              set -e
              printf '%s' "\$CLUSTER_JSON" > /tmp/cluster.json
              irb trace generate workloads/$workload.yaml -o /tmp/trace.jsonl
              status=0
              irb run --url $url --model $MODEL --trace /tmp/trace.jsonl --mode $mode --speedup $speedup \
                --description "$description" --cluster /tmp/cluster.json $(printf '%q ' "${scrape[@]}") \
                --raw /tmp/raw.jsonl -o /tmp/result.json || status=\$?
              echo "=== irb result"; cat /tmp/result.json
              echo "=== irb raw"; cat /tmp/raw.jsonl
              echo "=== irb end \$status"
          resources:
            requests: {cpu: 500m, memory: 256Mi}
          securityContext: {allowPrivilegeEscalation: false, capabilities: {drop: ["ALL"]}}
EOF

# Wait for the Job to finish, then read its log: attaching to a pod that may already have finished loses output.
for _ in $(seq 1 720); do
  state="$(kubectl -n "$NS" get job "$job" -o jsonpath='{.status.succeeded}{.status.failed}')"
  [ -n "$state" ] && break
  sleep 5
done
log="$out/$mode.log"
kubectl -n "$NS" logs "job/$job" > "$log"
grep -q "^=== irb end" "$log" || { echo "the load client did not finish; log in $log" >&2; tail -20 "$log" >&2; exit 1; }
sed -n '/^=== irb result$/,/^=== irb raw$/p' "$log" | sed '1d;$d' > "$out/$mode.json"
sed -n '/^=== irb raw$/,/^=== irb end/p' "$log" | sed '1d;$d' > "$out/$mode.raw.jsonl"
grep "^irb: " "$log" || true
exit "$(sed -n 's/^=== irb end //p' "$log")"
