"""Return registry candidates with optional bounded health probes."""
import argparse, json, shlex, subprocess, sys
from pathlib import Path
from validate_registry import load, validate

def discover(path, domain=None, operation=None, require_health=False):
    data = load(path); errors = validate(data)
    if errors: raise ValueError("invalid registry: " + "; ".join(errors))
    candidates = []
    for gateway in data["registry"]["gateways"]:
        if domain and gateway["domain"] != domain: continue
        if operation and operation not in gateway["operations"]: continue
        item = {"name": gateway["name"], "version": gateway["version"], "domain": gateway["domain"], "lifecycle": gateway["lifecycle"], "health": "not_checked"}
        if require_health:
            try:
                completed = subprocess.run(shlex.split(gateway["probe_cmd"]), shell=False, timeout=15, capture_output=True, text=True)
                item["health"] = "healthy" if completed.returncode == 0 else "unhealthy"
            except (subprocess.TimeoutExpired, OSError): item["health"] = "unhealthy"
        item["eligible_for_new_tasks"] = gateway["lifecycle"] not in {"deprecated", "retired"}
        candidates.append(item)
    return {"candidates": candidates}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--input", default=str(Path(__file__).parents[1] / "registry.yaml")); group = parser.add_mutually_exclusive_group(required=True); group.add_argument("--domain"); group.add_argument("--operation"); parser.add_argument("--require-health", action="store_true")
    args = parser.parse_args()
    try: print(json.dumps(discover(args.input, args.domain, args.operation, args.require_health), ensure_ascii=False, indent=2)); return 0
    except Exception as exc: print(json.dumps({"error": str(exc)}, ensure_ascii=False)); return 1
if __name__ == "__main__": sys.exit(main())
