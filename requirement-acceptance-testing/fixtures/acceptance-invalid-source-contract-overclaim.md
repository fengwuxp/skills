# 源码契约冒充视觉证据的错误验收报告

```acceptance-contract
acceptance_id: RAT-INVALID-SOURCE-VISUAL-001
requirement_source: approved-ui-contract-v1.md
requirement_version: v1
requirement_fingerprint: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
implementation_target: example-marketing-page
implementation_version: commit-example-12
scope: visual fidelity at desktop and mobile viewports
non_goals: production release
environment: local
test_data: synthetic page content
risk_level: medium
requirement_owner: ui-owner
acceptance_owner: qa-owner
checker: acceptance-checker
authorization_boundary: read-only
status: completed
```

```acceptance-criteria
[criterion]
id: AC-VIS-001
requirement_anchor: approved-ui-contract-v1.md#responsive-visuals
verification_kind: visual-fidelity
required: true
preconditions: source contract test completed
action: inspect source-level regex contract result
expected: match design at desktop and mobile without clipping or overlap
unacceptable: missing design context, runtime screenshot or independent visual review
owner: ui-owner
outcome: pass
evidence_refs: EV-SOURCE-001
finding_id: none
retest_scope: desktop and mobile visual fidelity
rationale: incorrectly treats source-level structure as visual runtime evidence
[/criterion]
```

```acceptance-evidence
[evidence]
id: EV-SOURCE-001
criterion_ids: AC-VIS-001
evidence_type: test-report
source: source-contract-test.txt
source_fingerprint: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
environment: local
command_or_method: regex assertions over JSX section and breakpoint tokens
result: pass
captured_at: 2026-08-24T12:00:00+08:00
producer: engineering-maker
independent_reviewer: acceptance-checker
limitations: no design context, browser layout, font rendering, runtime screenshot or visual review
[/evidence]
```

```acceptance-verdict
verdict: pass
summary: invalid because source-level contracts cannot independently prove visual fidelity
required_total: 1
pass_count: 1
fail_count: 0
blocked_count: 0
cant_tell_count: 0
untested_count: 0
not_applicable_count: 0
residual_risks: responsive layout and visual fidelity untested
next_owner: ui-owner
```
