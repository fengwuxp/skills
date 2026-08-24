# Invalid Design-Code Reconciliation Conflict Example

合成场景：Figma 与代码分别被不同人员修改，但没有 Owner 指定权威。

~~~design-code-reconciliation
reconciliation_id: DCR-INVALID-001
page_id: about
section_role: explain company identity
authoritative_surface: unresolved
sync_mode: reconcile-only
figma_file: synthetic-design-file
figma_node: 202:18
figma_revision: design-version-11
code_file: src/app/about/page.tsx
code_anchor: about-hero-section
code_revision: commit-example-29
content_fingerprint: divergent-content
geometry_fingerprint: divergent-geometry
pending_target: figma, code
write_authorization: none
verification_evidence: diff-only
status: conflict
owner: owner-required
~~~

失败原因：

- authoritative_surface 未裁决。
- 两端同时存在独立变化。
- 没有任何写入授权。
- diff-only 不能证明视觉、交互或双端一致。

停止条件：不得覆盖任一端；必须先由 Owner 裁决每项 delta。
