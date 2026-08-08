import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from discover import discover
from validate_registry import validate


def base():
    return yaml.safe_load((ROOT / "registry.yaml").read_text())


def test_production_bridge_entry_schema_valid():
    bridge = next(
        gateway
        for gateway in base()["registry"]["gateways"]
        if gateway["name"] == "chatgpt-production-bridge"
    )

    assert bridge["version"] == "1.0.1"
    assert bridge["layer"] == "strategy"
    assert bridge["domain"] == "bridge"
    assert bridge["message_prefix"] == "bridge."
    assert bridge["error_prefix"] == "BRIDGE-ERR-"
    assert bridge["owner"] == {"team": "strategy", "maintainer": "hudongyao"}
    assert bridge["protocol"] == {"name": "HACP", "version": "1.0"}
    assert bridge["lifecycle"] == "experimental"
    assert bridge["capabilities"] == [
        "http-transport",
        "api-key-auth",
        "scope-authz",
        "audit-log",
        "strategy-boundary",
    ]
    assert validate(base()) == []


def test_discovery_by_bridge_domain():
    candidates = discover(ROOT / "registry.yaml", domain="bridge")["candidates"]

    assert candidates == [
        {
            "name": "chatgpt-production-bridge",
            "version": "1.0.1",
            "domain": "bridge",
            "lifecycle": "experimental",
            "health": "not_checked",
            "eligible_for_new_tasks": True,
        }
    ]
