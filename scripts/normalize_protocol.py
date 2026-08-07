"""Normalize and compare structured HACP protocol versions."""
import re

_VERSION = re.compile(r"(\d+)\.(\d+)")

def parse_protocol(value):
    if isinstance(value, str):
        name = value.split("/", 1)[0].split(" ", 1)[0].split("-", 1)[0]
        match = _VERSION.search(value)
    elif isinstance(value, dict):
        name = value.get("name")
        match = _VERSION.search(str(value.get("version", "")))
    else:
        raise ValueError("protocol must be a string or dict")
    if not name or not match:
        raise ValueError("protocol requires name and major.minor version")
    return {"name": name, "version": f"{match.group(1)}.{match.group(2)}"}

def display_protocol(value):
    protocol = parse_protocol(value)
    return f"{protocol['name']}-v{protocol['version']}"

def compare_protocol(left, right):
    a, b = parse_protocol(left), parse_protocol(right)
    return a["name"].lower() == b["name"].lower() and a["version"].split(".")[0] == b["version"].split(".")[0]

if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(); parser.add_argument("protocol")
    print(json.dumps(parse_protocol(parser.parse_args().protocol)))
