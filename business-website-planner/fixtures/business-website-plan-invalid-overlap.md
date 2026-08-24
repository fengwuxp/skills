# Invalid Cross-Page Overlap Contract

```business-website-plan
plan_id: BWP-INVALID-OVERLAP
business_authority: owner-approved-software-brief.md
business_type: software-services
company_subject: Example Software Services Limited
target_customers: B2B operations teams
business_scope: implementation planning and managed support
non_goals: product checkout or production release
organization_mode: core-plus-conditional
reference_mode: none
design_carrier: figma
design_carrier_override: none
owner: business-owner
status: ready-for-ui
```

```website-modules
[module]
id: home-process
kind: suggested
role: explain the complete implementation process
required: true
placement: homepage
evidence: owner-approved-software-brief.md#process
owner: business-owner
page_role: home
primary_question: How does the implementation process work
client_value: understand every implementation stage
content_depth: detailed
handoff_to: services-process
overlap_with: none
overlap_disposition: none
[/module]

[module]
id: services-process
kind: suggested
role: repeat the complete implementation process
required: true
placement: services page
evidence: owner-approved-software-brief.md#process
owner: service-owner
page_role: services
primary_question: How does the implementation process work
client_value: understand every implementation stage
content_depth: detailed
handoff_to: none
overlap_with: none
overlap_disposition: none
[/module]
```

```metric-suggestions
[metric]
name: Implementations supported
business_meaning: Shows confirmed delivery experience
reference_example_value: 20+
owner_confirmed_value: none
publish: false
[/metric]
```

```reference-dna
```

```responsive-media
[media]
id: implementation-workshop
role: decorative collaboration image
source: owner-approved-assets/workshop.jpg
focal_point: team at center
text_safe_area: left area
crop_variants: landscape and portrait
target_viewports: mobile-390, desktop-1440, ultrawide-2560
owner: ui-owner
[/media]
```

```website-handoff
ui_owner: ui-design-expert
design_carrier: figma
figma_write_authorization: required
engineering_owner: senior-software-architect
acceptance_owner: requirement-acceptance-testing
legal_data_conditions: inquiry fields require confirmation
stop_conditions: stop when page roles remain duplicated
```
