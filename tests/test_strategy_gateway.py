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


def test_strategy_gateway_entry_schema_valid(tmp_path):
    gateways = base()["registry"]["gateways"]
    strategy = next(gateway for gateway in gateways if gateway["name"] == "chatgpt-strategy-gateway")
    assert strategy["layer"] == "strategy"
    assert run(base(), tmp_path).returncode == 0


def test_strategy_message_prefix_is_unique_and_collision_is_rejected(tmp_path):
    data = base()
    prefixes = [gateway["message_prefix"] for gateway in data["registry"]["gateways"]]
    assert prefixes.count("strategy.") == 1

    data["registry"]["gateways"][0]["message_prefix"] = "strategy."
    result = run(data, tmp_path)
    assert result.returncode != 0
    assert "duplicate message_prefix strategy." in result.stdout


def test_discovery_by_strategy_domain():
    sys.path.insert(0, str(ROOT / "scripts"))
    from discover import discover

    candidates = discover(ROOT / "registry.yaml", domain="strategy")["candidates"]
    assert candidates == [
        {
            "name": "chatgpt-strategy-gateway",
            "version": "1.3.0",
            "domain": "strategy",
            "lifecycle": "stable",
            "health": "not_checked",
            "eligible_for_new_tasks": True,
        }
    ]
