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
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--input", str(path)],
        capture_output=True,
        text=True,
    )


def test_aiwp_pipeline_entry_schema_valid(tmp_path):
    pipeline = next(
        gateway
        for gateway in base()["registry"]["gateways"]
        if gateway["name"] == "aiwp-pipeline"
    )
    assert pipeline["domain"] == "pipeline"
    assert run(base(), tmp_path).returncode == 0


def test_pipeline_domain_is_unique():
    gateways = base()["registry"]["gateways"]
    assert sum(gateway["domain"] == "pipeline" for gateway in gateways) == 1


def test_discovery_by_pipeline_domain():
    sys.path.insert(0, str(ROOT / "scripts"))
    from discover import discover

    candidates = discover(ROOT / "registry.yaml", domain="pipeline")["candidates"]
    assert candidates == [
        {
            "name": "aiwp-pipeline",
            "version": "1.2.0",
            "domain": "pipeline",
            "lifecycle": "stable",
            "health": "not_checked",
            "eligible_for_new_tasks": True,
        }
    ]
