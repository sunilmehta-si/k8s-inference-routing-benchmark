#!/usr/bin/env bash
# Create the kind cluster (unless it exists), install the InferencePool CRD the router implements, and build and
# load the load client's image.
set -euo pipefail
. "$(dirname "$0")/lib.sh"
cd "$ROOT"

name="${KIND_CONTEXT#kind-}"
if ! kind get clusters 2>/dev/null | grep -qx "$name"; then
  kind create cluster --name "$name" --image "$KIND_NODE_IMAGE" --wait 120s
fi
kubectl config use-context "$KIND_CONTEXT" >/dev/null
require_context

crds="$(mktemp)"
curl -sSfL -o "$crds" "https://github.com/kubernetes-sigs/gateway-api-inference-extension/releases/download/${GIE_VERSION}/v1-manifests.yaml"
echo "${GIE_CRDS_SHA256}  $crds" | sha256sum -c - >/dev/null
kubectl apply --server-side -f "$crds" >/dev/null
rm -f "$crds"

docker build -q --build-arg "PYTHON_IMAGE=${PYTHON_IMAGE}" -t irb-client:dev . >/dev/null
kind load docker-image irb-client:dev --name "$name" >/dev/null
echo "cluster ready: ${KIND_CONTEXT}, InferencePool CRD ${GIE_VERSION}, load client image irb-client:dev"
