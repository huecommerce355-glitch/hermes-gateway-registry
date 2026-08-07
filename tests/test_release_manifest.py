from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def release():
    return yaml.safe_load((ROOT / "registry.yaml").read_text())["registry"]["release"]


def test_release_manifest_is_frozen():
    manifest = release()
    assert manifest["manifest"] == "m0.1-release-freeze"
    assert manifest["status"] == "frozen"


def test_release_contains_expected_components_and_versions():
    components = {component["name"]: component for component in release()["components"]}
    expected_versions = {
        "coding-agent-gateway": "1.1.0",
        "github-development-gateway": "1.2.0",
        "obsidian-knowledge-gateway": "1.0.0",
        "chatgpt-strategy-gateway": "1.0.0",
        "aiwp-pipeline": "1.0.0",
    }
    assert len(components) == len(expected_versions)
    assert set(components) == set(expected_versions)
    assert {name: component["version"] for name, component in components.items()} == expected_versions


def test_release_component_tags_are_complete():
    for component in release()["components"]:
        if component["name"] != "github-development-gateway":
            assert component["tag"].startswith("v")
