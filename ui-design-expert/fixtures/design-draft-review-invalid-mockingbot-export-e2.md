# 墨刀导出物错误升级证据等级

```draft-review
review_id: mockingbot-export-e2-invalid
source_kind: mockingbot
source_locator: file:mockingbot-export.zip#sha256=demo
source_version: export-v1
access_mode: mockingbot-export
source_limitations: no-preview-or-annotation
target_role: current-draft-only
version: review-v1
source_of_truth: approved-brief-v1.md
content_manifest: content-manifest-v1.md
asset_registry: assets-v1.md
viewport_set: web-pc-v1
viewports: 1440x900, 1280x800
evidence_level: E2
reviewer: design-owner
status: ready-for-review
```

```draft-checks
[check]
id: content-source
category: content
status: pass
expected: approved content
observed: exported text appears consistent
test_case: representative content
evidence: content-manifest:content-manifest-v1; screenshot:mockingbot-export
owner: design-owner
[/check]
```
