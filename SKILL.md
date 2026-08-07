---
name: hermes-gateway-registry
description: Use for registering, discovering, validating, and health-checking Hermes gateways through the HACP metadata registry.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [gateway, registry, HACP, discovery, compatibility]
    related_skills: [coding-agent-gateway, github-development-gateway, obsidian-knowledge-gateway]
---

# Hermes Gateway Registry

## Overview

这是 Hermes 的基础设施层注册中心（metadata layer）。它统一维护 gateway 元数据，提供注册校验、候选发现、协议版本兼容比较和只读健康探测代理；它不负责任务派发或决策。

## When to Use

当需要新增/更新 gateway 注册信息、按 domain 或 operation 发现候选、检查 HACP 兼容性或执行健康探测时使用本 Skill。

不要用于任务派发、路由决策、业务执行、代码提交决策或替代 gateway 的实际操作。

## How to Load

1. 先读取 `registry.yaml` 与 `references/registry_schema.yaml`。
2. 需要协议解析时读取并调用 `scripts/normalize_protocol.py` 的函数。
3. 变更注册表后运行 `python3 scripts/validate_registry.py --input registry.yaml`。
4. 需要候选时运行 `python3 scripts/discover.py --domain <domain>` 或 `--operation <operation>`；只在确有需要时加 `--require-health`。
5. 发现协议、版本或扩展注册规则时，按需读取 `references/` 下对应文档。

## Core Architecture

```text
registry.yaml ──> validate_registry.py ──> JSON validation result
      │
      ├──────────> discover.py ──(optional read-only probe)──> candidate list
      │
      └──────────> normalize_protocol.py ──> HACP name/version comparison
```

## Phase 4.5 修正要点

1. HACP 协议是结构化 `protocol: {name, version}`；字符串只用于展示，解析、校验和比较使用结构化字段。
2. 每个 gateway 必须有非空 `owner.team` 与 `owner.maintainer`。
3. `status` 已替换为 `lifecycle`，值为 `experimental`、`beta`、`stable`、`deprecated` 或 `retired`。deprecated/retired 仍可见，但默认不参与新任务路由。
4. `probe_cmd` 只能是 read-only 探测：不得修改文件、执行远程写操作或包含危险写入命令。探测由 discover 以 15 秒超时执行。

## Error Codes

- `ERR-REG-001`: schema 无效
- `ERR-REG-002`: message/error prefix 冲突
- `ERR-REG-003`: 版本不兼容（跨 major）
- `ERR-REG-004`: probe 不安全
- `ERR-REG-005`: 未找到匹配 gateway

## Common Pitfalls

- 不要把 `HACP/1.0`、`HACP v1.0` 或 `HACP-v1.0` 写回 registry；注册表必须使用结构化字段。
- 不要把 lifecycle 当作任务路由决策；发现结果只列候选，并标记 deprecated/retired。
- prefix 必须全局唯一，避免消息和错误无法归属。
- `probe_cmd` 必须 read-only，只能读取状态或执行无副作用检查；禁止 `git push`、`git commit`、`git add`、`gh pr`、写 API、`rm -rf` 等。
- 健康探测失败不等于 gateway 从注册表消失；结果应保留 gateway 与其 lifecycle，并报告 health。

## Verification Checklist

- [ ] `registry.yaml` 通过 schema、owner、lifecycle、协议和 prefix 校验。
- [ ] probe 命令通过安全子串检查且 timeout 为 15 秒。
- [ ] domain/operation 查询结果只表示候选，不做派发或决策。
- [ ] deprecated/retired 被标记且默认排除新任务路由。
- [ ] 运行 `python3 -m pytest tests/ -v` 并核对真实结果。

## Related Skills

参见 `references/discovery_protocol.md`、`references/version_compat.md`、`references/hacp_register_extension.md`，以及 coding-agent、github-development、obsidian-knowledge gateway skills。
