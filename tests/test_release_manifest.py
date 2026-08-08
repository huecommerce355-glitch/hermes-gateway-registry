from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def release():
    return yaml.safe_load((ROOT / "registry.yaml").read_text())["registry"]["release"]


def test_current_manifest_points_to_latest_frozen():
    manifest = release()
    assert manifest["manifest"] == "m0.2-release-freeze"
    assert manifest["status"] == "frozen"
    history = {entry["manifest"]: entry for entry in manifest["release_history"]}
    assert history[manifest["manifest"]]["status"] == "frozen"


def test_release_contains_expected_components_and_versions():
    components = {component["name"]: component for component in release()["components"]}
    expected_versions = {
        "coding-agent-gateway": "1.1.0",
        "github-development-gateway": "1.2.0",
        "obsidian-knowledge-gateway": "1.2.0",
        "chatgpt-strategy-gateway": "1.2.0",
        "aiwp-pipeline": "1.2.0",
    }
    assert len(components) == len(expected_versions)
    assert set(components) == set(expected_versions)
    assert {name: component["version"] for name, component in components.items()} == expected_versions


def test_release_component_tags_are_complete():
    for component in release()["components"]:
        assert component["tag"].startswith("v")


def test_release_history_contains_active_m02_manifest():
    history = {entry["manifest"]: entry for entry in release()["release_history"]}
    assert len(history) == 5
    assert history["m0.1-release-freeze"]["status"] == "frozen"

    active = history["m0.2-active"]
    assert active["date"] == "2026-08-07"
    assert active["status"] == "active"
    components = {component["name"]: component for component in active["components"]}
    expected_versions = {
        "obsidian-knowledge-gateway": "1.1.0",
        "chatgpt-strategy-gateway": "1.1.0",
        "aiwp-pipeline": "1.1.0",
    }
    assert {name: components[name]["version"] for name in expected_versions} == expected_versions

    active_b = history["m0.2-b-active"]
    assert active_b["date"] == "2026-08-08"
    assert active_b["status"] == "active"
    components = {component["name"]: component for component in active_b["components"]}
    expected_versions = {
        "obsidian-knowledge-gateway": "1.2.0",
        "chatgpt-strategy-gateway": "1.2.0",
        "aiwp-pipeline": "1.2.0",
    }
    assert {name: components[name]["version"] for name in expected_versions} == expected_versions


def test_release_history_contains_m02_release_freeze_manifest():
    history = {entry["manifest"]: entry for entry in release()["release_history"]}
    freeze = history["m0.2-release-freeze"]

    assert freeze["date"] == "2026-08-08"
    assert freeze["status"] == "frozen"
    expected_versions = {
        "chatgpt-strategy-gateway": ("1.2.0", "v1.2.0"),
        "obsidian-knowledge-gateway": ("1.2.0", "v1.2.0"),
        "aiwp-pipeline": ("1.2.0", "v1.2.0"),
        "coding-agent-gateway": ("1.1.0", "v1.1.0"),
        "github-development-gateway": ("1.2.0", "v1.2.0"),
    }
    components = {component["name"]: component for component in freeze["components"]}
    assert set(components) == set(expected_versions)
    assert {
        name: (component["version"], component["tag"])
        for name, component in components.items()
    } == expected_versions

    records = freeze["records"]
    assert len(records["adrs_accepted"]) == 6
    assert set(records["adrs_accepted"]) == {
        "ADR-001",
        "ADR-002",
        "ADR-003",
        "ADR-004",
        "ADR-005",
        "ADR-006",
    }
    assert records["adr_status"] == "all accepted"
    assert "trace-context:" in "\n".join(records["capabilities"])
    assert "parallel-pipeline:" in "\n".join(records["capabilities"])


def test_release_history_contains_m10_a_active_manifest():
    history = {entry["manifest"]: entry for entry in release()["release_history"]}
    active = history["m1.0-a-active"]

    assert active["date"] == "2026-08-08"
    assert active["status"] == "active"
    expected_components = {
        "chatgpt-strategy-gateway": ("1.3.0", "v1.3.0"),
        "chatgpt-production-bridge": ("1.0.1", "v1.0.1"),
        "obsidian-knowledge-gateway": ("1.2.0", "v1.2.0"),
        "aiwp-pipeline": ("1.2.0", "v1.2.0"),
        "coding-agent-gateway": ("1.1.0", "v1.1.0"),
        "github-development-gateway": ("1.2.0", "v1.2.0"),
    }
    components = {component["name"]: component for component in active["components"]}
    assert {
        name: (component["version"], component["tag"])
        for name, component in components.items()
    } == expected_components
    assert active["records"] == {
        "adr_status": "7 ADRs (1-6 accepted, 7 proposed)",
        "capability": "chatgpt-production-bridge",
    }
