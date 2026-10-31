import json
import re
import subprocess
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")
KNOWN_PLUGINS = {
    "single-profile-handler",
    "decode-filter",
    "max-score-picker",
    "prefix-cache-scorer",
    "load-aware-scorer",
    "queue-scorer",
    "running-requests-size-scorer",
    "active-request-scorer",
    "kv-cache-utilization-scorer",
    "token-producer",
    "endpoint-notification-source",
    "precise-prefix-cache-producer",
}
# Modes that are prefix-load-aware with the load-aware scorer swapped for another of the router's load scorers.
SWAPPED_LOAD_SCORERS = {"prefix-queue": "queue-scorer", "prefix-running": "running-requests-size-scorer",
                        "prefix-active": "active-request-scorer"}
# Plugins that feed the scorers rather than score: they are declared but never appear in the scheduling profile.
NON_PROFILE_PLUGINS = {"single-profile-handler", "token-producer", "endpoint-notification-source",
                       "precise-prefix-cache-producer"}
# Modes that are the approximate prefix router of the same name with the picker's estimate replaced by the pods'
# real cache contents, read from their KV-cache events.
PRECISE_COUNTERPARTS = {"precise-aware": "prefix-aware", "precise-active": "prefix-active",
                        "precise-queue": "prefix-queue"}


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

    def test_every_pod_publishes_its_cache_events_for_the_precise_prefix_router(self):
        # The precise prefix-cache producer subscribes to tcp://<pod IP>:5557 and expects the topic kv@<ip>:<port>@<model>,
        # which the simulator builds from POD_IP and its serving port. A publisher that dials instead of binding
        # would never be reached, and without POD_IP the simulator refuses to start its cache.
        cm = next(d for d in self.docs if d["kind"] == "ConfigMap")
        cfg = yaml.safe_load(cm["data"]["config.yaml"])
        self.assertEqual(cfg["zmq-endpoint"], "tcp://*:5557")
        self.assertEqual(cfg["block-size"], 16)
        sim = next(d for d in self.docs if d["kind"] == "Deployment" and d["metadata"]["name"] == "sim")
        container = sim["spec"]["template"]["spec"]["containers"][0]
        self.assertIn({"name": "kv-events", "containerPort": 5557}, container["ports"])
        pod_ip = next(e for e in container["env"] if e["name"] == "POD_IP")
        self.assertEqual(pod_ip["valueFrom"]["fieldRef"]["fieldPath"], "status.podIP")

    def test_eight_pods_and_the_router_fit_a_four_cpu_runner(self):
        # kube-system on a kind node asks for about a CPU; everything the benchmark adds must fit in the other three
        def millicores(value):
            return int(value[:-1]) if value.endswith("m") else int(float(value) * 1000)
        docs = [d for d in yaml.safe_load_all((ROOT / "deploy/model-servers.yaml").read_text()) if d and d.get("kind") == "Deployment"]
        requests = {d["metadata"]["name"]: millicores(d["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["cpu"])
                    for d in docs}
        router = yaml.safe_load((ROOT / "deploy/router/common.yaml").read_text())["router"]
        epp = millicores(router["epp"]["resources"]["requests"]["cpu"])
        proxy = millicores(router["proxy"]["resources"]["requests"]["cpu"])
        self.assertLessEqual(requests["render"] + 8 * requests["sim"] + epp + proxy, 3000)

    def test_the_render_server_outlasts_the_simulators_idle_connections(self):
        render = next(d for d in self.docs if d["kind"] == "Deployment" and d["metadata"]["name"] == "render")
        env = {e["name"]: e["value"] for e in render["spec"]["template"]["spec"]["containers"][0]["env"]}
        # Go's http.DefaultTransport keeps idle connections 90 s; vLLM's default of 5 s made one request in a run
        # fail with a broken pipe when a simulator reused a connection the render server had just closed.
        self.assertGreater(int(env["VLLM_HTTP_TIMEOUT_KEEP_ALIVE"]), 90)

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
                self.assertEqual({p["pluginRef"] for p in profile}, types - NON_PROFILE_PLUGINS)
            scorers[path.stem] = sorted(t for t in types if t.endswith("-scorer"))
        self.assertEqual(scorers, {"load-aware": ["load-aware-scorer"], "prefix-aware": ["prefix-cache-scorer"],
                                   "prefix-load-aware": ["load-aware-scorer", "prefix-cache-scorer"],
                                   "prefix-load-2x": ["load-aware-scorer", "prefix-cache-scorer"],
                                   "prefix-load-q8": ["load-aware-scorer", "prefix-cache-scorer"],
                                   "prefix-queue": ["prefix-cache-scorer", "queue-scorer"],
                                   "prefix-running": ["prefix-cache-scorer", "running-requests-size-scorer"],
                                   "prefix-active": ["active-request-scorer", "prefix-cache-scorer"],
                                   "router-default": ["kv-cache-utilization-scorer", "prefix-cache-scorer", "queue-scorer"],
                                   "prefix-active-p2": ["active-request-scorer", "prefix-cache-scorer"],
                                   "prefix-active-a2": ["active-request-scorer", "prefix-cache-scorer"],
                                   "precise-aware": ["prefix-cache-scorer"],
                                   "precise-active": ["active-request-scorer", "prefix-cache-scorer"],
                                   "precise-queue": ["prefix-cache-scorer", "queue-scorer"],
                                   "precise-active-spec": ["active-request-scorer", "prefix-cache-scorer"]})

    def test_each_precise_mode_is_its_counterpart_with_the_real_cache_index(self):
        def config(mode):
            epp = yaml.safe_load((ROOT / f"deploy/router/{mode}.yaml").read_text())["router"]["epp"]
            return yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
        sim = yaml.safe_load(next(d for d in yaml.safe_load_all((ROOT / "deploy/model-servers.yaml").read_text())
                                  if d and d["kind"] == "ConfigMap")["data"]["config.yaml"])
        for precise, approximate in PRECISE_COUNTERPARTS.items():
            with self.subTest(mode=precise):
                cfg, base = config(precise), config(approximate)
                plugins = {p["type"]: p.get("parameters", {}) for p in cfg["plugins"]}
                # the same scorers and weights as the counterpart; only where the prefix score comes from differs
                self.assertEqual(cfg["schedulingProfiles"], base["schedulingProfiles"])
                self.assertEqual(set(plugins) - set(p["type"] for p in base["plugins"]),
                                 {"token-producer", "endpoint-notification-source", "precise-prefix-cache-producer"})
                self.assertEqual(plugins["prefix-cache-scorer"], {"prefixMatchInfoProducerName": "precise-prefix-cache-producer"})
                # the picker hashes the pods' token ids in blocks of the pods' own size, and tokenizes on the
                # render server the pods use, so a prompt's blocks hash the same on both sides
                self.assertEqual(plugins["precise-prefix-cache-producer"]["tokenProcessorConfig"]["blockSizeTokens"], sim["block-size"])
                self.assertEqual(plugins["token-producer"], {"modelName": versions()["MODEL"], "vllm": {"url": "http://render.irb.svc:8082"}})
                # the producer learns the pods from the endpoint notifications and opens one subscriber per pod
                self.assertEqual(cfg["dataLayer"]["sources"], [{"pluginRef": "endpoint-notification-source",
                                                                "extractors": [{"pluginRef": "precise-prefix-cache-producer"}]}])

    def test_precise_active_spec_differs_from_precise_active_only_in_speculative_indexing(self):
        def config(mode):
            epp = yaml.safe_load((ROOT / f"deploy/router/{mode}.yaml").read_text())["router"]["epp"]
            return yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
        spec, base = config("precise-active-spec"), config("precise-active")
        producer = next(p for p in spec["plugins"] if p["type"] == "precise-prefix-cache-producer")
        self.assertTrue(producer["parameters"].pop("speculativeIndexing"))
        self.assertEqual(spec, base)

        def config(mode):
            epp = yaml.safe_load((ROOT / f"deploy/router/{mode}.yaml").read_text())["router"]["epp"]
            return yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
        equal, q8 = config("prefix-load-aware"), config("prefix-load-q8")
        self.assertEqual(equal["schedulingProfiles"], q8["schedulingProfiles"])
        load = next(p for p in q8["plugins"] if p["type"] == "load-aware-scorer")
        self.assertEqual(load["parameters"], {"threshold": 8})
        # the simulated pods run at most 8 requests at once (deploy/model-servers.yaml)
        sims = [d for d in yaml.safe_load_all((ROOT / "deploy/model-servers.yaml").read_text()) if d and d.get("kind") == "ConfigMap"]
        self.assertEqual(yaml.safe_load(sims[0]["data"]["config.yaml"])["max-num-seqs"], 8)
        self.assertEqual([p for p in q8["plugins"] if p["type"] != "load-aware-scorer"],
                         [p for p in equal["plugins"] if p["type"] != "load-aware-scorer"])

    def test_the_other_load_scorers_replace_load_aware_and_change_nothing_else(self):
        def config(mode):
            epp = yaml.safe_load((ROOT / f"deploy/router/{mode}.yaml").read_text())["router"]["epp"]
            return yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
        base = yaml.safe_dump(config("prefix-load-aware"))
        for mode, scorer in SWAPPED_LOAD_SCORERS.items():
            with self.subTest(mode=mode):
                self.assertEqual(yaml.safe_dump(config(mode)), base.replace("load-aware-scorer", scorer))

    def test_router_default_has_the_charts_default_weights_on_the_common_base(self):
        epp = yaml.safe_load((ROOT / "deploy/router/router-default.yaml").read_text())["router"]["epp"]
        config = yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
        weights = {p["pluginRef"]: p.get("weight") for p in config["schedulingProfiles"][0]["plugins"]}
        # config/charts/routerlib/templates/_config.yaml at ROUTER_COMMIT; the chart job re-checks it against a render
        self.assertEqual(weights, {"decode-filter": None, "queue-scorer": 2.0, "kv-cache-utilization-scorer": 2.0,
                                   "prefix-cache-scorer": 3.0, "max-score-picker": None})
        self.assertIn("router-default scores like the chart's own default", (ROOT / ".github/workflows/ci.yml").read_text())

    def test_prefix_active_variants_differ_from_prefix_active_only_in_one_weight(self):
        def profile(mode):
            epp = yaml.safe_load((ROOT / f"deploy/router/{mode}.yaml").read_text())["router"]["epp"]
            config = yaml.safe_load(epp["pluginsCustomConfig"][epp["pluginsConfigFile"]])
            return config["plugins"], {p["pluginRef"]: p.get("weight") for p in config["schedulingProfiles"][0]["plugins"]}
        plugins, weights = profile("prefix-active")
        for mode, heavier in (("prefix-active-p2", "prefix-cache-scorer"), ("prefix-active-a2", "active-request-scorer")):
            with self.subTest(mode=mode):
                v_plugins, v_weights = profile(mode)
                self.assertEqual(v_plugins, plugins)
                self.assertEqual(v_weights, {**weights, heavier: 2.0})

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
        self.assertIn("github.event_name == 'push' && '[1]'", run["strategy"]["matrix"]["repeat"])   # a push runs each router once
        for name, job in flow["jobs"].items():
            self.assertNotIn("latest", str(job["runs-on"]), name)                          # the runner is pinned too
        routers = {p.stem for p in (ROOT / "deploy/router").glob("*.yaml")} - {"common"}
        default_modes = set(json.loads(flow[True]["workflow_dispatch"]["inputs"]["modes"]["default"]))
        self.assertEqual(default_modes, routers | {"round-robin"})                       # every router config runs
        chart_job = (ROOT / ".github/workflows/ci.yml").read_text()
        for router in routers:
            self.assertIn(router, chart_job)
            self.assertIn(router, run["strategy"]["matrix"]["mode"])
        self.assertIn("is not a plugin type at $ROUTER_COMMIT", chart_job)            # typos fail before a cluster run
        steps = "\n".join(s.get("run", "") for s in run["steps"])
        self.assertIn("scripts/cluster-up.sh", steps)                                  # every repeat builds its own cluster
        self.assertIn('scripts/deploy-servers.sh "$REPLICAS"', steps)                  # the pod count is a dispatch input
        self.assertEqual(flow[True]["workflow_dispatch"]["inputs"]["replicas"]["default"], "4")
        self.assertEqual(run["env"]["REPLICAS"], "${{ inputs.replicas || '4' }}")
        self.assertIn('scripts/run.sh "$MODE" "$WORKLOAD" out "$SPEEDUP" "$REPEAT"', steps)
        uploads = [s["with"]["name"] for s in run["steps"] if "upload-artifact" in s.get("uses", "")]
        self.assertEqual(uploads, ["result-${{ matrix.mode }}-r${{ matrix.repeat }}"])  # repeats don't overwrite each other
        script = (ROOT / "scripts/run.sh").read_text()
        self.assertIn('name="$mode-r$repeat"', script)
        self.assertIn("--repeat $repeat", script)
        report = "\n".join(s.get("run", "") for s in flow["jobs"]["report"]["steps"])
        self.assertIn('-r*.json', report)
        # the report compares exactly the routers the matrix ran
        compare = next(s for s in flow["jobs"]["report"]["steps"] if s.get("name") == "Compare the routers")
        matrix_modes = run["strategy"]["matrix"]["mode"]
        self.assertEqual("${{ fromJSON(" + compare["env"]["MODES"][4:-3] + ") }}", matrix_modes)
        self.assertIn('jq -r \'.[]\' <<<"$MODES"', compare["run"])
        # pyyaml reads the key `on` as True; docs and results pushes must not cancel a run that takes most of an hour
        self.assertEqual(flow[True]["push"]["paths-ignore"], ["**.md", "docs/**", "results/**"])
        # and a push must never cancel a dispatched experiment: the two are different concurrency groups
        self.assertIn("${{ github.event_name }}", flow["concurrency"]["group"])
        self.assertEqual(flow["concurrency"]["cancel-in-progress"], "${{ github.event_name != 'workflow_dispatch' }}")

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
