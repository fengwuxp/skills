# 需求验收测试报告

```acceptance-contract
acceptance_id: RAT-DEMO-001
requirement_source: product-spec-v1.md
requirement_version: v1
requirement_fingerprint: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
implementation_target: demo-web
implementation_version: commit-abc123
scope: order submission business result and Web confirmation flow
non_goals: production release approval
environment: local-test
test_data: fixture-order-v1
risk_level: high
requirement_owner: product-owner
acceptance_owner: qa-owner
checker: requirement-acceptance-testing
authorization_boundary: local read and existing test execution only
status: completed
```

```acceptance-criteria
[criterion]
id: AC-001
requirement_anchor: product-spec-v1.md#submit-order
verification_kind: business-logic
required: true
preconditions: valid customer and in-stock item
action: submit one order
expected: order becomes submitted exactly once
unacceptable: duplicate order or success without persisted state
owner: engineering-owner
outcome: pass
evidence_refs: EV-001
finding_id: none
retest_scope: order submission service
rationale: automated application-service evidence
[/criterion]

[criterion]
id: AC-002
requirement_anchor: product-spec-v1.md#confirmation-flow
verification_kind: ui-interaction
required: true
preconditions: order form is ready
action: submit the form from the browser
expected: confirmation is visible and duplicate submit is disabled
unacceptable: dead control, missing feedback or duplicate submit
owner: ui-owner
outcome: pass
evidence_refs: EV-002
finding_id: none
retest_scope: submit and confirmation interaction
rationale: browser interaction evidence
[/criterion]

[criterion]
id: AC-003
requirement_anchor: approved-design-v1#confirmation
verification_kind: visual-fidelity
required: true
preconditions: approved design and browser implementation use the same content
action: compare the rendered confirmation with the approved design
expected: layout, typography, assets and text wrapping match the approved contract
unacceptable: clipped text, missing asset or unapproved visual deviation
owner: design-owner
outcome: pass
evidence_refs: EV-003, EV-004, EV-005
finding_id: none
retest_scope: confirmation view at declared viewport
rationale: design source, runtime screenshot and human visual review
[/criterion]
```

```acceptance-evidence
[evidence]
id: EV-001
criterion_ids: AC-001
evidence_type: test-report
source: reports/order-submission.xml
source_fingerprint: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
environment: local-test
command_or_method: targeted application-service test
result: pass
captured_at: 2026-08-22T12:00:00+08:00
producer: engineering-maker
independent_reviewer: acceptance-checker
limitations: external payment not in scope
[/evidence]

[evidence]
id: EV-002
criterion_ids: AC-002
evidence_type: browser-trace
source: artifacts/order-confirmation-trace.zip
source_fingerprint: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
environment: chromium-local
command_or_method: Playwright submit and state assertion
result: pass
captured_at: 2026-08-22T12:05:00+08:00
producer: ui-maker
independent_reviewer: acceptance-checker
limitations: Chromium only
[/evidence]

[evidence]
id: EV-003
criterion_ids: AC-003
evidence_type: design-context
source: approved-design-v1#confirmation
source_fingerprint: dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
environment: design-source
command_or_method: exact design node readback
result: pass
captured_at: 2026-08-22T12:10:00+08:00
producer: design-owner
independent_reviewer: acceptance-checker
limitations: static design evidence
[/evidence]

[evidence]
id: EV-004
criterion_ids: AC-003
evidence_type: runtime-screenshot
source: artifacts/order-confirmation-1440.png
source_fingerprint: eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
environment: chromium-1440x900
command_or_method: browser screenshot
result: pass
captured_at: 2026-08-22T12:12:00+08:00
producer: ui-maker
independent_reviewer: acceptance-checker
limitations: one declared viewport
[/evidence]

[evidence]
id: EV-005
criterion_ids: AC-003
evidence_type: visual-review
source: review/order-confirmation-v1.md
source_fingerprint: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
environment: design-review
command_or_method: independent comparison of design and runtime evidence
result: pass
captured_at: 2026-08-22T12:15:00+08:00
producer: design-checker
independent_reviewer: acceptance-checker
limitations: no target-user evidence
[/evidence]
```

```acceptance-verdict
verdict: pass
summary: all required acceptance criteria passed with traceable evidence
required_total: 3
pass_count: 3
fail_count: 0
blocked_count: 0
cant_tell_count: 0
untested_count: 0
not_applicable_count: 0
residual_risks: production release and external payment remain outside scope
next_owner: release-owner
```
