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

| 概念 | 类型 | 统一定义 | 边界 / 不等于 |
| --- | --- | --- | --- |
| 审核任务 | 业务对象 | 等待审核员裁决的一次申请 | 不等于交易订单 |
"""


class QualificationCheckerTests(unittest.TestCase):
    def test_noun_phrase_definitions_keep_boundary_separate(self) -> None:
        definitions = (
            "将已授权请求转换为可回查结果的产品",
            "在明确范围下的一份不可变内容版本",
            "面向明确用户的一次审核记录",
            "审核记录下的一次处理结果",
            "目标用户显式操作形成的确认事实",
            "引导使用方查询进度的短时信号",
            "安全能力为特定用途签发并一次消费的证明",
        )
        prefix = VALID.split("## 核心概念与业务口径")[0] + "## 核心概念与业务口径\n\n"
        for definition in definitions:
            with self.subTest(definition=definition):
                record = "**审核概念**：" + definition + "。不等于业务结果。\n"
                self.assertEqual([], MODULE.check(prefix + record))
                self.assertIn("concept_definition_missing", MODULE.check(prefix + record.replace(definition + "。", "")))
                self.assertIn("concept_boundary_missing", MODULE.check(prefix + record.replace("不等于业务结果。", "")))

    def test_concept_paragraphs_keep_definition_and_boundary_local(self) -> None:
        intro = VALID.split("## 核心概念与业务口径")[0]
        records = (
            "**审核任务**：一项等待审核员裁决的申请。只记录本次审核，不等于交易订单。",
            "**生效范围**：内容适用于指定团队。查询和修改都必须明确该范围。",
        )
        section = "## 核心概念与业务口径\n\n"
        self.assertEqual([], MODULE.check(intro + section + "\n\n".join(records)))
        for record in records:
            definition, boundary = record.split("。", 1)
            for fragment, expected in (
                (definition + "。", "concept_boundary_missing"),
                (record.split("：", 1)[0] + "：" + boundary, "concept_definition_missing"),
            ):
                with self.subTest(record=record, fragment=fragment):
                    text = intro + section + "\n\n".join(
                        fragment if candidate == record else candidate for candidate in records
                    ) + "\n\n## 其他章节\n" + record
                    self.assertIn(expected, MODULE.check(text))

    def test_mixed_concept_table_cannot_hide_incomplete_paragraph(self) -> None:
        text = VALID + "\n**风险判断**：一项审核结果。\n"
        self.assertIn("concept_boundary_missing", MODULE.check(text))

    def test_concept_paragraph_cannot_hide_broken_table(self) -> None:
        paragraph = "\n**发布记录**：一项已发布的内容版本。不能覆盖历史。\n"
        broken = VALID.replace("| 统一定义 |", "| 备注 |")
        self.assertIn("concept_definition_table_incomplete", MODULE.check(broken + paragraph))
        self.assertIn("concept_definition_table_incomplete", MODULE.check(VALID + "\n" + broken.split("## 核心概念与业务口径")[1]))

    def test_concept_prose_requires_explicit_manual_review_if_unrecognized(self) -> None:
        text = VALID.split("| 概念 |")[0] + "概念需要更好的管理。\n"
        self.assertIn("concept_expression_manual_review_required", MODULE.check(text))

    def test_accepts_qualified_prd_with_unified_concept_definition(self) -> None:
        self.assertEqual([], MODULE.check(VALID))

    def test_rejects_project_qualified_unified_definition_header(self) -> None:
        text = VALID.replace("| 统一定义 |", "| Acme 4.0 统一定义 |")
        self.assertIn("concept_definition_table_incomplete", MODULE.check(text))

    def test_accepts_legacy_six_column_concept_table(self) -> None:
        text = VALID.replace(
            "| 概念 | 类型 | 统一定义 | 边界 / 不等于 |\n"
            "| --- | --- | --- | --- |\n"
            "| 审核任务 | 业务对象 | 等待审核员裁决的一次申请 | 不等于交易订单 |",
            "| 概念 | 类型 | 本 PRD 中的定义 | 边界 / 不等于 | 状态 | Owner / 权威来源 |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| 审核任务 | 业务对象 | 等待审核员裁决的一次申请 | 不等于交易订单 | 当前 | 运营 Owner / 审核术语库 V2 |",
        )
        self.assertEqual([], MODULE.check(text))

    def test_rejects_missing_unified_definition_column(self) -> None:
        issues = MODULE.check(VALID.replace("| 统一定义 |", "| 局部说明 |"))
        self.assertIn("concept_definition_table_incomplete", issues)

    def test_rejects_negated_unified_definition_column(self) -> None:
        issues = MODULE.check(VALID.replace("| 统一定义 |", "| 非统一定义 |"))
        self.assertIn("concept_definition_table_incomplete", issues)

    def test_rejects_missing_concept_boundary_column(self) -> None:
        issues = MODULE.check(VALID.replace("| 边界 / 不等于 |", "| 备注 |"))
        self.assertIn("concept_definition_table_incomplete", issues)

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

if __name__ == "__main__":
    unittest.main()
