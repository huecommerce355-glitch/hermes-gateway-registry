import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from normalize_protocol import compare_protocol, display_protocol, parse_protocol

def test_protocol_forms():
    expected = {"name": "HACP", "version": "1.0"}
    for value in ["HACP/1.0", "HACP v1.0", "HACP-v1.0", {"name": "HACP", "version": "1.0"}]:
        assert parse_protocol(value) == expected

def test_version_extraction_and_display():
    assert parse_protocol({"name": "HACP", "version": "v1.0-preview"})["version"] == "1.0"
    assert display_protocol("HACP/1.0") == "HACP-v1.0"

def test_major_compatibility():
    assert compare_protocol("HACP/1.0", {"name": "hacp", "version": "1.9"})
    assert not compare_protocol("HACP/1.0", "HACP/2.0")
