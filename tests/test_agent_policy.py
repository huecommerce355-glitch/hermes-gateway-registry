import yaml


def coding_gateway():
    with open("registry.yaml") as registry_file:
        gateways = yaml.safe_load(registry_file)["registry"]["gateways"]
    return next(gateway for gateway in gateways if gateway["name"] == "coding-agent-gateway")


def test_coding_agent_gateway_version_is_12():
    assert coding_gateway()["version"] == "1.2.0"


def test_coding_agent_gateway_declares_dual_agent_capabilities_and_routing():
    gateway = coding_gateway()
    agents = {agent["name"]: agent for agent in gateway["capabilities"]["agents"]}

    assert agents["codex"] == {
        "name": "codex",
        "capabilities": ["implementation", "testing", "debugging"],
        "auth_status": "logged_in",
        "production": True,
    }
    assert agents["cursor"] == {
        "name": "cursor",
        "capabilities": ["code_review", "refactor", "architecture_review"],
        "auth_status": "needs_login",
        "production": True,
        "degraded_fallback": "codex.review with degraded_from: cursor",
    }
    assert gateway["routing"] == [
        {"capability": ["implementation", "testing", "debugging"], "agent": "codex"},
        {
            "capability": ["code_review", "refactor", "architecture_review"],
            "agent": "cursor",
            "fallback": "codex.review + degraded_from: cursor",
        },
    ]
