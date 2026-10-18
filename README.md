# x4-mcp-gateway

**Policy-controlled MCP gateway and registry**

Authentication • Authorization • Schema validation • Rate limiting • Approval gates • Audit

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-v0.1-orange)](CHANGELOG.md)

Part of **[ARIEX4Ops / X4](https://github.com/dhe-cruzer69)**.

---

## Thesis

A secure MCP gateway is not just a proxy. It is a control plane.

```
MCP Client
    ↓
Authentication
    ↓
Server Registry + Tool Discovery
    ↓
Schema Validation
    ↓
Policy Engine + Risk Engine
    ├─ DENY
    ├─ ALLOW
    └─ REQUIRE HUMAN APPROVAL
    ↓
Tool Invocation → Result Filter → Audit Log
```

<!-- X4-APEX-DIAGRAM-START:x4-mcp-gateway -->

```mermaid
sequenceDiagram
    autonumber
    participant C as MCP Client
    participant R as Registry and Discovery
    participant A as Authentication
    participant S as Schema Validator
    participant P as Policy and Risk Engine
    participant H as Human Approval
    participant T as Backend Tool
    participant L as Audit Log
    C->>R: Discover configured tools
    C->>A: Request tool invocation
    A-->>S: Identity and scope
    S->>S: Validate request schema
    S->>P: Validated request
    P-->>L: Record decision
    alt denied
        P-->>C: Deny
    else approval required
        P->>H: Request approval
        H-->>P: Decision
    end
    P->>T: Invoke only if allowed
    T-->>C: Filtered result
    T-->>L: Invocation evidence
```

<!-- X4-APEX-DIAGRAM-END:x4-mcp-gateway -->

## Example policy

```yaml
policy:
  name: production-github
rules:
  - tool: github.delete_repository
    action: deny
  - tool: github.create_issue
    action: allow
  - tool: github.merge_pull_request
    action: approval_required
```

Full architecture in [ARCHITECTURE.md](ARCHITECTURE.md).

## Related

- [x4-agents](https://github.com/dhe-cruzer69/x4-agents)
- [x4-sandbox](https://github.com/dhe-cruzer69/x4-sandbox)
- [x4-core](https://github.com/dhe-cruzer69/x4-core)

## License

Apache-2.0

## Security

See [SECURITY.md](SECURITY.md).

## Support

**[GitHub Sponsors](https://github.com/sponsors/dhe-cruzer69)**

## APEX Architecture Map

> Status: architecture documentation; implementation and deployment claims require independent verification.

**Evidence note:** Transport support, authentication, scope enforcement, argument validation, and audit behavior must be confirmed from the actual gateway implementation.

