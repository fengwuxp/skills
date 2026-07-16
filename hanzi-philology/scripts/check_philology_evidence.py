#!/usr/bin/env python3
"""Check structural completeness and single-source overreach in evidence cards.

The checker is offline and read-only. It does not determine whether a glyph,
reading, reconstruction, or interpretation is philologically correct.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class RequiredGroup(NamedTuple):
    name: str
    aliases: tuple[str, ...]
    min_hits: int = 1


CHECKS: dict[str, tuple[RequiredGroup, ...]] = {
    "character-form": (
        RequiredGroup("object_and_layer", ("研究对象", "研究對象", "所问层次", "所問層次", "字形"), 2),
        RequiredGroup("excavated_material", ("出土材料", "甲骨", "金文", "简帛", "簡帛")),
        RequiredGroup("provenance_and_date", ("合集号", "合集號", "器号", "器號", "图版", "圖版", "出处", "出處", "时代", "時代", "年代"), 2),
        RequiredGroup("form_and_usage", ("构形", "構形", "辞例", "辭例", "用例", "语境", "語境"), 2),
        RequiredGroup("traditional_and_modern", ("传统训释", "傳統訓釋", "说文", "說文", "尔雅", "爾雅", "现代研究", "現代研究", "学者", "學者"), 2),
        RequiredGroup("conflict_and_status", ("支持", "反证", "反證", "争议", "爭議", "冲突", "衝突", "结论等级", "結論等級", "材料可证", "材料可證", "待考"), 2),
    ),
    "exegesis": (
        RequiredGroup("passage_and_edition", ("原文", "上下文", "篇章", "底本", "版本", "异文", "異文"), 3),
        RequiredGroup("textual_usage", ("传世文献", "傳世文獻", "同时代", "同時代", "平行用例", "语境", "語境"), 2),
        RequiredGroup("traditional_glosses", ("尔雅", "爾雅", "说文", "說文", "注疏", "训诂", "訓詁"), 2),
        RequiredGroup("phonology", ("音韵", "音韻", "读音", "讀音", "通假", "假借")),
        RequiredGroup("analysis_and_conflict", ("分析", "支持", "反证", "反證", "争议", "爭議", "异说", "異說"), 2),
        RequiredGroup("conclusion_status", ("结论等级", "結論等級", "材料可证", "材料可證", "传统训释", "傳統訓釋", "现代通说", "現代通說", "争议", "爭議", "待考"), 2),
    ),
    "etymology": (
        RequiredGroup("object_and_scope", ("研究对象", "研究對象", "本义", "本義", "字源", "时代", "時代"), 2),
        RequiredGroup("form_evidence", ("出土材料", "甲骨", "金文", "简帛", "簡帛", "小篆"), 2),
        RequiredGroup("provenance", ("合集号", "合集號", "器号", "器號", "图版", "圖版", "出处", "出處")),
        RequiredGroup("phonology_and_context", ("音韵", "音韻", "声符", "聲符", "辞例", "辭例", "语境", "語境"), 2),
        RequiredGroup("traditional_and_modern", ("传统训释", "傳統訓釋", "说文", "說文", "尔雅", "爾雅", "现代研究", "現代研究", "学者", "學者"), 2),
        RequiredGroup("conflict_and_status", ("支持", "反证", "反證", "争议", "爭議", "结论等级", "結論等級", "材料可证", "材料可證", "待考"), 2),
    ),
}


SELF_TESTS: dict[str, tuple[str, str]] = {
    "character-form": (
        "研究对象：某字；所问层次：字形。出土材料：甲骨；合集号：123；时代：商。"
        "构形：候选解释；辞例：卜辞语境。传统训释：《说文》；现代研究：某学者。"
        "支持：字形与辞例一致；反证：异体未定；结论等级：争议，待考。",
        "研究对象：某字。《说文》已经证明它的甲骨文原形就是某物。",
    ),
    "exegesis": (
        "原文：某句；上下文：前后两句；篇章：《国语》某篇；底本：四部丛刊；异文：另一版本作某。"
        "传世文献：同时代平行用例；语境：作动词。《尔雅》和《说文》有不同训诂，旧注疏另说。"
        "音韵：采用某体系，可能通假。分析：支持甲说；反证：乙说解释异文。结论等级：争议，待考。",
        "原文：某句。《说文》说是这个意思，所以结论确定。",
    ),
    "etymology": (
        "研究对象：某字本义；时代：商周。出土材料：甲骨和金文；合集号：123。"
        "音韵：声符关系待核；辞例语境：用于某义。传统训释：《说文》作某；现代研究：某学者有异说。"
        "支持：辞例；反证：构形未定；结论等级：现代通说，仍有争议。",
        "研究对象：某字本义。《说文》权威解释，因此本义就是某义。",
    ),
}

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"
INVALID_FIXTURES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "character-form",
        "invalid-placeholder-character-form.md",
        ("placeholder_required_fields",),
    ),
    (
        "etymology",
        "invalid-negated-shuowen-overclaim.md",
        ("shuowen_single_source_overreach",),
    ),
)


SHUOWEN = re.compile(r"《?(?:说文解字|說文解字|说文|說文)》?")
OVERCLAIM = re.compile(
    r"本[义義]就是|原形就是|已[经經]?证明|已[经經]?證明|权威|權威|定论|定論|"
    r"一定是|结论确定|結論確定|释义确定|釋義確定"
)
INDEPENDENT_EVIDENCE = (
    "合集号", "合集號", "器号", "器號", "图版", "圖版", "卜辞", "卜辭", "铭文", "銘文",
    "简帛", "簡帛", "音韵", "音韻", "平行用例", "现代研究", "現代研究", "学者", "學者",
)
REQUIRED_VALUE_FIELDS: dict[str, tuple[str, ...]] = {
    "character-form": (
        "研究对象", "研究對象", "出土材料", "合集号", "合集號", "器号", "器號", "图版", "圖版",
        "时代", "時代", "年代", "构形", "構形", "辞例", "辭例", "传统训释", "傳統訓釋", "现代研究", "現代研究", "支持",
    ),
    "exegesis": (
        "原文", "上下文", "篇章", "底本", "版本", "异文", "異文", "传世文献", "傳世文獻",
        "传统训释", "傳統訓釋", "音韵", "音韻", "分析", "支持",
    ),
    "etymology": (
        "研究对象", "研究對象", "时代", "時代", "出土材料", "合集号", "合集號", "器号", "器號",
        "图版", "圖版", "音韵", "音韻", "辞例", "辭例", "传统训释", "傳統訓釋", "现代研究", "現代研究", "支持",
    ),
}
PLACEHOLDER_VALUE = re.compile(
    r"^(?:无|無|暂无|暫無|待补|待補|待查|未知|不明|未执行|未執行|未核验|未核驗|无需查|無需查|无须查|無須查|不适用|不適用|N/?A|TBD|TODO|[-—/]+)$",
    re.IGNORECASE,
)
PLACEHOLDER_PREFIXES = (
    "待补",
    "待補",
    "待完善",
    "待查",
    "待定",
    "稍后补",
    "稍後補",
    "后续补",
    "後續補",
    "未提供",
    "未填写",
    "未填寫",
)
FIELD_ASSIGNMENT = re.compile(r"(?:^|[。；;\n|])\s*(?:[-*]\s*)?([^：:]+)[：:]\s*([^。；;\n|]*)")
NEGATED_EVIDENCE = re.compile(
    r"无需查|無需查|无须查|無須查|不必查|不需查|未查|尚未查|待查|待补|待補|"
    r"未知|不明|不存在|没有(?:材料|证据|记录|相关)?|沒有(?:材料|證據|記錄|相關)?|"
    r"未见|未見|无相关|無相關|缺少|不足"
)
NEGATED_OVERCLAIM = re.compile(
    r"(?:并非|並非|不是|不算)(?:唯一)?(?:权威|權威|定论|定論)|"
    r"(?:不等于|不等於|不代表)(?:权威|權威|定论|定論)|"
    r"(?:不能|不可|不得|不应|不應|不宜|无法|無法|未能|不足以)"
    r"(?:据此|據此|由此)?(?:直接)?(?:说|說|认为|認為|断定|斷定|证明|證明)?"
    r"(?:这个字|這個字|该字|該字|其)?(?:的)?"
    r"(?:本义就是|本義就是|原形就是|一定是|结论确定|結論確定|释义确定|釋義確定)"
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def is_placeholder_value(value: str) -> bool:
    normalized = normalize(value)
    return bool(PLACEHOLDER_VALUE.fullmatch(normalized)) or normalized.startswith(PLACEHOLDER_PREFIXES)


def has_placeholder_required_field(kind: str, text: str) -> bool:
    required_fields = REQUIRED_VALUE_FIELDS[kind]
    for match in FIELD_ASSIGNMENT.finditer(text):
        field, value = (part.strip() for part in match.groups())
        if any(alias in field for alias in required_fields) and is_placeholder_value(value):
            return True
    return False


def without_negated_clauses(text: str, negation: re.Pattern[str]) -> str:
    clauses = re.split(r"[。；;\n|]", text)
    return " ".join(clause for clause in clauses if not negation.search(clause))


def affirmative_claim_text(text: str) -> str:
    return NEGATED_OVERCLAIM.sub("", text)


def missing_groups(kind: str, text: str) -> list[str]:
    normalized = normalize(text)
    missing: list[str] = []
    for group in CHECKS[kind]:
        hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
        if hits < group.min_hits:
            missing.append(group.name)
    if has_placeholder_required_field(kind, text):
        missing.append("placeholder_required_fields")
    affirmative_claims = normalize(affirmative_claim_text(text))
    if SHUOWEN.search(affirmative_claims) and OVERCLAIM.search(affirmative_claims):
        affirmative_evidence = normalize(without_negated_clauses(text, NEGATED_EVIDENCE))
        hits = sum(1 for term in INDEPENDENT_EVIDENCE if term.casefold() in affirmative_evidence)
        if hits < 2:
            missing.append("shuowen_single_source_overreach")
    return missing


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    return sys.stdin.read()


def run_self_test() -> int:
    failures: list[str] = []
    for kind, (valid_text, invalid_text) in SELF_TESTS.items():
        valid_missing = missing_groups(kind, valid_text)
        if valid_missing:
            failures.append(f"{kind}: valid fixture missing {', '.join(valid_missing)}")
        invalid_missing = missing_groups(kind, invalid_text)
        if not invalid_missing:
            failures.append(f"{kind}: invalid fixture unexpectedly passed")
        if "shuowen_single_source_overreach" not in invalid_missing:
            failures.append(f"{kind}: Shuowen-only overclaim was not rejected")
    for kind, fixture_name, expected_missing in INVALID_FIXTURES:
        fixture_text = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8")
        actual_missing = set(missing_groups(kind, fixture_text))
        absent = [name for name in expected_missing if name not in actual_missing]
        if absent:
            failures.append(f"{fixture_name}: expected missing {', '.join(absent)}")
    placeholder_variant = (
        "研究对象：待补充；所问层次：字形；出土材料：待补充；合集号：待补充；时代：待补充；"
        "构形：待补充；辞例：待补充；传统训释：待补充；现代研究：待补充；支持：待补充；"
        "反证：待补充；结论等级：材料可证。"
    )
    if "placeholder_required_fields" not in missing_groups("character-form", placeholder_variant):
        failures.append("character-form: common placeholder variant unexpectedly passed")
    safe_boundary = (
        "原文：某句；上下文：前后文；篇章：《国语》某篇；传世文献：本篇；语境：作动词；"
        "《尔雅》有一训；《说文》并非权威，不能据此说本义就是某义；读音：某；分析：甲说较优；"
        "支持：语法；反证：异文；结论等级：争议，待考。"
    )
    if "shuowen_single_source_overreach" in missing_groups("exegesis", safe_boundary):
        failures.append("exegesis: negated Shuowen overclaim was rejected")
    contrastive_overclaim = (
        "研究对象：某字本义；时代：商周；出土材料：甲骨和金文；合集号：不存在；"
        "音韵：没有材料；辞例语境：未见；传统训释：《说文》不是一般参考，而是权威解释；"
        "现代研究：无相关研究；支持：传统说解；反证：无；结论等级：材料可证，因此本义就是某义。"
    )
    if "shuowen_single_source_overreach" not in missing_groups("etymology", contrastive_overclaim):
        failures.append("etymology: contrastive negation bypassed Shuowen overclaim guard")
    negated_evidence = (
        "研究对象：某字本义；时代：商周；出土材料：甲骨和金文；合集号：不存在；"
        "音韵：没有材料；辞例语境：未见；传统训释：《说文》权威解释；现代研究：无相关研究；"
        "支持：《说文》；反证：无；结论等级：材料可证，因此本义就是某义。"
    )
    if "shuowen_single_source_overreach" not in missing_groups("etymology", negated_evidence):
        failures.append("etymology: negated evidence bypassed Shuowen overclaim guard")
    if failures:
        print("FAIL philology evidence self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK philology evidence self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查训诂证据卡的结构完整性和单一证据越权")
    parser.add_argument("--kind", choices=sorted(CHECKS), help="研究类型")
    parser.add_argument("--file", help="待检查的本地 Markdown/文本文件")
    parser.add_argument("--text", help="直接传入待检查文本")
    parser.add_argument("--self-test", action="store_true", help="运行内置正反例自测")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.kind:
        parser.error("--kind is required unless --self-test is used")

    text = read_input(args)
    if not text.strip():
        print("FAIL philology evidence check: empty input", file=sys.stderr)
        return 2

    missing = missing_groups(args.kind, text)
    if missing:
        print(
            f"FAIL philology evidence check: kind={args.kind} missing " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    print(f"OK philology evidence check: kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
