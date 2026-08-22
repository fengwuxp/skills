# 墨刀 Web PC 设计稿保真审查

## Review Contract

```draft-review
review_id: mockingbot-home-v1
source_kind: mockingbot
source_locator: https://modao.cc/proto/example
source_version: share-v3
access_mode: mockingbot-preview-annotation
source_limitations: hidden-pages-not-reviewed
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

## Review Checks

```draft-checks
[check]
id: content-source
category: content
status: pass
expected: visible page copy matches the approved manifest
observed: sampled headings, navigation and CTA match the approved brief
test_case: representative content
evidence: content-manifest:content-manifest-v1; mockingbot-page-inventory:home-inquiry; annotation:home-default; screenshot:home-default-v1
owner: design-owner
[/check]

[check]
id: content-completeness
category: content
status: pass
expected: every shared page and declared state has visible content
observed: all pages included by the share settings contain the required sections and state copy
test_case: page manifest, empty state, error state
evidence: content-manifest:content-manifest-v1; mockingbot-page-inventory:home-inquiry
owner: design-owner
[/check]

[check]
id: content-consistency
category: content
status: pass
expected: navigation, CTA and terminology remain consistent across shared pages
observed: shared Home and Inquiry use the same approved terms and contact action
test_case: representative content
evidence: content-manifest:content-manifest-v1; screenshot:home-inquiry-v1
owner: design-owner
[/check]

[check]
id: layout-fit
category: layout
status: pass
expected: visible sections and CTA keep their hierarchy at both desktop viewports
observed: no overlap or clipping was observed in the two captured viewport states
test_case: 1440x900, 1280x800
evidence: screenshot:mockingbot-home-1440x900; screenshot:mockingbot-home-1280x800
owner: design-owner
[/check]

[check]
id: text-wrap
category: typography
status: pass
expected: longest labels stay within the declared line budget
observed: the longest navigation label and CTA wrap only at approved points
test_case: longest-label, cjk-latin, long-content
evidence: annotation:mockingbot-wrap-budget; screenshot:mockingbot-longest-label
owner: design-owner
[/check]

[check]
id: overflow
category: layout
status: pass
expected: long text and failed images do not hide content
observed: annotated containers keep all visible content inside the page bounds
test_case: long-content, asset-failure
evidence: annotation:mockingbot-container-bounds; screenshot:mockingbot-overflow
owner: design-owner
[/check]

[check]
id: responsive
category: responsive
status: pass
expected: the shared Web PC layout preserves hierarchy at both declared widths
observed: navigation, content grid and form controls remain in the intended order
test_case: 1440x900, 1280x800
evidence: screenshot:mockingbot-home-1440x900; screenshot:mockingbot-home-1280x800
owner: design-owner
[/check]

[check]
id: asset-source
category: assets
status: pass
expected: visible images, fonts and downloadable assets have source records
observed: all visible assets resolve to the approved registry; hidden pages remain excluded
test_case: representative assets, asset-failure
evidence: asset-registry:assets-v1; annotation:mockingbot-assets
owner: design-owner
[/check]

[check]
id: state-coverage
category: states
status: pass
expected: shared default, validation, success, close and return paths are walkable
observed: every declared shared state has a preview path; hidden pages remain unverified
test_case: inquiry-default, inquiry-error, inquiry-success
evidence: preview:mockingbot-inquiry-flow; mockingbot-page-inventory:home-inquiry
owner: design-owner
[/check]
```
