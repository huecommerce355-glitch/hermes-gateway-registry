import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_registry import validate

def test_register_extension_with_metadata_passes():
    path = Path(__file__).parents[1] / "registry.yaml"
    base = yaml.safe_load(path.read_text())
    gateway = dict(base["registry"]["gateways"][0])
    gateway.update(name="extension-gateway", message_prefix="ext.", error_prefix="ERR-EXT-", lifecycle="beta", owner={"team": "infrastructure", "maintainer": "hudongyao"}, boundaries={"delegated_to": []}, probe_cmd="python3 -c 'print(\"ok\")'")
    base["registry"]["gateways"].append(gateway)
    assert validate(base) == []

def test_unsafe_probe_rejected():
    path = Path(__file__).parents[1] / "registry.yaml"
    base = yaml.safe_load(path.read_text())
    base["registry"]["gateways"][0]["probe_cmd"] = "git push origin main"
    assert any("ERR-REG-004" in error for error in validate(base))
