#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "product-architecture-expert" / "scripts" / "check_product_qualification.py"
SPEC = importlib.util.spec_from_file_location("check_product_qualification", CHECKER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load product qualification checker")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


VALID = """# 审核流程产品设计

定性对象：业务流程
本期变化：治理
责任边界：统一审核责任与结果，不设计内部消息和存储机制。
文档强度：标准；依据：涉及审核员、运营和申请状态协作。

## 核心概念与业务口径

| 概念 | 类型 | 本 PRD 中的定义 | 边界 / 不等于 | 状态 | Owner / 权威来源 |
| --- | --- | --- | --- | --- | --- |
| 审核任务 | 业务对象 | 等待审核员裁决的一次申请 | 不等于交易订单 | 当前 | 运营 Owner / 审核术语库 V2 |
"""


class QualificationCheckerTests(unittest.TestCase):
    def test_accepts_qualified_prd_with_concept_projection(self) -> None:
        self.assertEqual([], MODULE.check(VALID))

    def test_requires_qualification_fields(self) -> None:
        issues = MODULE.check(VALID.replace("定性对象：业务流程\n", ""))
        self.assertIn("qualification_object_missing", issues)

    def test_rejects_unknown_qualification_object(self) -> None:
        issues = MODULE.check(VALID.replace("定性对象：业务流程", "定性对象：缓存产品"))
        self.assertIn("qualification_object_invalid", issues)

    def test_rejects_noncanonical_qualification_alias(self) -> None:
        issues = MODULE.check(VALID.replace("定性对象：业务流程", "定性对象：流程"))
        self.assertIn("qualification_object_invalid", issues)

    def test_rejects_conflicting_qualification_values(self) -> None:
        issues = MODULE.check(VALID + "\n定性对象：技术机制\n")
        self.assertIn("qualification_object_conflict", issues)

    def test_rejects_unknown_change_type(self) -> None:
        issues = MODULE.check(VALID.replace("本期变化：治理", "本期变化：平台化"))
        self.assertIn("change_type_invalid", issues)

    def test_rejects_conflicting_change_types(self) -> None:
        issues = MODULE.check(VALID + "\n本期变化：退役\n")
        self.assertIn("change_type_conflict", issues)

    def test_requires_document_strength_rationale(self) -> None:
        issues = MODULE.check(VALID.replace("；依据：涉及审核员、运营和申请状态协作", ""))
        self.assertIn("document_strength_rationale_missing", issues)

    def test_accepts_markdown_labeled_document_strength(self) -> None:
        text = VALID.replace(
            "文档强度：标准；依据：涉及审核员、运营和申请状态协作。",
            "- **文档强度**：标准；依据：涉及审核员、运营和申请状态协作。",
        )
        self.assertEqual([], MODULE.check(text))

    def test_rejects_conflicting_document_strengths(self) -> None:
        issues = MODULE.check(VALID + "\n文档强度：增强；依据：涉及不可逆操作。\n")
        self.assertIn("document_strength_conflict", issues)

    def test_rejects_invalid_concept_status(self) -> None:
        issues = MODULE.check(VALID.replace("| 当前 |", "| 永久 |"))
        self.assertIn("concept_status_invalid", issues)

    def test_requires_concept_authority(self) -> None:
        issues = MODULE.check(VALID.replace("运营 Owner / 审核术语库 V2", "待确认"))
        self.assertIn("concept_authority_missing", issues)


if __name__ == "__main__":
    unittest.main()
