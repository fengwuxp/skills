# 截图来源错误升级证据等级

```draft-review
review_id: screenshot-e2-invalid
source_kind: screenshot
source_locator: file:home.png#sha256=demo
source_version: export-v1
access_mode: local-file
source_limitations: static-image-only
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
observed: screenshot text appears consistent
test_case: representative content
evidence: content-manifest:content-manifest-v1; screenshot:home
owner: design-owner
[/check]
```
