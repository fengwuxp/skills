#!/usr/bin/env python3
"""CR 结论分支的离线回归；无写入、网络或凭据读取。"""

import unittest
from pathlib import Path

from check_architecture_deliverable import missing_groups


class CodeReviewConclusionTests(unittest.TestCase):
    def cleanReview(self):
        path = Path(__file__).resolve().parents[1] / "fixtures/code-review-clean-valid.md"
        return path.read_text(encoding="utf-8")

    def testCleanReviewWithEvidence(self):
        path = Path(__file__).resolve().parents[1] / "fixtures/code-review-clean-valid.md"
        self.assertEqual([], missing_groups("code-review", path.read_text(encoding="utf-8")))

    def testCurrentReportTitleMayContainTemplateOrExample(self):
        body = self.cleanReview().split("\n", 1)[1]
        for title in ("Controller 测试模板 CR", "Java 示例代码评审", "历史记录模块 CR"):
            with self.subTest(title=title):
                self.assertEqual([], missing_groups("code-review", f"# {title}\n{body}"))

    def testCleanClaimWithoutEvidenceIsRejected(self):
        for text in ("", "代码没问题", "结论：未发现需修复的问题。",
                     "结论：未发现需修复的问题。\n范围：\n证据：\n验证：\n风险："):
            with self.subTest(text=text):
                self.assertTrue(missing_groups("code-review", text))

    def testCleanReviewRequiresEachEvidenceField(self):
        path = Path(__file__).resolve().parents[1] / "fixtures/code-review-clean-valid.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        for label in ("范围", "证据", "验证", "风险"):
            with self.subTest(label=label):
                text = "\n".join(line for line in lines if not line.startswith(label + "："))
                self.assertTrue(missing_groups("code-review", text))

    def testUncertainConclusionDoesNotBecomeClean(self):
        text = "尚未发现问题，但尚未完成检查。证据：文件 a.py。风险：未完成。验证：测试未执行。"
        self.assertIn("findings", missing_groups("code-review", text))

    def testFindingStillNeedsSeverity(self):
        text = "发现：a.py:1 吞异常。证据：文件和调用链显示失败丢失。风险：数据错误。建议：传播错误。验证：补回归。"
        self.assertIn("findings", missing_groups("code-review", text))

    def testCleanConclusionCannotHideCurrentFinding(self):
        for finding in ("发现：example.py:12 会丢失错误。", "## 发现\nexample.py:12 会丢失错误。",
                        "- [P2] example.py:12 会丢失错误。", "- 发现：example.py:12 会丢失错误。",
                        "问题 1：example.py:12 会丢失错误。"):
            with self.subTest(finding=finding):
                self.assertTrue(missing_groups("code-review", self.cleanReview() + "\n" + finding))

    def testHistoricalCleanConclusionCannotReplaceCurrentConclusion(self):
        current = self.cleanReview().replace("结论：未发现需修复的问题。", "结论：存在需要修复的问题。")
        for history in ("```text\n结论：未发现需修复的问题。\n```",
                        "~~~text\n结论：未发现需修复的问题。\n~~~",
                        "> 结论：未发现需修复的问题。",
                        "## 历史模板\n结论：未发现需修复的问题。"):
            with self.subTest(history=history):
                self.assertTrue(missing_groups("code-review", current + "\n" + history))

    def testConflictingCurrentConclusionsAreRejected(self):
        self.assertTrue(missing_groups("code-review", self.cleanReview() + "\n结论：存在缺陷。"))

    def testValidCleanReviewMayQuoteOldFinding(self):
        self.assertEqual([], missing_groups("code-review", self.cleanReview() +
                         "\n```text\n发现：[P2] 旧版本失败，已修复。\n```"))


if __name__ == "__main__":
    unittest.main()
