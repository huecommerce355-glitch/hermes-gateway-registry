import subprocess
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).parents[1]

def test_error_prefix_collision(tmp_path):
    data = yaml.safe_load((ROOT / "registry.yaml").read_text())
    data["registry"]["gateways"][1]["error_prefix"] = data["registry"]["gateways"][0]["error_prefix"]
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(data))
    result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_registry.py"), "--input", str(path)])
    assert result.returncode != 0
