# Figma Design Plan

## Design Contract

```design-contract
project_id: demo-site
client_scope: web-pc
change_mode: visual-adjustment-with-bounded-content-optimization
product_source: product-source-v1.md
brief_source: approved-brief-v1.md
reference_figma: https://www.figma.com/design/reference/file?node-id=1-2
target_figma: https://www.figma.com/design/target/file?node-id=1-2
target_role: current-draft-only
terminology_source: terminology-v1.md
asset_registry: assets-v1.md
brand_boundary: brand-boundary-v1.md
owner: design-owner
status: ready-for-figma
```

## Page Manifest

```page-manifest
[page]
id: home
route: /
display_name: Home
figma_name: Web PC / 10 Home / default / 1440 / Draft
purpose: explain-positioning
source_node: https://www.figma.com/design/reference/file?node-id=1-2
states: default, inquiry-open, inquiry-validation, inquiry-success, inquiry-close, inquiry-return
state_exclusions: loading, empty, permission
state_notes: inquiry paths are validated in the same prototype
content_source: brief:home
nav_label: Home
client_scope: web-pc
status: draft
is_current: true
[/page]

[page]
id: advertising-services
route: /advertising-services
display_name: Advertising Services
figma_name: Web PC / 11 Advertising Services / default / 1440 / Draft
purpose: explain-service-scope
source_node: https://www.figma.com/design/reference/file?node-id=1-3
states: default, inquiry-open, inquiry-error, inquiry-success, inquiry-close, inquiry-return
state_exclusions: loading, empty, permission
state_notes: inquiry opens from the page CTA and returns to the page
content_source: brief:advertising-services
nav_label: Advertising Services
client_scope: web-pc
status: draft
is_current: true
[/page]

[page]
id: about
route: /about
display_name: About
figma_name: Web PC / 12 About / default / 1440 / Draft
purpose: explain-company-role
source_node: https://www.figma.com/design/reference/file?node-id=1-4
states: default, inquiry-open, inquiry-error, inquiry-success, inquiry-close, inquiry-return
state_exclusions: loading, empty, permission
state_notes: page CTA opens the shared inquiry panel
content_source: brief:about
nav_label: About
client_scope: web-pc
status: draft
is_current: true
[/page]
```

## Navigation Map

```navigation-map
[item]
page_id: home
route: /
label: Home
[/item]
[item]
page_id: advertising-services
route: /advertising-services
label: Advertising Services
[/item]
[item]
page_id: about
route: /about
label: About
[/item]
```

## Figma Evidence

```figma-evidence
components: status=planned; evidence=component-contract-v1
variables: status=planned; evidence=token-contract-v1
auto_layout: status=planned; evidence=layout-contract-v1
annotations: status=planned; evidence=interaction-contract-v1
dev_resources: status=planned; evidence=handoff-contract-v1
code_connect: status=planned; evidence=not-required-before-code-handoff
component_playground: status=planned; evidence=component-contract-v1
ready_for_dev: status=planned; evidence=handoff-contract-v1
state_matrix: status=planned; evidence=state-matrix-v1
```
