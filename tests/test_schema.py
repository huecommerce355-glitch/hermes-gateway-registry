import subprocess
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / "scripts" / "validate_registry.py"

def base():
    return yaml.safe_load((ROOT / "registry.yaml").read_text())

def run(data, tmp_path):
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(data))
    return subprocess.run([sys.executable, str(VALIDATOR), "--input", str(path)], capture_output=True, text=True)

def test_valid_registry(tmp_path):
    assert run(base(), tmp_path).returncode == 0

def test_missing_owner_rejected(tmp_path):
    data = base(); data["registry"]["gateways"][0].pop("owner")
    assert run(data, tmp_path).returncode != 0

def test_invalid_lifecycle_rejected(tmp_path):
    data = base(); data["registry"]["gateways"][0]["lifecycle"] = "active"
    assert run(data, tmp_path).returncode != 0

def test_prefix_collision_rejected(tmp_path):
    data = base(); data["registry"]["gateways"][1]["message_prefix"] = data["registry"]["gateways"][0]["message_prefix"]
    assert run(data, tmp_path).returncode != 0

def test_all_gateway_entries_require_layer():
    allowed_layers = {"strategy", "management", "infrastructure"}
    gateways = base()["registry"]["gateways"]

    assert all(gateway.get("layer") in allowed_layers for gateway in gateways)
