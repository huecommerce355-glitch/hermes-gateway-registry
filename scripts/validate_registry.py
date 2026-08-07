"""Validate a Hermes gateway registry."""
import argparse, json, sys
from pathlib import Path
from normalize_protocol import parse_protocol

LIFECYCLES = {"experimental", "beta", "stable", "deprecated", "retired"}
LAYERS = {"strategy", "orchestration", "management", "infrastructure"}
DANGEROUS = ["git push", "git commit", "git add", "gh pr", "gh api --method post", "gh api --method put", "gh api --method delete", "write ", "rm -rf"]

def load(path):
    try:
        import yaml
        return yaml.safe_load(Path(path).read_text())
    except ImportError:
        return json.loads(Path(path).read_text())

def validate(data):
    errors = []
    root = data.get("registry") if isinstance(data, dict) else None
    if not isinstance(root, dict): return ["ERR-REG-001: missing registry"]
    if not isinstance(root.get("gateways"), list): return ["ERR-REG-001: gateways must be a list"]
    try: parse_protocol(root.get("protocol"))
    except (TypeError, ValueError) as exc: errors.append(f"ERR-REG-001: registry protocol: {exc}")
    names, messages, prefixes = set(), set(), set()
    required = ["name", "version", "lifecycle", "domain", "protocol", "message_prefix", "error_prefix", "operations", "probe_cmd", "owner", "boundaries"]
    for i, gateway in enumerate(root["gateways"]):
        label = f"gateway[{i}]"
        if not isinstance(gateway, dict): errors.append(f"ERR-REG-001: {label} must be an object"); continue
        for key in required:
            if key not in gateway: errors.append(f"ERR-REG-001: {label} missing {key}")
        if gateway.get("name") in names: errors.append(f"ERR-REG-001: duplicate name {gateway.get('name')}")
        names.add(gateway.get("name"))
        if gateway.get("lifecycle") not in LIFECYCLES: errors.append(f"ERR-REG-001: {label} invalid lifecycle")
        if "layer" in gateway and gateway["layer"] not in LAYERS: errors.append(f"ERR-REG-001: {label} invalid layer")
        try:
            protocol = parse_protocol(gateway.get("protocol"))
            if protocol["name"].lower() != "hacp": errors.append(f"ERR-REG-001: {label} protocol name must be HACP")
        except (TypeError, ValueError) as exc: errors.append(f"ERR-REG-001: {label} protocol: {exc}")
        owner = gateway.get("owner") or {}
        if not isinstance(owner, dict) or not owner.get("team") or not owner.get("maintainer"): errors.append(f"ERR-REG-001: {label} owner is incomplete")
        for key, seen in [("message_prefix", messages), ("error_prefix", prefixes)]:
            value = gateway.get(key)
            if not isinstance(value, str) or not value: errors.append(f"ERR-REG-001: {label} {key} invalid")
            elif value in seen: errors.append(f"ERR-REG-002: duplicate {key} {value}")
            seen.add(value)
        for token in DANGEROUS:
            if token in str(gateway.get("probe_cmd", "")).lower(): errors.append(f"ERR-REG-004: {label} unsafe probe contains {token}")
    return errors

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try: errors = validate(load(args.input))
    except Exception as exc: errors = [f"ERR-REG-001: {exc}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__": sys.exit(main())
