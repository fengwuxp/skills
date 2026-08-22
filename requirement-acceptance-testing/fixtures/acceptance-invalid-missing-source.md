# 缺需求权威的错误验收报告

```acceptance-contract
acceptance_id: RAT-INVALID-001
requirement_source:
requirement_version: v1
requirement_fingerprint: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
implementation_target: demo
implementation_version: v1
scope: one rule
non_goals: release
environment: local
test_data: fixture
risk_level: low
requirement_owner: product-owner
acceptance_owner: qa-owner
checker: checker
authorization_boundary: read-only
status: completed
```

```acceptance-criteria
[criterion]
id: AC-001
requirement_anchor: missing#rule
verification_kind: business-logic
required: true
preconditions: ready
action: execute
expected: result
unacceptable: wrong result
owner: owner
outcome: pass
evidence_refs: EV-001
finding_id: none
retest_scope: rule
rationale: sample
[/criterion]
```

```acceptance-evidence
[evidence]
id: EV-001
criterion_ids: AC-001
evidence_type: test-report
source: report.xml
source_fingerprint: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
environment: local
command_or_method: test
result: pass
captured_at: 2026-08-22T12:00:00+08:00
producer: maker
independent_reviewer: checker
limitations: none observed
[/evidence]
```

```acceptance-verdict
verdict: pass
summary: invalid because requirement source is missing
required_total: 1
pass_count: 1
fail_count: 0
blocked_count: 0
cant_tell_count: 0
untested_count: 0
not_applicable_count: 0
residual_risks: none
next_owner: none
```
