# Web PC 设计稿保真审查

## Review Contract

```draft-review
review_id: demo-home-v1
source_kind: figma
source_locator: https://www.figma.com/design/target/file?node-id=1-2
source_version: target-v1
access_mode: figma-mcp-read-only
source_limitations: browser-runtime-not-checked
target_role: current-draft-only
version: target-v1
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
expected: headline, navigation, CTA and legal copy match the approved content manifest
observed: all sampled strings match content-manifest-v1.md
test_case: representative content
evidence: manifest:content-manifest-v1; design-context:node-1-2; screenshot:home-default-v1
owner: design-owner
[/check]

[check]
id: content-completeness
category: content
status: pass
expected: every page-manifest section, CTA, state copy and required legal text is present
observed: Home and Inquiry contain every required content item with no empty or omitted block
test_case: page manifest, empty state, error state, legal copy
evidence: content-manifest:content-manifest-v1; screenshot:home-inquiry-complete-v1
owner: design-owner
[/check]

[check]
id: content-consistency
category: content
status: pass
expected: page copy, image role and illustrative data describe the same service
observed: service wording and illustrative labels remain consistent across Home and Inquiry
test_case: representative content, illustrative data
evidence: screenshot:home-inquiry-v1; page-manifest:home
owner: design-owner
[/check]

[check]
id: layout-fit
category: layout
status: pass
expected: sections, cards and CTA keep their intended hierarchy at both desktop viewports
observed: no overlap, collapse or misplaced fixed layer at 1440 and 1280 widths
test_case: 1440x900, 1280x800
evidence: screenshot:home-1440x900; screenshot:home-1280x800
owner: design-owner
[/check]

[check]
id: text-wrap
category: typography
status: pass
expected: longest navigation label, headline and CTA stay within the declared line budget
observed: longest labels wrap only at approved break points and no word is clipped
test_case: longest-label, cjk-latin, large-number
evidence: screenshot:home-longest-label-v1; annotation:wrap-budget-v1
owner: design-owner
[/check]

[check]
id: overflow
category: layout
status: pass
expected: long text, large numbers and failed images do not create horizontal overflow
observed: containers expand or wrap within the page grid; no content is hidden by clipping
test_case: long-content, large-number, asset-failure
evidence: screenshot:home-overflow-v1; annotation:content-resilience-v1
owner: design-owner
[/check]

[check]
id: responsive
category: responsive
status: pass
expected: desktop layout preserves hierarchy across the declared Web PC viewport set
observed: navigation, grid and form controls resize without accidental reordering
test_case: 1440x900, 1280x800
evidence: screenshot:home-1440x900; screenshot:home-1280x800
owner: design-owner
[/check]

[check]
id: asset-source
category: assets
status: pass
expected: every image, font and logo has a source, usage and license boundary
observed: all placed assets resolve to assets-v1.md and no placeholder is presented as final
test_case: representative assets, asset-failure
evidence: asset-registry:assets-v1; screenshot:home-assets-v1
owner: design-owner
[/check]

[check]
id: state-coverage
category: states
status: pass
expected: default, loading, error, success, close and return states are reachable for Inquiry
observed: each declared state has a node and preview path; unimplemented states remain planned
test_case: inquiry-default, inquiry-error, inquiry-success
evidence: state-matrix:inquiry-v1; preview:inquiry-flow-v1
owner: design-owner
[/check]
```
