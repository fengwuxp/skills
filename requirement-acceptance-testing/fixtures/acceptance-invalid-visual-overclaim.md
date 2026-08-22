# 截图冒充 UI 交互的错误验收报告

```acceptance-contract
acceptance_id: RAT-INVALID-002
requirement_source: product-spec-v1.md
requirement_version: v1
requirement_fingerprint: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
implementation_target: demo-web
implementation_version: v1
scope: submit interaction
non_goals: release
environment: local
test_data: fixture
risk_level: medium
requirement_owner: product-owner
acceptance_owner: qa-owner
checker: checker
authorization_boundary: read-only
status: completed
```

```acceptance-criteria
[criterion]
id: AC-UI-001
requirement_anchor: product-spec-v1.md#submit
verification_kind: ui-interaction
required: true
preconditions: form visible
action: submit form
expected: confirmation and disabled duplicate submit
unacceptable: dead control or duplicate submit
owner: ui-owner
outcome: pass
evidence_refs: EV-UI-001
finding_id: none
retest_scope: form interaction
rationale: incorrectly relies on a screenshot
[/criterion]
```

```acceptance-evidence
[evidence]
id: EV-UI-001
criterion_ids: AC-UI-001
evidence_type: runtime-screenshot
source: screenshot.png
source_fingerprint: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
environment: chromium
command_or_method: screenshot only
result: pass
captured_at: 2026-08-22T12:00:00+08:00
producer: maker
independent_reviewer: checker
limitations: no interaction evidence
[/evidence]
```

```acceptance-verdict
verdict: pass
summary: invalid because screenshot cannot prove interaction
required_total: 1
pass_count: 1
fail_count: 0
blocked_count: 0
cant_tell_count: 0
untested_count: 0
not_applicable_count: 0
residual_risks: interaction untested
next_owner: ui-owner
```
