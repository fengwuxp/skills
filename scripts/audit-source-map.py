#!/usr/bin/env python3
"""Audit source-map attribution and unverifiable-source boundaries.

The script only inspects repository Markdown files. It does not access the
network, upload content, read secrets, or modify files. It is a deterministic
guard against treating unreadable external articles as absorbed sources.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP = ROOT / "product-architecture-expert" / "references" / "source-map.md"
SKILL_MD = ROOT / "product-architecture-expert" / "SKILL.md"
PAYMENT_ROUTING = ROOT / "product-architecture-expert" / "references" / "payment-scenario-routing.md"

RULE_TERMS = [
    "Playwright 或等价浏览器自动化读取标题、作者、发布时间和正文",
    "公开 HTML 中可读取到标题、作者、发布时间和正文",
    "Playwright 尝试状态、公开 HTML 读取状态和读取日期",
    "未读取到正文、页面删除、只剩验证页或正文为空",
    "不得作为已吸收来源",
    "不代表原文逐字表述",
    "不作为监管、合同、卡组织规则、财务准则或上线结论",
]

BOUNDARY_TERMS = [
    "不复制文章正文",
    "不声称技能代表作者本人观点",
    "不得继续作为已吸收来源",
    "必须按最新公开来源、合同或专业确认结果复核",
]

KNOWN_UNVERIFIABLE_URLS = {
    "https://mp.weixin.qq.com/s/vHJ7LlePC8o5qV84XVtU4Q": [
        "2026-05-26 Playwright 核验结果为页面已被发布者删除",
        "正文不可复核",
        "仅保留为历史索引线索",
        "不得作为已吸收来源",
    ],
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_no(text: str, needle: str) -> int:
    before = text.split(needle, 1)[0]
    return before.count("\n") + 1


def source_bullets(text: str) -> list[tuple[int, str]]:
    bullets: list[tuple[int, str]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("- ") and "http" in stripped:
            bullets.append((idx, stripped))
    return bullets


def urls(line: str) -> list[str]:
    return re.findall(r"`(https?://[^`]+)`", line)


def has_date(text: str) -> bool:
    return bool(re.search(r"20\d{2}-\d{2}-\d{2}", text))


def audit_text(
    text: str,
    *,
    source_label: str,
    skill_text: str,
    skill_label: str,
    routing_text: str,
    routing_label: str,
) -> list[str]:
    failures: list[str] = []

    for term in RULE_TERMS:
        if term not in text:
            failures.append(f"{source_label}: missing source reading rule term: {term}")

    for term in BOUNDARY_TERMS:
        if term not in text:
            failures.append(f"{source_label}: missing source boundary term: {term}")

    if "references/source-map.md" not in skill_text:
        failures.append(f"{skill_label}: does not link source-map.md")

    if "source-map.md" not in routing_text:
        failures.append(f"{routing_label}: payment routing does not link source-map.md")

    seen_urls: dict[str, int] = {}
    for lineno, bullet in source_bullets(text):
        bullet_urls = urls(bullet)
        if not bullet_urls:
            failures.append(f"{source_label}:{lineno}: source bullet has http text but no backticked URL")
            continue

        for url in bullet_urls:
            if url in seen_urls:
                failures.append(
                    f"{source_label}:{lineno}: duplicate URL also appears at line {seen_urls[url]}: {url}"
                )
            seen_urls[url] = lineno

        is_wechat_article = "mp.weixin.qq.com" in bullet and "微信公众号文章" in bullet
        if is_wechat_article:
            has_supported_status = any(
                term in bullet
                for term in [
                    "公开内容用于参考",
                    "公开内容仅用于",
                    "Playwright 核验结果",
                ]
            )
            if not has_supported_status:
                failures.append(
                    f"{source_label}:{lineno}: WeChat article must state readable reference or Playwright audit status"
                )
            has_html_fallback_status = "公开 HTML" in bullet and has_supported_status
            if has_html_fallback_status:
                for required in ["Playwright", "标题、作者、发布时间和正文"]:
                    if required not in bullet:
                        failures.append(
                            f"{source_label}:{lineno}: HTML fallback source missing trace term: {required}"
                        )
                if not has_date(bullet):
                    failures.append(f"{source_label}:{lineno}: HTML fallback source must record read date")

        is_unverifiable = any(
            term in bullet
            for term in [
                "不可复核",
                "历史索引线索",
                "已被发布者删除",
                "只剩验证页",
            ]
        )
        if is_unverifiable:
            if "公开内容用于参考" in bullet or "公开内容仅用于" in bullet:
                failures.append(
                    f"{source_label}:{lineno}: unverifiable source must not be written as absorbed reference"
                )
            for required in ["Playwright 核验结果", "正文不可复核", "不得作为已吸收来源"]:
                if required not in bullet:
                    failures.append(
                        f"{source_label}:{lineno}: unverifiable source missing downgrade term: {required}"
                    )
            if not has_date(bullet):
                failures.append(f"{source_label}:{lineno}: unverifiable source must record audit date")

    for url, required_terms in KNOWN_UNVERIFIABLE_URLS.items():
        if url not in text:
            failures.append(f"{source_label}: known unverifiable URL missing from source map: {url}")
            continue
        line_start = line_no(text, url)
        source_line = next((line for _, line in source_bullets(text) if url in line), "")
        for term in required_terms:
            if term not in source_line:
                failures.append(f"{source_label}:{line_start}: known unverifiable source missing: {term}")

    if "公开内容用于参考多业务线清结算全局规划" in text:
        failures.append(f"{source_label}: stale attribution for deleted clearing article")

    return failures


def audit_current() -> list[str]:
    return audit_text(
        read(SOURCE_MAP),
        source_label=rel(SOURCE_MAP),
        skill_text=read(SKILL_MD),
        skill_label=rel(SKILL_MD),
        routing_text=read(PAYMENT_ROUTING),
        routing_label=rel(PAYMENT_ROUTING),
    )


KNOWN_BAD_URL = "https://mp.weixin.qq.com/s/vHJ7LlePC8o5qV84XVtU4Q"
KNOWN_GOOD_BULLET = (
    f"- 微信公众号文章《头部大厂，怎么做清结算全局规划，分享一个真实案例！》：`{KNOWN_BAD_URL}`。"
    "2026-05-26 Playwright 核验结果为页面已被发布者删除，正文不可复核；"
    "仅保留为历史索引线索，不得作为已吸收来源。"
)
READABLE_DEMO_URL = "https://" + "mp.weixin.qq.com/s/readable-demo"
ORDINARY_DEMO_URL = "https://" + "example.com/source-map-demo"
READABLE_BULLET = (
    f"- 微信公众号文章《已读取文章》：`{READABLE_DEMO_URL}`。公开内容用于参考支付账本观。"
)
HTML_FALLBACK_DEMO_URL = "https://" + "mp.weixin.qq.com/s/html-fallback-demo"
HTML_FALLBACK_BULLET = (
    f"- 微信公众号文章《HTML 可读取文章》：`{HTML_FALLBACK_DEMO_URL}`。"
    "2026-05-26 已尝试 Playwright，当前浏览器通道加载为空白；"
    "随后通过公开 HTML 读取到标题、作者、发布时间和正文，公开内容用于参考复杂度治理。"
)
VALID_FIXTURE = f"""# 公开资料来源与支付专项提炼边界

## 读取与归因规则

- 微信文章等动态页面必须先通过 Playwright 或等价浏览器自动化读取标题、作者、发布时间和正文；如果 Playwright 当前通道失败，但公开 HTML 中可读取到标题、作者、发布时间和正文，也可以写成“公开内容用于参考”，但条目必须同时记录 Playwright 尝试状态、公开 HTML 读取状态和读取日期。
- 未读取到正文、页面删除、只剩验证页或正文为空的条目，只能标为“当前不可复核”或“历史索引线索”，不得作为已吸收来源。
- 条目中的英文术语、分层名称和能力边界可能是 Skill 为统一输出做的标准化表达，不代表原文逐字表述；需要引用作者原话时必须重新读取正文并核对。
- 从文章吸收的内容只作为产品架构问题、检查项、路由和边界，不作为监管、合同、卡组织规则、财务准则或上线结论。

## 已参考的公开来源

{READABLE_BULLET}
{HTML_FALLBACK_BULLET}
{KNOWN_GOOD_BULLET}
- 普通公开来源：`{ORDINARY_DEMO_URL}`。公开资料用于主题发现。

## 提炼边界

- 不复制文章正文、付费课程内容、书籍章节、原图、课件、原型或专有案例。
- 不声称技能代表作者本人观点。
- 对当前不可复核、已删除或只剩索引页的文章，不得继续作为已吸收来源；相关能力只能按通用方法、项目事实或其他可核验来源表达，并标明待核验。
- 外部规则具有时效性。引用法律法规、卡组织规则、Nacha/ACH、PCI DSS、银行/通道协议、税务或会计准则时，必须按最新公开来源、合同或专业确认结果复核，并记录核验日期。
"""
VALID_SKILL_FIXTURE = "需要核对公开来源边界时读取 `references/source-map.md`。"
VALID_ROUTING_FIXTURE = "支付专项来源和归因边界见 `source-map.md`。"


def fixture_failures(name: str, source_text: str) -> list[str]:
    return audit_text(
        source_text,
        source_label=f"fixture:{name}",
        skill_text=VALID_SKILL_FIXTURE,
        skill_label=f"fixture:{name}:SKILL.md",
        routing_text=VALID_ROUTING_FIXTURE,
        routing_label=f"fixture:{name}:payment-scenario-routing.md",
    )


def run_self_test() -> list[str]:
    failures: list[str] = []
    valid_failures = fixture_failures("valid", VALID_FIXTURE)
    if valid_failures:
        failures.append("self-test valid fixture should pass")
        failures.extend(valid_failures)

    negative_cases = [
        (
            "absorbed-unverifiable",
            VALID_FIXTURE.replace(
                KNOWN_GOOD_BULLET,
                KNOWN_GOOD_BULLET.replace(
                    "仅保留为历史索引线索，不得作为已吸收来源",
                    "仅保留为历史索引线索，公开内容用于参考多业务线清结算全局规划，不得作为已吸收来源",
                ),
            ),
            "unverifiable source must not be written as absorbed reference",
        ),
        (
            "missing-audit-date",
            VALID_FIXTURE.replace(
                KNOWN_GOOD_BULLET,
                KNOWN_GOOD_BULLET.replace("2026-05-26 Playwright 核验结果", "Playwright 核验结果"),
            ),
            "unverifiable source must record audit date",
        ),
        (
            "missing-downgrade-term",
            VALID_FIXTURE.replace(
                KNOWN_GOOD_BULLET,
                KNOWN_GOOD_BULLET.replace("不得作为已吸收来源", "不得作为正式来源"),
            ),
            "unverifiable source missing downgrade term: 不得作为已吸收来源",
        ),
        (
            "stale-deleted-clearing-attribution",
            VALID_FIXTURE.replace(
                READABLE_BULLET,
                READABLE_BULLET.replace("公开内容用于参考支付账本观", "公开内容用于参考多业务线清结算全局规划"),
            ),
            "stale attribution for deleted clearing article",
        ),
        (
            "duplicate-url",
            VALID_FIXTURE.replace(READABLE_BULLET, f"{READABLE_BULLET}\n{READABLE_BULLET}"),
            "duplicate URL also appears",
        ),
        (
            "wechat-missing-readable-or-audit-status",
            VALID_FIXTURE.replace(
                READABLE_BULLET,
                READABLE_BULLET.replace("公开内容用于参考支付账本观", "用于支付账本观"),
            ),
            "WeChat article must state readable reference or Playwright audit status",
        ),
        (
            "html-fallback-missing-playwright-trace",
            VALID_FIXTURE.replace(
                HTML_FALLBACK_BULLET,
                HTML_FALLBACK_BULLET.replace("已尝试 Playwright，", ""),
            ),
            "HTML fallback source missing trace term: Playwright",
        ),
        (
            "html-fallback-missing-date",
            VALID_FIXTURE.replace(
                HTML_FALLBACK_BULLET,
                HTML_FALLBACK_BULLET.replace("2026-05-26 ", ""),
            ),
            "HTML fallback source must record read date",
        ),
        (
            "html-fallback-missing-fields",
            VALID_FIXTURE.replace(
                HTML_FALLBACK_BULLET,
                HTML_FALLBACK_BULLET.replace("标题、作者、发布时间和正文", "正文"),
            ),
            "HTML fallback source missing trace term: 标题、作者、发布时间和正文",
        ),
        (
            "html-fallback-rule-wording-detected",
            VALID_FIXTURE.replace(
                HTML_FALLBACK_BULLET,
                HTML_FALLBACK_BULLET.replace("通过公开 HTML 读取到", "公开 HTML 中可读取到"),
            ).replace("2026-05-26 ", "", 1),
            "HTML fallback source must record read date",
        ),
    ]

    for name, source_text, expected in negative_cases:
        case_failures = fixture_failures(name, source_text)
        joined = "\n".join(case_failures)
        if not case_failures:
            failures.append(f"self-test {name}: expected failure but audit passed")
        elif expected not in joined:
            failures.append(f"self-test {name}: expected failure containing {expected!r}")
            failures.extend(case_failures)

    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run embedded positive and negative fixtures for the source-map audit rules",
    )
    args = parser.parse_args(argv)

    failures = run_self_test() if args.self_test else audit_current()

    if failures:
        print("FAIL source map self-test" if args.self_test else "FAIL source map audit")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("OK source map self-test" if args.self_test else "OK source map audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
