# hermes-gateway-registry

Hermes Gateway Registry - metadata registry for infrastructure gateways (v1.0).

Unified management of:
- coding-agent-gateway v1.0.0
- github-development-gateway v1.2.0
- obsidian-knowledge-gateway v1.0.0

## Capabilities

- registry.discover: domain/operation queries with optional read-only health probes
- Version compatibility: structured HACP protocol {name, version}
- Lifecycle: experimental / beta / stable / deprecated / retired
- Safety: probe_cmd must be read-only (ERR-REG-004 enforcement)

## Tests

```bash
python3 -m pytest tests/ -v
```
