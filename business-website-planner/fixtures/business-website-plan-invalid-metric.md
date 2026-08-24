# Invalid Metric Contract

```business-website-plan
plan_id: BWP-INVALID-METRIC
business_authority: owner-approved-sourcing-brief.md
business_type: sourcing-services
company_subject: Example Sourcing Limited
target_customers: overseas buyers
business_scope: supplier sourcing and quality coordination
non_goals: customs or legal advice
organization_mode: single-page
reference_mode: public
design_carrier: figma
design_carrier_override: none
owner: business-owner
status: ready-for-ui
```

```website-modules
[module]
id: sourcing-scope
kind: suggested
role: explain supplier sourcing and quality checks
required: true
placement: homepage section
evidence: owner-approved-sourcing-brief.md#scope
owner: sourcing-owner
page_role: home
primary_question: What sourcing support is available
client_value: understand the sourcing scope
content_depth: summary
handoff_to: none
overlap_with: none
overlap_disposition: none
[/module]
```

```metric-suggestions
[metric]
name: Verified suppliers
business_meaning: Shows supplier network depth
reference_example_value: 200+
owner_confirmed_value: none
publish: true
[/metric]
```

```reference-dna
[reference]
source: https://www.foreigngo.com/
read_status: body-read
adopt: visible sourcing workflow and inspection evidence
reject: company metrics, wording, images and page layout
limitations: source claims are not evidence for the target company
[/reference]
```

```responsive-media
[media]
id: inspection-proof
role: semantic inspection image
source: owner-approved-asset-library/inspection.jpg
focal_point: inspected product and visible checklist
text_safe_area: none
crop_variants: contain without cropping
target_viewports: mobile-390, desktop-1440, ultrawide-2560
owner: quality-owner
[/media]
```

```website-handoff
ui_owner: ui-design-expert
design_carrier: figma
figma_write_authorization: required before file mutation
engineering_owner: senior-software-architect
acceptance_owner: requirement-acceptance-testing
legal_data_conditions: inquiry data fields require Owner confirmation
stop_conditions: stop when supplier metrics or asset rights are unresolved
```
