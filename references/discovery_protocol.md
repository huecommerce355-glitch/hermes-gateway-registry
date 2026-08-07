# Discovery Protocol

`registry.discover` accepts exactly one filter: `domain` or `operation`. It returns matching candidates and does not choose or dispatch work. `--require-health` adds a bounded, read-only probe result (`healthy`, `unhealthy`, or `not_checked`). Deprecated and retired gateways remain visible but are marked and excluded from new-task routing by default.
