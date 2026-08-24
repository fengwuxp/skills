# Valid Design-Code Reconciliation Example

合成场景：Example Orbit 的服务页文案先在 Figma 获批，再同步到 React 页面。

~~~design-code-reconciliation
reconciliation_id: DCR-VALID-001
page_id: services
section_role: explain service scope and client responsibilities
authoritative_surface: figma
sync_mode: design-first
figma_file: synthetic-design-file
figma_node: 101:24
figma_revision: design-version-7
code_file: src/app/services/page.tsx
code_anchor: services-scope-section
code_revision: commit-example-17
content_fingerprint: content-sha256-example-7
geometry_fingerprint: geometry-sha256-example-3
pending_target: none
write_authorization: figma-and-code-approved
verification_evidence: figma-readback, source-contract, runtime-screenshot
status: aligned
owner: ui-owner
~~~

验收说明：

- 只同步 copy，未改变 geometry、asset 或 interaction。
- Figma 与代码均已回读。
- 运行截图只证明已声明视口，不外推生产或目标用户效果。
