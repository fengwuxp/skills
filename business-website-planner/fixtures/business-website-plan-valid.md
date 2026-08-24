# Business Website Contract

```business-website-plan
plan_id: BWP-DEMO-001
business_authority: owner-approved-business-brief-v1.md
business_type: advertising-services
company_subject: Example Advertising Services Limited
target_customers: B2B marketing teams
business_scope: campaign planning and coordination
non_goals: media budget custody, direct ad account operation, production release
organization_mode: core-plus-conditional
reference_mode: public
design_carrier: figma
design_carrier_override: none
owner: business-owner
status: ready-for-ui
```

```website-modules
[module]
id: positioning
kind: suggested
role: explain the literal business category and target customers
required: true
placement: homepage hero or opening section
evidence: owner-approved-business-brief-v1.md#positioning
owner: business-owner
page_role: home
primary_question: What business does the company provide and for whom
client_value: understand the business category and relevance
content_depth: summary
handoff_to: services
overlap_with: none
overlap_disposition: none
[/module]

[module]
id: services
kind: suggested
role: explain service scope, client control and documented outputs
required: true
placement: homepage section or separate business page
evidence: owner-approved-business-brief-v1.md#scope
owner: service-owner
page_role: services
primary_question: What support is included and how responsibilities are divided
client_value: evaluate service fit and delivery boundaries
content_depth: detailed
handoff_to: inquiry
overlap_with: none
overlap_disposition: none
[/module]

[module]
id: inquiry
kind: conditional
role: explain the real contact path and next response
required: false
placement: page-end section or contact page
evidence: inquiry-data-brief-v1.md
owner: operations-owner
page_role: shared
primary_question: How can an interested client start a conversation
client_value: know the next contact step
content_depth: decision-support
handoff_to: none
overlap_with: positioning, services
overlap_disposition: keep-shared
[/module]
```

```metric-suggestions
[metric]
name: Advertising engagements
business_meaning: Shows operating experience across approved client work
reference_example_value: 50+
owner_confirmed_value: 80+
publish: true
[/metric]

[metric]
name: Advertising service areas
business_meaning: Shows the documented breadth of the service scope
reference_example_value: 5+
owner_confirmed_value: 10+
publish: true
[/metric]

[metric]
name: Client industry categories
business_meaning: Suggests an optional breadth indicator for Owner review
reference_example_value: 12+
owner_confirmed_value: none
publish: false
[/metric]
```

```reference-dna
[reference]
source: https://ebiquity.com/digital-media-governance-digital-media-auditing/
read_status: body-read
adopt: service scope, accountability and evidence-led case structure
reject: client logos, published metrics, page composition and visual identity
limitations: enterprise-scale claims do not transfer to the target company
[/reference]
```

```responsive-media
[media]
id: hero-collaboration
role: decorative business-context image
source: owner-approved-asset-library/team-collaboration.jpg
focal_point: people reviewing campaign materials at the center-right
text_safe_area: left 42 percent remains free of faces and documents
crop_variants: landscape desktop, ultrawide landscape, mobile portrait
target_viewports: mobile-390, desktop-1440, desktop-1920, ultrawide-2560, ultrawide-3440
owner: ui-owner
[/media]

[media]
id: service-output-example
role: semantic image showing a documented campaign output
source: owner-approved-asset-library/redacted-review-summary.png
focal_point: full document content
text_safe_area: none; do not overlay text
crop_variants: contain without cropping
target_viewports: mobile-390, desktop-1440
owner: content-owner
[/media]
```

```website-handoff
ui_owner: ui-design-expert
design_carrier: figma
figma_write_authorization: required before file mutation
engineering_owner: senior-software-architect
acceptance_owner: requirement-acceptance-testing
legal_data_conditions: inquiry collection requires confirmed data fields and privacy notice
stop_conditions: stop when business facts, confirmed metrics, asset rights or data behavior are unresolved
```
