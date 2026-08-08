from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from discover import discover


def registry():
    return yaml.safe_load((ROOT / "registry.yaml").read_text())["registry"]


def final_release():
    return registry()["release"]


def test_final_manifest_pointer_versions_history_and_legacy_order():
    release = final_release()
    assert release["manifest"] == "m1.0-a-final-freeze"
    assert release["date"] == "2026-08-08"
    assert release["status"] == "frozen"
    expected_components = {
        "chatgpt-production-bridge": ("1.1.0", "v1.1.0"),
        "chatgpt-strategy-gateway": ("1.3.1", "v1.3.1"),
        "obsidian-knowledge-gateway": ("1.3.0", "v1.3.0"),
        "aiwp-pipeline": ("1.4.0", "v1.4.0"),
        "coding-agent-gateway": ("1.2.0", "v1.2.0"),
        "github-development-gateway": ("1.2.0", "v1.2.0"),
    }
    assert {
        component["name"]: (component["version"], component["tag"])
        for component in release["components"]
    } == expected_components
    history = release["release_history"]
    assert [entry["manifest"] for entry in history[:8]] == [
        "m0.1-release-freeze",
        "m0.2-active",
        "m0.2-b-active",
        "m0.2-release-freeze",
        "m1.0-a-active",
        "m1.0-a-freeze",
        "m1.0-a-review-active",
        "m1.0-a-knowledge-v13-active",
    ]
    assert len(history) == 9
    final_entry = history[-1]
    for key in (
        "manifest",
        "date",
        "status",
        "components",
        "agent_policy_version",
        "capabilities",
        "agents",
        "full_e2e_evidence",
    ):
        assert final_entry[key] == release[key]


def test_bridge_is_stable_and_discovery_reports_stable():
    bridge = next(gateway for gateway in registry()["gateways"] if gateway["name"] == "chatgpt-production-bridge")
    assert bridge["lifecycle"] == "stable"
    assert discover(ROOT / "registry.yaml", domain="bridge")["candidates"][0]["lifecycle"] == "stable"


def test_final_agent_policy_preserves_gateway_cursor_code_review():
    release = final_release()
    assert release["agent_policy_version"] == "1.0"
    assert release["agents"] == {
        "codex": {"capabilities": ["implementation", "testing", "debugging"]},
        "cursor": {"capabilities": ["review", "refactor", "architecture_review"]},
    }
    coding = next(gateway for gateway in registry()["gateways"] if gateway["name"] == "coding-agent-gateway")
    agents = {agent["name"]: agent for agent in coding["capabilities"]["agents"]}
    assert agents["cursor"]["capabilities"] == ["code_review", "refactor", "architecture_review"]


def test_final_review_capabilities_and_e2e_evidence():
    release = final_release()
    assert release["capabilities"] == [
        "production-bridge",
        "multi-agent-routing",
        "review-engine",
        "quality-gate",
        "review-knowledge",
        "full-e2e-validation",
    ]
    assert {"review-engine", "quality-gate", "review-knowledge", "full-e2e-validation"} <= set(release["capabilities"])
    assert release["full_e2e_evidence"] == {
        "trace_id": "tr-f12-e2e-001",
        "repository": "huecommerce355-glitch/hermes-codex-test",
        "pull_request": 9,
        "merge_sha": "c381591daf986dbed36d23ec93755208f7011151",
        "tag": "f12-e2e-hello-review",
        "review_decision": "PASS",
        "review_score": 92.0,
        "review_mode": "degraded",
        "review_agent": "codex.review",
        "degraded_from": "cursor",
    }
