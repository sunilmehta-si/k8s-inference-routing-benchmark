import json
import re
import subprocess
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")
KNOWN_PLUGINS = {"single-profile-handler", "decode-filter", "max-score-picker", "prefix-cache-scorer", "load-aware-scorer"}


def versions() -> dict[str, str]:
    out = {}
    for line in (ROOT / "deploy/versions.env").read_text().splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            out[key] = value
    return out


class VersionsTests(unittest.TestCase):
    def test_every_image_by_digest_and_every_download_by_checksum(self):
        v = versions()
        for key in ("SIM_IMAGE", "RENDER_IMAGE", "EPP_IMAGE", "ENVOY_IMAGE", "PYTHON_IMAGE"):
            with self.subTest(key=key):
                self.assertRegex(v[key], DIGEST)
        for key in ("GIE_CRDS_SHA256", "HELM_SHA256_LINUX_AMD64", "KIND_SHA256_LINUX_AMD64"):
            self.assertRegex(v[key], r"^[0-9a-f]{64}$")
        self.assertRegex(v["ROUTER_COMMIT"], r"^[0-9a-f]{40}$")
        self.assertIn(f":{v['ROUTER_VERSION']}@", v["EPP_IMAGE"])                    # chart and image from one release
        self.assertEqual(v["KIND_CONTEXT"], "kind-irb")
        self.assertIn(f"ARG PYTHON_IMAGE={v['PYTHON_IMAGE']}\n", (ROOT / "Dockerfile").read_text())


class ModelServerTests(unittest.TestCase):
    def setUp(self):
        self.docs = [d for d in yaml.safe_load_all((ROOT / "deploy/model-servers.yaml").read_text()) if d]

    def test_simulated_vllm_with_a_prefix_cache_and_per_token_prefill(self):
        cm = next(d for d in self.docs if d["kind"] == "ConfigMap")
        cfg = yaml.safe_load(cm["data"]["config.yaml"])
        self.assertTrue(cfg["enable-kvcache"])
        self.assertEqual(cfg["latency-calculator"], "per-token")         # prefill cost scales with uncached tokens
        self.assertGreater(cfg["max-model-len"], 2700 * 1.5)                # the longest prompts, with headroom
        sim = next(d for d in self.docs if d["kind"] == "Deployment" and d["metadata"]["name"] == "sim")
        args = sim["spec"]["template"]["spec"]["containers"][0]["args"]
        self.assertIn("http://render.irb.svc:8082", args)
        self.assertEqual(sim["spec"]["template"]["metadata"]["labels"], {"app": "sim"})

    def test_the_render_server_can_run_without_a_passwd_entry(self):
        # vLLM's import calls getpass.getuser(); with no USER and no passwd entry for the UID it crashed in a loop.
        render = next(d for d in self.docs if d["kind"] == "Deployment" and d["metadata"]["name"] == "render")
        env = {e["name"]: e["value"] for e in render["spec"]["template"]["spec"]["containers"][0]["env"]}
        self.assertEqual(env["USER"], "vllm")
        self.assertTrue(env["TORCHINDUCTOR_CACHE_DIR"].startswith("/tmp/"))

    def test_pods_run_unprivileged(self):
        for d in self.docs:
            if d["kind"] != "Deployment":
                continue
            spec = d["spec"]["template"]["spec"]
            with self.subTest(deployment=d["metadata"]["name"]):
                self.assertTrue(spec["securityContext"]["runAsNonRoot"])
                for c in spec["containers"]:
                    self.assertFalse(c["securityContext"]["allowPrivilegeEscalation"])
                    self.assertEqual(c["securityContext"]["capabilities"]["drop"], ["ALL"])
                    self.assertIn("memory", c["resources"]["limits"])


class RouterConfigTests(unittest.TestCase):
    def test_each_mode_is_one_scoring_change_on_the_same_base(self):
        common = yaml.safe_load((ROOT / "deploy/router/common.yaml").read_text())["router"]
        self.assertFalse(common["proxy"]["failOpen"])                       # a broken picker fails, never bypasses
        self.assertEqual(common["inferencePool"]["failureMode"], "FailClose")
        self.assertEqual(common["modelServers"]["matchLabels"], {"app": "sim"})
        # the namespace enforces Pod Security "restricted"; without these the chart's pods are refused
        self.assertTrue(common["epp"]["podSecurityContext"]["runAsNonRoot"])
        self.assertEqual(common["epp"]["podSecurityContext"]["seccompProfile"], {"type": "RuntimeDefault"})
        for part in (common["epp"], common["proxy"]):
            self.assertFalse(part["securityContext"]["allowPrivilegeEscalation"])
            self.assertEqual(part["securityContext"]["capabilities"]["drop"], ["ALL"])
        scorers = {}
        for path in sorted((ROOT / "deploy/router").glob("*.yaml")):
            if path.name == "common.yaml":
                continue
            epp = yaml.safe_load(path.read_text())["router"]["epp"]
            config = yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
            types = {p["type"] for p in config["plugins"]}
            with self.subTest(mode=path.stem):
                self.assertEqual(types - KNOWN_PLUGINS, set())
                profile = config["schedulingProfiles"][0]["plugins"]
                self.assertEqual({p["pluginRef"] for p in profile}, types - {"single-profile-handler"})
            scorers[path.stem] = sorted(t for t in types if t.endswith("-scorer"))
        self.assertEqual(scorers, {"load-aware": ["load-aware-scorer"], "prefix-aware": ["prefix-cache-scorer"],
                                   "prefix-load-aware": ["load-aware-scorer", "prefix-cache-scorer"],
                                   "prefix-load-2x": ["load-aware-scorer", "prefix-cache-scorer"]})

    def test_prefix_load_2x_differs_from_prefix_load_aware_only_in_the_load_weight(self):
        def profile(mode):
            epp = yaml.safe_load((ROOT / f"deploy/router/{mode}.yaml").read_text())["router"]["epp"]
            config = yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
            return config, {p["pluginRef"]: p.get("weight") for p in config["schedulingProfiles"][0]["plugins"]}
        equal, equal_weights = profile("prefix-load-aware")
        heavy, heavy_weights = profile("prefix-load-2x")
        self.assertEqual(equal["plugins"], heavy["plugins"])
        self.assertEqual(equal_weights, {**heavy_weights, "load-aware-scorer": 1.0})
        self.assertEqual((heavy_weights["prefix-cache-scorer"], heavy_weights["load-aware-scorer"]), (1.0, 2.0))


class ScriptTests(unittest.TestCase):
    def test_scripts_are_strict_executable_and_valid_bash(self):
        for path in sorted((ROOT / "scripts").glob("*.sh")):
            with self.subTest(script=path.name):
                text = path.read_text()
                if path.name != "lib.sh":
                    self.assertIn("set -euo pipefail", text)
                    self.assertTrue(path.stat().st_mode & 0o111, "not executable")
                subprocess.run(["bash", "-n", str(path)], check=True)

    def test_model_servers_are_counted_only_after_every_pod_reports_ready(self):
        script = (ROOT / "scripts/deploy-servers.sh").read_text()
        rollout = script.index("rollout status deployment/sim")
        wait = script.index("wait --for=condition=Ready pod -l app=sim")
        count = script.index('ready="$(kubectl')
        self.assertLess(rollout, wait)
        self.assertLess(wait, count)

    def test_every_cluster_script_refuses_other_contexts(self):
        for path in sorted((ROOT / "scripts").glob("*.sh")):
            if path.name in ("lib.sh", "cluster-up.sh"):
                continue
            with self.subTest(script=path.name):
                self.assertIn("require_context", path.read_text())

    def test_guard_refuses_any_other_context(self):
        script = f'. "{ROOT}/scripts/lib.sh"; kubectl() {{ echo gke_prod_cluster; }}; require_context; echo reached'
        out = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertNotIn("reached", out.stdout)
        self.assertIn("refusing to run", out.stderr)


class WorkflowTests(unittest.TestCase):
    def test_the_cluster_workflow_runs_every_router_several_times_on_fresh_clusters(self):
        flow = yaml.safe_load((ROOT / ".github/workflows/cluster.yml").read_text())
        run = flow["jobs"]["run"]
        self.assertIn("[1, 2, 3]", run["strategy"]["matrix"]["repeat"])
        self.assertEqual(list(run["strategy"]["matrix"])[:2], ["repeat", "mode"])        # whole repeats start together
        routers = {p.stem for p in (ROOT / "deploy/router").glob("*.yaml")} - {"common"}
        default_modes = set(json.loads(flow[True]["workflow_dispatch"]["inputs"]["modes"]["default"]))
        self.assertEqual(default_modes, routers | {"round-robin"})                       # every router config runs
        chart_job = (ROOT / ".github/workflows/ci.yml").read_text()
        for router in routers:
            self.assertIn(router, chart_job)
            self.assertIn(router, run["strategy"]["matrix"]["mode"])
        steps = "\n".join(s.get("run", "") for s in run["steps"])
        self.assertIn("scripts/cluster-up.sh", steps)                                  # every repeat builds its own cluster
        self.assertIn('scripts/run.sh "$MODE" "$WORKLOAD" out "$SPEEDUP" "$REPEAT"', steps)
        uploads = [s["with"]["name"] for s in run["steps"] if "upload-artifact" in s.get("uses", "")]
        self.assertEqual(uploads, ["result-${{ matrix.mode }}-r${{ matrix.repeat }}"])  # repeats don't overwrite each other
        script = (ROOT / "scripts/run.sh").read_text()
        self.assertIn('name="$mode-r$repeat"', script)
        self.assertIn("--repeat $repeat", script)
        report = "\n".join(s.get("run", "") for s in flow["jobs"]["report"]["steps"])
        self.assertIn('-r*.json', report)
        # pyyaml reads the key `on` as True; docs and results pushes must not cancel a run that takes most of an hour
        self.assertEqual(flow[True]["push"]["paths-ignore"], ["**.md", "docs/**", "results/**"])

    def test_workflows_run_bash_with_pipefail_and_read_only_tokens(self):
        flows = sorted((ROOT / ".github/workflows").glob("*.yml"))
        self.assertTrue(flows)
        for path in flows:
            flow = yaml.safe_load(path.read_text())
            with self.subTest(workflow=path.name):
                self.assertEqual(flow["defaults"]["run"]["shell"], "bash")
                self.assertEqual(flow["permissions"], {"contents": "read"})
                for job in flow["jobs"].values():
                    for step in job["steps"]:
                        if "uses" in step and not step["uses"].startswith("./"):
                            self.assertRegex(step["uses"], r"@[0-9a-f]{40}( |$)", step["uses"])
