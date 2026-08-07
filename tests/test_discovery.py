import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from discover import discover

ROOT = Path(__file__).parents[1]

def test_domain_and_operation_queries():
    path = ROOT / "registry.yaml"
    assert discover(path, domain="github-lifecycle")["candidates"][0]["name"] == "github-development-gateway"
    assert discover(path, operation="knowledge.write")["candidates"][0]["name"] == "obsidian-knowledge-gateway"

def test_deprecated_visible_but_ineligible(tmp_path):
    data = yaml.safe_load((ROOT / "registry.yaml").read_text())
    data["registry"]["gateways"][0]["lifecycle"] = "deprecated"
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(data))
    item = discover(path, domain="coding")["candidates"][0]
    assert item["lifecycle"] == "deprecated" and not item["eligible_for_new_tasks"]
