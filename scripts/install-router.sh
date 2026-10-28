#!/usr/bin/env bash
# Install the llm-d Router in standalone mode (Envoy + endpoint picker) with one of the scoring configurations
# in deploy/router/, from its Helm chart at the pinned commit.
# Usage: scripts/install-router.sh MODE   (the name of any file in deploy/router/ but common.yaml, e.g. prefix-queue)
set -euo pipefail
. "$(dirname "$0")/lib.sh"
require_context
cd "$ROOT"

mode="${1:?usage: install-router.sh MODE, one of: $(cd deploy/router && ls *.yaml | grep -vx common.yaml | sed s/.yaml$// | tr "\n" " ")}"
[ -f "deploy/router/$mode.yaml" ] || { echo "no router configuration deploy/router/$mode.yaml" >&2; exit 2; }

src="${ROUTER_SRC:-$(mktemp -d)}"
if [ ! -d "$src/.git" ]; then
  git -C "$src" init -q
  git -C "$src" fetch -q --depth 1 "$ROUTER_REPO" "$ROUTER_COMMIT"
  git -C "$src" checkout -q FETCH_HEAD
fi
[ "$(git -C "$src" rev-parse HEAD)" = "$ROUTER_COMMIT" ] || { echo "router chart is not at $ROUTER_COMMIT" >&2; exit 1; }
chart="$src/config/charts/llm-d-router-standalone"
helm dependency build "$chart" >/dev/null

# The chart builds registry/repository:tag, so the digest rides in the tag: ...endpoint-picker:v1.0.0@sha256:...
name_tag="${EPP_IMAGE##*/}"
helm upgrade --install router "$chart" --namespace "$NS" \
  -f deploy/router/common.yaml -f "deploy/router/$mode.yaml" \
  --set "router.epp.image.registry=${EPP_IMAGE%/*}" \
  --set "router.epp.image.repository=${name_tag%%:*}" --set-string "router.epp.image.tag=${name_tag#*:}" \
  --set "router.epp.image.pullPolicy=IfNotPresent" \
  --set "router.proxy.image=${ENVOY_IMAGE}" \
  --wait --timeout 10m >/dev/null
echo "router ready: llm-d Router ${ROUTER_VERSION} standalone, scoring '$mode'"
