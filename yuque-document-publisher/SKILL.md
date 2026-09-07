---
name: yuque-document-publisher
description: 用户明确要求把本地 Markdown、PRD、系分或正式文档上传、同步、更新或发布到语雀，且需要处理既有 docRef、Mermaid、本地图片、相对链接、草稿冲突或发布后回读时触发。仅写作或评审文档、只读查看语雀、导出本地文件及其它平台发布不触发。
---

# 语雀文档发布

## 定位

本 Skill 负责把已确认的本地 Markdown 权威版本受控发布为语雀协作副本。它不改写产品、工程或其它领域事实，不把语雀反向升级为源仓权威，也不因“同步”获得删除、权限、Git、Token 或批量发布授权。

本 Skill 当前为候选能力，仅在用户显式调用时使用；准入状态见 `admission.json`。

## 工作流

1. **冻结发布契约**：确认本地源路径、`SourceVersion`、SHA-256、目标知识库、稳定 docRef、新建或更新、图片范围、授权和停止条件。正文语义未确认或目标不唯一时停止。
2. **生成发布投影**：对本地 Markdown 运行 `scripts/prepare_yuque_projection.py`，检查生成的 `projection.md` 与 `manifest.json`。投影只处理来源标记、本地图片和相对链接，不能改写正文事实；`missing_images` 非空时停止发布并先补齐输入。
3. **选择发布表面**：先按当前环境规则查询适用 connector/API；不可用或用户明确要求浏览器时，使用环境可用的 Browser Skill。不得读取 Cookie、Token、密码或会话存储。
4. **核对云端状态**：进入稳定 docRef，比较阅读版、编辑器草稿、本地版本和摘要。存在人工草稿、摘要漂移或目标不明时停止并交文档 Owner。
5. **执行已授权发布**：粘贴投影并完成 Markdown 样式转换；按 manifest 上传仍需的 SVG/图片；确认草稿已保存后再更新。外部传输、覆盖、权限变更和删除分别遵守动作时授权。
6. **回读并记录**：核对来源标记、版本、标题、目录、表格、Mermaid、图片实际加载、内部链接和重复节点，输出成功项、失败项、证据边界和下一 Owner。

详细契约、失败恢复和证据口径读取 `references/markdown-publication-contract.md`。

## 投影脚本

```bash
python3 yuque-document-publisher/scripts/prepare_yuque_projection.py \
  --source /absolute/path/product-design.md \
  --source-version v1.0 \
  --link-map /absolute/path/link-map.json \
  --output-dir /absolute/path/to/temporary-output
```

`--link-map` 可省略。脚本只读取显式输入并写入显式输出目录，不联网、不访问语雀、不读取密钥；生成的投影是临时载体，不回写源文档。

## 输出契约

- 本地源：路径、版本、SHA-256。
- 语雀目标：知识库、稳定 docRef、更新前后版本。
- 发布结果：正文、Mermaid、图片、链接和目录状态。
- 验证证据：阅读页实际结果、检查时间和证据限制。
- 未尽事项：失败原因、未确认前处理、下一 Owner 和最小动作。

## 停止条件

- 本地源、版本、目标知识库或 docRef 无法唯一确认。
- 阅读版与草稿不一致，或发布期间本地摘要变化。
- 需要上传敏感内容、覆盖人工草稿、删除云端对象、改变权限或使用 Token，但缺少对应授权。
- Markdown 转换、图片加载或 Mermaid 渲染失败，且无法保留可读正文和明确残余项。
- 投影 manifest 的 `missing_images` 非空。

## 红线

- 不从语雀阅读页纯文本重建源 Markdown。
- 不把本地相对图片路径当成语雀可访问 URL。
- 不用等价 SVG 重复表达已由 Mermaid 持有的流程事实。
- 不把上传提示、文件名、DOM 节点、截图或 Agent 自述单独当成发布完成。
- 不持久化重导后可能变化的章节 anchor，只记录稳定 docRef。
- 不默认删除旧文档、空分组、附件或历史版本。
