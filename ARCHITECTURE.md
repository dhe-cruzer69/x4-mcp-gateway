# x4-mcp-gateway Architecture

## Thesis

A policy-controlled MCP gateway, not merely a proxy.

## Request path

```
MCP Client
    ↓
Authentication
    ↓
Server Registry / Tool Discovery
    ↓
Schema Validation
    ↓
Policy Engine + Risk Engine
    ├─ DENY
    ├─ ALLOW
    └─ REQUIRE HUMAN APPROVAL
    ↓
Tool Invocation
    ↓
Result Filter
    ↓
Audit Log
```

## Example policy fragment

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

## Differentiation

Authentication, authorization, schema validation, rate limiting, approval gates, and immutable audit trails are first-class.
