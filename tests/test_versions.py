import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, timedelta
from unittest import mock

from inference_routing_bench import versions
from inference_routing_bench.cli import main
from inference_routing_bench.versions import (COMPONENTS, NOT_COMPARED, Release, Row, VersionsError, compare, markdown,
                                              pinned_version, read_pins, report)

TODAY = date(2026, 10, 31)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, *args):
        return json.dumps(self.payload).encode()


def serving(routes):
    """A urlopen stand-in: the payload whose path ends the requested URL, else an unreachable API. Also returns the requests seen."""
    seen = []

    def urlopen(request, timeout=None):
        seen.append(request)
        for suffix, payload in routes.items():
            if request.full_url.endswith(suffix):
                return FakeResponse(payload)
        raise OSError(f"no route for {request.full_url}")
    return urlopen, seen


class CompareTests(unittest.TestCase):
    def test_how_far_behind(self):
        self.assertEqual(compare("v1.0.0", "v1.0.0"), "current")
        self.assertEqual(compare("0.21.0", "v0.21.0"), "current")         # a pin without the v its tags carry
        self.assertEqual(compare("v0.33.0", "v0.33.1"), "patch behind")
        self.assertEqual(compare("v1.6.2", "v1.7.0"), "minor behind")
        self.assertEqual(compare("v0.21.0", "v1.0.0"), "major behind")
        self.assertEqual(compare("v4.3.1", "v4.3.0"), "current")          # a pin ahead of "latest" is not behind
        self.assertEqual(compare("v1.0.0-rc.1", "v1.0.0"), "unknown")

    def test_an_image_pin_is_compared_by_its_tag(self):
        self.assertEqual(pinned_version("ghcr.io/llm-d/llm-d-inference-sim:v1.0.0@sha256:" + "0" * 64), "v1.0.0")
        self.assertEqual(pinned_version("docker.io/vllm/vllm-openai-cpu:v0.21.0@sha256:" + "0" * 64), "v0.21.0")
        self.assertEqual(pinned_version("docker.io/envoyproxy/envoy:distroless-v1.33.2@sha256:" + "0" * 64), "v1.33.2")
        self.assertEqual(pinned_version("docker.io/library/python:3.12.12-slim-bookworm@sha256:" + "0" * 64), "3.12.12")
        self.assertEqual(pinned_version("v0.33.0"), "v0.33.0")
        with self.assertRaisesRegex(VersionsError, "tag"):
            pinned_version("ghcr.io/llm-d/llm-d-inference-sim@sha256:" + "0" * 64)   # a digest alone names no release


class GithubApiTests(unittest.TestCase):
    LATEST = {"tag_name": "v1.2.3", "published_at": "2026-10-20T08:00:00Z"}

    def read(self, routes, env=None):
        urlopen, seen = serving(routes)
        with mock.patch.dict(os.environ, env or {}, clear=True), mock.patch.object(versions.urllib.request, "urlopen", urlopen):
            return versions.github_latest("o/r"), seen

    def test_the_latest_release_carries_its_tag_and_publish_date(self):
        release, _ = self.read({"/repos/o/r/releases/latest": self.LATEST})
        self.assertEqual(release, Release("v1.2.3", date(2026, 10, 20)))

    def test_a_token_raises_the_rate_limit_and_none_sends_no_header(self):
        _, seen = self.read({"/releases/latest": self.LATEST}, env={"GH_TOKEN": "t0k"})
        self.assertEqual(seen[0].get_header("Authorization"), "Bearer t0k")
        _, seen = self.read({"/releases/latest": self.LATEST})
        self.assertIsNone(seen[0].get_header("Authorization"))

    def test_the_release_notes_come_back_as_text(self):
        urlopen, _ = serving({"/releases/tags/v1.2.3": {"body": "notes"}})
        with mock.patch.object(versions.urllib.request, "urlopen", urlopen):
            self.assertEqual(versions.github_release_body("o/r", "v1.2.3"), "notes")

    def test_an_unreachable_api_is_a_versions_error_for_both_lookups(self):
        urlopen, _ = serving({})
        with mock.patch.object(versions.urllib.request, "urlopen", urlopen):
            with self.assertRaisesRegex(VersionsError, "latest release"):
                versions.github_latest("o/r")
            with self.assertRaisesRegex(VersionsError, "release notes"):
                versions.github_release_body("o/r", "v1.2.3")


class ReportTests(unittest.TestCase):
    def test_every_component_has_a_pin_in_versions_env(self):
        pins = read_pins()
        self.assertEqual(set(COMPONENTS) - set(pins), set())
        self.assertEqual(pinned_version(pins["SIM_IMAGE"]), "v1.0.0")
        self.assertEqual(pins["ROUTER_VERSION"], "v1.0.0")

    def test_every_pin_is_compared_or_says_why_not(self):
        # a new line in versions.env has to be mapped to the repository that releases it, or listed with its reason
        pins = read_pins()
        self.assertEqual(set(pins), set(COMPONENTS) | set(NOT_COMPARED))
        self.assertEqual(set(COMPONENTS) & set(NOT_COMPARED), set())

    def test_the_router_pins_move_together(self):
        # ROUTER_VERSION is what the report compares; the chart commit and the picker image must be that release
        pins = read_pins()
        self.assertEqual(pinned_version(pins["EPP_IMAGE"]), pins["ROUTER_VERSION"])

    def test_a_missing_pin_is_an_error_not_a_skipped_row(self):
        with self.assertRaisesRegex(VersionsError, "GIE_VERSION"):
            report({k: "v1.0.0" for k in COMPONENTS if k != "GIE_VERSION"}, fetch=lambda repo: Release("v1.0.0"))

    def test_rows_follow_the_component_order_and_use_the_fetched_release(self):
        rows = report({k: "v1.0.0" for k in COMPONENTS}, fetch=lambda repo: Release("v1.0.1", date(2026, 10, 1)))
        self.assertEqual([r.name for r in rows], list(COMPONENTS))
        self.assertEqual({r.status for r in rows}, {"patch behind"})

    def test_the_default_fetch_is_looked_up_when_called(self):
        with mock.patch.object(versions, "github_latest", return_value=Release("v1.0.0")) as fake:
            report({k: "v1.0.0" for k in COMPONENTS})
        self.assertEqual(fake.call_count, len(COMPONENTS))


class MarkdownTests(unittest.TestCase):
    def row(self, pinned, tag, published):
        return Row("ROUTER_VERSION", "llm-d/llm-d-router", pinned, Release(tag, published))

    def test_a_release_younger_than_two_weeks_is_too_new(self):
        fresh = self.row("v1.0.0", "v1.0.1", date(2026, 10, 25))
        self.assertTrue(fresh.too_new(TODAY))
        self.assertEqual(fresh.adoptable_on, date(2026, 11, 8))
        text = markdown([fresh], TODAY)
        self.assertIn("1 of 1 behind upstream, 1 of them too new to adopt yet", text)
        self.assertIn("patch behind; published 2026-10-25, adoptable from 2026-11-08", text)

    def test_an_old_enough_release_is_adoptable_and_current_pins_say_so(self):
        old = self.row("v0.9.0", "v1.0.0", date(2026, 10, 1))
        self.assertFalse(old.too_new(TODAY))
        text = markdown([old, self.row("v1.0.0", "v1.0.0", date(2026, 10, 25))], TODAY)
        self.assertIn("1 of 2 behind upstream\n", text)
        self.assertIn("major behind; published 2026-10-01, adoptable |", text)
        self.assertIn("| v1.0.0 | v1.0.0 | current |", text)
        self.assertIn("ROUTER_VERSION, ROUTER_COMMIT and EPP_IMAGE are one bump", text)
        self.assertIn("Not compared: KIND_NODE_IMAGE (chosen from the kind release's notes", text)
        self.assertIn("PYTHON_IMAGE (CPython publishes tags", text)


class NodeImageTests(unittest.TestCase):
    NOTES = ("Images pre-built for this release:\n* v1.37.0: `kindest/node:v1.37.0@sha256:" + "a" * 64 + "`\n"
             "* v1.36.4: `kindest/node:v1.36.4@sha256:" + "b" * 64 + "`\n")

    def test_the_pinned_node_image_must_be_one_the_kind_release_lists(self):
        pins = {"KIND_VERSION": "v0.33.0", "KIND_NODE_IMAGE": "kindest/node:v1.37.0@sha256:" + "a" * 64}
        seen = []
        def body(repo, tag):
            seen.append((repo, tag)); return self.NOTES
        self.assertTrue(versions.node_image_listed(pins, body))
        self.assertEqual(seen, [("kubernetes-sigs/kind", "v0.33.0")])
        pins["KIND_NODE_IMAGE"] = "kindest/node:v1.37.0@sha256:" + "c" * 64      # same tag, another release's build
        self.assertFalse(versions.node_image_listed(pins, body))

    def test_the_committed_pins_pass_against_the_real_notes_shape(self):
        pins = read_pins()
        notes = f"* {pins['KIND_NODE_IMAGE'].split(':')[1].split('@')[0]}: `{pins['KIND_NODE_IMAGE']}`"
        self.assertTrue(versions.node_image_listed(pins, lambda repo, tag: notes))

    def test_markdown_says_whether_the_node_image_is_listed(self):
        row = Row("KIND_VERSION", "kubernetes-sigs/kind", "v0.33.0", Release("v0.33.0", TODAY))
        self.assertIn("Node image: listed, digest and all", markdown([row], TODAY, node_image_ok=True))
        self.assertIn("**not among the images", markdown([row], TODAY, node_image_ok=False))
        self.assertNotIn("Node image:", markdown([row], TODAY))

    def test_cli_fails_when_the_node_image_is_not_listed(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(versions, "github_latest", return_value=Release("v0.33.0", date(2026, 1, 1))), \
                mock.patch.object(versions, "github_release_body", return_value="nothing here"), \
                redirect_stdout(out), redirect_stderr(err):
            self.assertEqual(main(["versions"]), 1)
        self.assertIn("not an image the pinned kind release lists", err.getvalue())


class CliTests(unittest.TestCase):
    def run_cli(self, *argv, published):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(versions, "github_latest", return_value=Release("v9.9.9", published)), \
                mock.patch.object(versions, "github_release_body", return_value=read_pins()["KIND_NODE_IMAGE"]), \
                redirect_stdout(out), redirect_stderr(err):
            code = main(["versions", *argv])
        return code, out.getvalue(), err.getvalue()

    def test_strict_fails_only_on_releases_old_enough_to_adopt(self):
        code, out, _ = self.run_cli("--strict", published=date.today() - timedelta(days=30))
        self.assertEqual(code, 1)
        self.assertIn(f"{len(COMPONENTS)} of {len(COMPONENTS)} behind upstream", out)
        code, _, err = self.run_cli("--strict", published=date.today() - timedelta(days=3))
        self.assertEqual(code, 0)
        self.assertIn("too new to adopt yet: KIND_VERSION v9.9.9", err)

    def test_without_strict_it_only_reports(self):
        self.assertEqual(self.run_cli(published=date.today() - timedelta(days=30))[0], 0)

    def test_an_unreachable_api_is_an_error(self):
        with mock.patch.object(versions, "github_latest", side_effect=VersionsError("llm-d/llm-d-router: offline")), \
                mock.patch.object(versions, "github_release_body", return_value=""), \
                redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main(["versions"]), 2)
        self.assertIn("offline", err.getvalue())

    def test_json_rows_carry_the_dates_a_tool_needs(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = f"{d}/versions.json"
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(versions, "github_latest", return_value=Release("v9.9.9", date(2026, 10, 27))), \
                    mock.patch.object(versions, "github_release_body", return_value=read_pins()["KIND_NODE_IMAGE"]), \
                    redirect_stdout(out), redirect_stderr(err):
                self.assertEqual(main(["versions", "--json", path, "-o", f"{d}/versions.md"]), 0)
            rows = json.loads(open(path).read())
        self.assertEqual([r["name"] for r in rows[:-1]], list(COMPONENTS))
        self.assertEqual(rows[-1], {"name": "KIND_NODE_IMAGE", "check": "listed in the pinned kind release's notes", "ok": True})
        rows = rows[:-1]
        self.assertEqual(rows[0]["latest"], "v9.9.9")
        self.assertEqual(rows[0]["adoptable_on"], "2026-11-10")
        self.assertEqual({r["status"] for r in rows}, {"major behind"})


if __name__ == "__main__":
    unittest.main()
