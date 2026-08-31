#!/usr/bin/env python3
"""Build, search, and verify the offline UI style evidence gallery.

Inputs are an explicit catalog path and optional output directory. Generated
files stay under that output directory. The script does not access the network,
execute upstream code, or read secrets.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = SKILL_ROOT / "assets" / "style-gallery"
DEFAULT_CATALOG = DEFAULT_ROOT / "catalog.json"
DEFAULT_RELEVANCE = DEFAULT_ROOT / "relevance-cases.json"
LICENSE_NAME = "LICENSE.ui-ux-pro-max.txt"
ALLOWED_TYPES = {"visual-language", "data-task", "mobile-system"}
ALLOWED_STATUSES = {"active", "supplemental"}
TOKEN_FIELDS = {
    "bg",
    "surface",
    "text",
    "muted",
    "accent",
    "accent2",
    "border",
    "radius",
    "shadow",
    "font",
    "display_font",
}
UNSAFE_HTML = {
    "external URL": re.compile(r"https?://", re.IGNORECASE),
    "external script": re.compile(r"<script\b[^>]*\bsrc\s*=", re.IGNORECASE),
    "form submission": re.compile(r"<form\b", re.IGNORECASE),
    "network request": re.compile(r"\b(?:fetch|XMLHttpRequest|sendBeacon)\s*\(", re.IGNORECASE),
    "browser storage": re.compile(r"\b(?:localStorage|sessionStorage|indexedDB)\b"),
    "download action": re.compile(r"\bdownload\s*=", re.IGNORECASE),
}


class CatalogError(ValueError):
    pass


def read_catalog(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"cannot read catalog: {type(exc).__name__}") from exc
    if not isinstance(data, dict):
        raise CatalogError("catalog root must be an object")
    return data


def non_empty_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def validate_catalog(catalog: dict[str, Any], catalog_path: Path) -> list[str]:
    errors: list[str] = []
    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if catalog.get("status") != "pilot":
        errors.append("status must be pilot")
    if catalog.get("proof_limit") != "local-visual-evidence-only":
        errors.append("proof_limit must be local-visual-evidence-only")

    source = catalog.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        for field in (
            "repository",
            "commit",
            "commit_authored_at",
            "license",
            "license_sha256",
            "styles_sha256",
            "usage_boundary",
        ):
            if not isinstance(source.get(field), str) or not source[field].strip():
                errors.append(f"source.{field} is required")
        if source.get("license") != "MIT":
            errors.append("source.license must be MIT")
        if not re.fullmatch(r"[0-9a-f]{40}", str(source.get("commit", ""))):
            errors.append("source.commit must be a full lowercase Git SHA")

    groups = catalog.get("comparison_groups")
    if not isinstance(groups, dict) or len(groups) != 3:
        errors.append("comparison_groups must contain exactly 3 groups")
        groups = {}

    styles = catalog.get("styles")
    if not isinstance(styles, list) or len(styles) != 24:
        errors.append("styles must contain exactly 24 pilot entries")
        styles = styles if isinstance(styles, list) else []

    seen: set[str] = set()
    for index, style in enumerate(styles):
        prefix = f"styles[{index}]"
        if not isinstance(style, dict):
            errors.append(f"{prefix} must be an object")
            continue
        style_id = style.get("id")
        if not isinstance(style_id, str) or not re.fullmatch(r"[a-z0-9-]+", style_id):
            errors.append(f"{prefix}.id must use lowercase letters, digits, and hyphens")
            continue
        if style_id in seen:
            errors.append(f"duplicate style id: {style_id}")
        seen.add(style_id)
        if style.get("upstream_status") not in ALLOWED_STATUSES:
            errors.append(f"{style_id}: deprecated or unknown upstream status")
        if style.get("type") not in ALLOWED_TYPES:
            errors.append(f"{style_id}: unknown type")
        if style.get("comparison_group") not in groups:
            errors.append(f"{style_id}: unknown comparison group")
        for field in ("name", "upstream_type", "summary", "accessibility_risk", "treatment"):
            if not isinstance(style.get(field), str) or not style[field].strip():
                errors.append(f"{style_id}.{field} is required")
        for field in ("tags", "best_for", "avoid_for", "observable_variables"):
            if not non_empty_strings(style.get(field)):
                errors.append(f"{style_id}.{field} must be a non-empty string list")
        tokens = style.get("tokens")
        if not isinstance(tokens, dict) or set(tokens) != TOKEN_FIELDS:
            errors.append(f"{style_id}.tokens must contain the exact token contract")
        elif any(not isinstance(value, str) or not value.strip() for value in tokens.values()):
            errors.append(f"{style_id}.tokens values must be non-empty strings")
        specimen_path = style.get("specimen_path")
        expected_path = f"styles/{style_id}.html"
        if specimen_path != expected_path:
            errors.append(f"{style_id}.specimen_path must be {expected_path}")

    license_path = catalog_path.parent / LICENSE_NAME
    if not license_path.is_file():
        errors.append(f"missing {LICENSE_NAME}")
    elif isinstance(source, dict) and isinstance(source.get("license_sha256"), str):
        actual = hashlib.sha256(license_path.read_bytes()).hexdigest()
        if actual != source["license_sha256"]:
            errors.append(f"{LICENSE_NAME} sha256 mismatch")
    return errors


def normalize_terms(value: str) -> list[str]:
    return [term for term in re.findall(r"[\w-]+", value.casefold()) if term]


def search_catalog(
    catalog: dict[str, Any], query: str, style_type: str | None, limit: int
) -> list[dict[str, Any]]:
    terms = normalize_terms(query)
    results: list[tuple[int, dict[str, Any]]] = []
    for style in catalog["styles"]:
        if style_type and style["type"] != style_type:
            continue
        name = style["name"].casefold()
        style_id = style["id"].casefold()
        tags = [item.casefold() for item in style["tags"]]
        haystack = " ".join(
            [name, style_id, style["summary"].casefold(), *tags]
            + [item.casefold() for item in style["best_for"]]
            + [item.casefold() for item in style["observable_variables"]]
        )
        score = 0
        for term in terms:
            if term in tags:
                score += 6
            if term in name:
                score += 5
            if term in style_id:
                score += 4
            if term in haystack:
                score += 2
        if score or not terms:
            results.append((score, style))
    results.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [
        {
            "id": style["id"],
            "name": style["name"],
            "type": style["type"],
            "upstream_status": style["upstream_status"],
            "summary": style["summary"],
            "specimen_path": style["specimen_path"],
            "score": score,
            "proof_limit": catalog["proof_limit"],
        }
        for score, style in results[:limit]
    ]


def evaluate_relevance(
    catalog: dict[str, Any], relevance: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    cases = relevance.get("cases")
    if relevance.get("version") != 1:
        errors.append("relevance version must be 1")
    if relevance.get("proof_limit") != "deterministic-relevance-only":
        errors.append("relevance proof_limit must be deterministic-relevance-only")
    if not isinstance(cases, list) or not cases:
        errors.append("relevance cases must be a non-empty list")
        cases = []

    known_ids = {style["id"] for style in catalog["styles"]}
    failed_case_ids: list[str] = []
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, case in enumerate(cases):
        case_errors: list[str] = []
        if not isinstance(case, dict):
            errors.append(f"relevance cases[{index}] must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9-]+", case_id):
            errors.append(f"relevance cases[{index}].id is invalid")
            continue
        if case_id in seen:
            errors.append(f"duplicate relevance case id: {case_id}")
        seen.add(case_id)
        query = case.get("query")
        style_type = case.get("type")
        limit = case.get("limit")
        expected_first = case.get("expected_first")
        required_ids = case.get("required_ids")
        forbidden_ids = case.get("forbidden_ids")
        if not isinstance(query, str) or not query.strip():
            case_errors.append("query is required")
        if style_type not in ALLOWED_TYPES:
            case_errors.append("type is invalid")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 5:
            case_errors.append("limit must be between 1 and 5")
        if expected_first not in known_ids:
            case_errors.append("expected_first is unknown")
        if not non_empty_strings(required_ids) or not set(required_ids).issubset(known_ids):
            case_errors.append("required_ids are invalid")
        if not isinstance(forbidden_ids, list) or any(
            not isinstance(item, str) or item not in known_ids for item in forbidden_ids
        ):
            case_errors.append("forbidden_ids are invalid")
        matches = (
            search_catalog(catalog, query, style_type, limit)
            if not case_errors
            else []
        )
        match_ids = [item["id"] for item in matches]
        if not match_ids or match_ids[0] != expected_first:
            case_errors.append(f"expected first {expected_first}, got {match_ids[:1]}")
        missing = sorted(set(required_ids or []) - set(match_ids))
        if missing:
            case_errors.append(f"missing required ids: {', '.join(missing)}")
        forbidden = sorted(set(forbidden_ids or []) & set(match_ids))
        if forbidden:
            case_errors.append(f"returned forbidden ids: {', '.join(forbidden)}")
        if any(item["type"] != style_type for item in matches):
            case_errors.append("returned a cross-type result")
        if case_errors:
            failed_case_ids.append(case_id)
        results.append(
            {
                "id": case_id,
                "status": "failed" if case_errors else "passed",
                "result_ids": match_ids,
                "errors": case_errors,
            }
        )
    failed = len(failed_case_ids) + len(errors)
    return {
        "status": "failed" if failed else "passed",
        "cases": len(cases),
        "passed": len(cases) - len(failed_case_ids) if not errors else 0,
        "failed": failed,
        "failed_case_ids": failed_case_ids,
        "errors": errors,
        "results": results,
        "proof_limit": relevance.get("proof_limit"),
    }


def css_variables(tokens: dict[str, str]) -> str:
    return ";".join(f"--{name.replace('_', '-')}:{value}" for name, value in tokens.items())


def workspace_markup() -> str:
    return """
    <div class="shell workspace-shell">
      <header class="appbar"><a class="brand" href="#main">Northstar</a><nav aria-label="工作区"><a href="#main">项目</a><a href="#activity">动态</a><button type="button">新建</button></nav></header>
      <div class="workspace-grid">
        <aside aria-label="项目导航"><p class="eyebrow">工作区</p><h2>设计交付</h2><a class="nav-item active" href="#main">概览 <span>12</span></a><a class="nav-item" href="#activity">待处理 <span>4</span></a><a class="nav-item" href="#team">成员 <span>8</span></a></aside>
        <main id="main"><div class="title-row"><div><p class="eyebrow">本周进展</p><h1>发布准备</h1></div><button type="button">查看计划</button></div>
          <section class="metric-grid" aria-label="关键指标"><article><span>完成度</span><strong>76%</strong><small>较上周 +12%</small></article><article><span>待复核</span><strong>04</strong><small>2 项今天到期</small></article><article><span>参与者</span><strong>08</strong><small>3 个角色在线</small></article></section>
          <section class="content-grid"><article class="primary-panel"><div class="panel-head"><h2>里程碑</h2><span class="status">进行中</span></div><div class="progress" aria-label="完成 76%"><i style="width:76%"></i></div><ul><li><b>内容核对</b><span>已完成</span></li><li><b>设计复核</b><span>今天</span></li><li><b>工程验收</b><span>周五</span></li></ul></article><article id="activity"><div class="panel-head"><h2>最近动态</h2><button class="icon-button" type="button" title="更多动态" aria-label="更多动态">···</button></div><p><b>林澈</b> 更新了错误恢复说明</p><p><b>周岭</b> 完成移动视口走查</p><p><b>纪宁</b> 提交了评审意见</p></article></section>
        </main>
      </div>
    </div>"""


def operations_markup() -> str:
    return """
    <div class="shell operations-shell">
      <header class="appbar"><a class="brand" href="#main">Operations Pulse</a><nav aria-label="运营视图"><a href="#main">总览</a><a href="#events">事件</a><button type="button">确认告警</button></nav></header>
      <main id="main"><div class="title-row"><div><p class="eyebrow">UTC+8 · 10:42:18</p><h1>核心服务运行态</h1></div><span class="live-badge"><i></i> 数据有效</span></div>
        <section class="metric-grid" aria-label="实时指标"><article><span>请求成功率</span><strong>99.92%</strong><small>过去 15 分钟</small></article><article><span>P95 延迟</span><strong>184 ms</strong><small>阈值 250 ms</small></article><article><span>待确认事件</span><strong>03</strong><small>1 项高优先级</small></article><article><span>处理队列</span><strong>1,284</strong><small>下降 8.4%</small></article></section>
        <section class="content-grid"><article class="primary-panel"><div class="panel-head"><h2>流量趋势</h2><span>最近 12 个窗口</span></div><div class="bars" aria-label="流量趋势柱状图"><i style="height:42%"></i><i style="height:58%"></i><i style="height:48%"></i><i style="height:76%"></i><i style="height:68%"></i><i style="height:84%"></i><i style="height:72%"></i><i style="height:90%"></i><i style="height:78%"></i><i style="height:66%"></i><i style="height:82%"></i><i style="height:74%"></i></div></article><article><div class="panel-head"><h2>服务状态</h2><span>4 / 4</span></div><ul class="service-list"><li><i class="ok"></i><b>API 网关</b><span>正常</span></li><li><i class="ok"></i><b>账务投影</b><span>正常</span></li><li><i class="warn"></i><b>消息消费</b><span>关注</span></li><li><i class="ok"></i><b>数据仓库</b><span>正常</span></li></ul></article></section>
        <section id="events" class="event-table" aria-label="事件列表"><div class="table-row table-head"><span>时间</span><span>事件</span><span>范围</span><span>状态</span></div><div class="table-row"><span>10:39</span><b>消费延迟超过观察线</b><span>华南</span><span class="status warning">待确认</span></div><div class="table-row"><span>10:34</span><b>网关错误率恢复</b><span>全局</span><span class="status">已恢复</span></div><div class="table-row"><span>10:21</span><b>报表批次完成</b><span>亚太</span><span class="status">完成</span></div></section>
      </main>
    </div>"""


def mobile_markup() -> str:
    return """
    <main id="main" class="mobile-stage"><section class="phone" aria-label="移动任务示例"><header><div><p class="eyebrow">星期一 · 10:42</p><h1>待办中心</h1></div><button class="icon-button" type="button" title="搜索" aria-label="搜索">⌕</button></header>
      <section class="mobile-summary"><span>今天</span><strong>6 项任务</strong><div class="progress" aria-label="完成 50%"><i style="width:50%"></i></div></section>
      <section aria-labelledby="urgent"><div class="panel-head"><h2 id="urgent">需要处理</h2><span>3</span></div><article class="task"><span class="task-icon">01</span><div><b>供应商资料复核</b><small>高优先级 · 11:30 到期</small></div><span class="status warning">待审</span></article><article class="task"><span class="task-icon">02</span><div><b>季度权限确认</b><small>安全团队 · 今天</small></div><span class="status">进行中</span></article><article class="task"><span class="task-icon">03</span><div><b>移动端发布检查</b><small>产品交付 · 周三</small></div><span class="status">未开始</span></article></section>
      <button class="primary-action" type="button">开始处理</button><nav class="bottom-nav" aria-label="主导航"><a class="active" href="#main">待办</a><a href="#activity">动态</a><a href="#profile">我的</a></nav></section></main>"""


BASE_CSS = """
*{box-sizing:border-box}html{font-size:16px}body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);letter-spacing:0;min-width:280px}a{color:inherit;text-decoration:none}button{font:inherit;color:inherit;background:var(--accent);border:1px solid var(--border);border-radius:var(--radius);padding:.58rem .86rem;cursor:pointer;font-weight:700}a:focus-visible,button:focus-visible{outline:3px solid var(--accent2);outline-offset:3px}.specimen-note{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.5rem .8rem;border-bottom:1px solid var(--border);font:600 .72rem/1.3 Arial,sans-serif;background:var(--surface);position:relative;z-index:10}.specimen-note div{display:flex;gap:.45rem;flex-wrap:wrap}.specimen-note span{border:1px solid var(--border);padding:.18rem .38rem;border-radius:3px}.shell{max-width:1180px;margin:0 auto;padding:1rem}.appbar{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.85rem 1rem;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow)}.brand{font:800 1rem/1 var(--display-font)}.appbar nav{display:flex;align-items:center;gap:.9rem}.appbar nav a{font-size:.82rem}.workspace-grid{display:grid;grid-template-columns:210px 1fr;gap:1rem;margin-top:1rem}.workspace-grid aside,.metric-grid article,.content-grid article,.event-table{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow)}.workspace-grid aside{padding:1rem}.workspace-grid main,.operations-shell main{min-width:0}.eyebrow{text-transform:uppercase;font:700 .68rem/1.2 var(--font);color:var(--muted);margin:0 0 .3rem}.workspace-grid h2,.panel-head h2{font:800 .92rem/1.2 var(--display-font);margin:0}.nav-item{display:flex;justify-content:space-between;margin-top:.55rem;padding:.55rem .65rem;border:1px solid transparent}.nav-item.active{border-color:var(--border);background:color-mix(in srgb,var(--accent) 12%,var(--surface))}.title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin:.2rem 0 1rem}.title-row h1,.phone h1{font:850 clamp(1.45rem,3vw,2.3rem)/1.02 var(--display-font);margin:0}.metric-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem}.operations-shell .metric-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.metric-grid article{padding:.85rem;min-height:108px}.metric-grid span,.metric-grid small{display:block;color:var(--muted);font-size:.72rem}.metric-grid strong{display:block;font:850 clamp(1.35rem,3vw,2.1rem)/1 var(--display-font);margin:.8rem 0 .35rem}.content-grid{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(220px,.8fr);gap:.75rem;margin-top:.75rem}.content-grid article{padding:1rem;min-height:180px}.panel-head{display:flex;align-items:center;justify-content:space-between;gap:.7rem}.panel-head>span{font-size:.72rem;color:var(--muted)}.status{display:inline-block;padding:.2rem .4rem;border:1px solid var(--border);border-radius:3px;font-size:.68rem;background:color-mix(in srgb,var(--accent) 12%,var(--surface))}.status.warning{background:color-mix(in srgb,var(--accent2) 22%,var(--surface))}.progress{height:8px;margin:1rem 0;background:color-mix(in srgb,var(--muted) 18%,transparent);overflow:hidden;border-radius:2px}.progress i{display:block;height:100%;background:var(--accent)}ul{list-style:none;padding:0;margin:.7rem 0 0}.primary-panel li,.service-list li{display:grid;grid-template-columns:1fr auto;gap:.7rem;padding:.55rem 0;border-top:1px solid color-mix(in srgb,var(--border) 60%,transparent);font-size:.8rem}.content-grid p{font-size:.8rem;line-height:1.5;border-top:1px solid color-mix(in srgb,var(--border) 60%,transparent);padding-top:.6rem}.icon-button{width:34px;height:34px;padding:0;display:grid;place-items:center;background:transparent}.live-badge{font-size:.72rem;border:1px solid var(--border);padding:.35rem .5rem}.live-badge i,.service-list i{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent);margin-right:.35rem}.service-list i.warn{background:var(--accent2)}.bars{height:130px;display:flex;align-items:end;gap:5px;padding-top:1rem;border-bottom:1px solid var(--border)}.bars i{flex:1;min-width:4px;background:var(--accent);opacity:.78}.event-table{margin-top:.75rem;overflow:hidden}.table-row{display:grid;grid-template-columns:80px minmax(180px,1.5fr) minmax(80px,.6fr) minmax(72px,.5fr);gap:.8rem;align-items:center;padding:.62rem .8rem;border-top:1px solid color-mix(in srgb,var(--border) 60%,transparent);font-size:.78rem}.table-head{background:color-mix(in srgb,var(--muted) 8%,var(--surface));color:var(--muted);border-top:0}.mobile-stage{min-height:calc(100vh - 35px);display:grid;place-items:center;padding:1rem}.phone{width:min(390px,100%);min-height:680px;background:var(--surface);border:1px solid var(--border);border-radius:calc(var(--radius) + 4px);box-shadow:var(--shadow);padding:1rem;position:relative;padding-bottom:76px}.phone header{display:flex;justify-content:space-between;align-items:flex-start}.mobile-summary{margin:1rem 0;padding:1rem;background:color-mix(in srgb,var(--accent) 10%,var(--surface));border:1px solid var(--border);border-radius:var(--radius)}.mobile-summary span,.mobile-summary strong{display:block}.mobile-summary span{font-size:.75rem;color:var(--muted)}.mobile-summary strong{font-size:1.25rem;margin-top:.2rem}.task{display:grid;grid-template-columns:38px 1fr auto;gap:.7rem;align-items:center;padding:.8rem 0;border-top:1px solid color-mix(in srgb,var(--border) 60%,transparent)}.task-icon{width:34px;height:34px;display:grid;place-items:center;background:color-mix(in srgb,var(--accent) 14%,var(--surface));border-radius:var(--radius);font-size:.7rem;font-weight:800}.task small{display:block;color:var(--muted);margin-top:.25rem}.primary-action{width:100%;margin-top:1rem}.bottom-nav{position:absolute;left:1rem;right:1rem;bottom:1rem;display:grid;grid-template-columns:repeat(3,1fr);background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}.bottom-nav a{text-align:center;padding:.75rem .3rem;font-size:.75rem}.bottom-nav a.active{background:var(--accent);color:#fff}
"""


TREATMENT_CSS = """
body.t-swiss{background-image:linear-gradient(90deg,transparent 24px,rgba(0,0,0,.05) 25px,transparent 26px)}.t-swiss .appbar,.t-swiss article,.t-swiss aside{text-transform:none}.t-swiss .title-row h1{max-width:8ch}.t-glass{background-image:linear-gradient(135deg,#0b3f42 0%,#25414d 48%,#683846 100%)}.t-glass .appbar,.t-glass article,.t-glass aside,.t-glass .event-table,.t-glass .phone{backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}.t-neubrutal button{box-shadow:3px 3px 0 #111}.t-neubrutal .metric-grid article:nth-child(2){background:#dce8ff}.t-neubrutal .metric-grid article:nth-child(3){background:#ffd9d5}.t-neubrutal .nav-item.active{box-shadow:3px 3px 0 #111}.t-clay .metric-grid article:nth-child(2){background:#e3f2fc}.t-clay .metric-grid article:nth-child(3){background:#f8e1e6}.t-clay button:active{transform:translateY(2px)}.t-bento .metric-grid{grid-template-columns:1.4fr .8fr .8fr}.t-bento .metric-grid article:first-child{grid-row:span 2;min-height:224px}.t-bento .content-grid{margin-top:-108px;margin-left:calc(40% + .3rem)}.t-cyber::before{content:"";position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 3px,rgba(53,225,208,.035) 4px);z-index:20}.t-cyber .eyebrow,.t-cyber .status{text-transform:uppercase;letter-spacing:.08em}.t-cyber .appbar,.t-cyber article,.t-cyber aside{clip-path:polygon(0 0,calc(100% - 10px) 0,100% 10px,100% 100%,0 100%)}.t-organic .metric-grid article:nth-child(odd){border-radius:8px 24px 8px 24px}.t-organic .content-grid article:first-child{border-radius:24px 8px 24px 8px}.t-editorial .appbar{border-left:0;border-right:0}.t-editorial .title-row{border-bottom:4px double var(--border);padding-bottom:.8rem}.t-editorial .metric-grid article{border-width:0 0 1px}.t-editorial .content-grid{grid-template-columns:1.2fr .8fr}.t-editorial .primary-panel>ul{columns:2;column-gap:1.5rem}.t-dense .shell{max-width:1320px}.t-dense .appbar,.t-dense .metric-grid article,.t-dense .content-grid article{padding:.55rem}.t-dense .metric-grid,.t-dense .content-grid{gap:.4rem}.t-dense .metric-grid article{min-height:84px}.t-dense .table-row{padding:.42rem .6rem}.t-live .live-badge i{animation:pulse 1.4s infinite}.t-live .bars i:nth-child(3n){background:var(--accent2)}.t-live .event-table{box-shadow:var(--shadow)}.t-material .phone{border-radius:28px}.t-material .primary-action,.t-material .bottom-nav{border-radius:999px}.t-material .task-icon{border-radius:50%}.t-material .mobile-summary{background:#e8def8}.t-enterprise .phone{min-height:650px}.t-enterprise .mobile-summary{border-left:4px solid var(--accent)}.t-enterprise .primary-action{background:var(--accent)}.t-oled .appbar,.t-oled article,.t-oled aside{border-color:#303030}.t-oled .status{color:var(--text)}.t-flat .metric-grid article:nth-child(2){background:#e5f4ee}.t-flat .metric-grid article:nth-child(3){background:#fdebe6}.t-flat button{border-color:var(--accent);color:#fff}.t-vibrant .metric-grid article:nth-child(1){background:#ffe457}.t-vibrant .metric-grid article:nth-child(2){background:#ffd7e0}.t-vibrant .metric-grid article:nth-child(3){background:#bde9e7}.t-vibrant .title-row h1{text-transform:uppercase}.t-memphis .appbar{background-image:repeating-linear-gradient(45deg,transparent 0 18px,rgba(239,93,168,.12) 18px 22px)}.t-memphis .metric-grid article:nth-child(2){transform:rotate(-1deg)}.t-memphis .metric-grid article:nth-child(3){transform:rotate(1deg)}.t-hud::before{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(40,215,227,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(40,215,227,.035) 1px,transparent 1px);background-size:28px 28px}.t-hud .eyebrow,.t-hud .status{text-transform:uppercase;letter-spacing:.1em}.t-hud .metric-grid article{border-left:3px solid var(--accent)}.t-pixel .appbar,.t-pixel article,.t-pixel aside,.t-pixel button{box-shadow:var(--shadow)}.t-pixel .progress,.t-pixel .progress i{border-radius:0}.t-pixel .metric-grid strong{letter-spacing:.05em}.t-eink *{transition:none!important}.t-eink .appbar,.t-eink article,.t-eink aside{border-width:1px;box-shadow:none}.t-eink .status{background:var(--accent2);color:#111}.t-executive .metric-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.t-executive .metric-grid article:nth-child(4){display:none}.t-executive .metric-grid strong{font-size:2.35rem}.t-executive .event-table{opacity:.72}.t-drilldown .event-table{border-left:5px solid var(--accent)}.t-drilldown .table-row:nth-child(3){padding-left:1.6rem}.t-drilldown .table-row:nth-child(4){padding-left:2.3rem}.t-financial .metric-grid strong,.t-financial .table-row{font-variant-numeric:tabular-nums}.t-financial .bars i:nth-child(even){background:var(--accent2)}.t-financial .status.warning{color:#72251f}.t-bauhaus .phone,.t-bauhaus .mobile-summary,.t-bauhaus .task,.t-bauhaus .bottom-nav{box-shadow:var(--shadow)}.t-bauhaus .task-icon:nth-child(1){background:#f0c020}.t-bauhaus .primary-action{box-shadow:4px 4px 0 #141414}.t-monochrome .phone{border:3px solid #000}.t-monochrome .mobile-summary,.t-monochrome .bottom-nav{border-width:3px}.t-monochrome .task{border-top:2px solid #000}.t-monochrome .primary-action{background:#000;color:#fff;border-radius:0}@keyframes pulse{50%{opacity:.35;transform:scale(.8)}}
@media (max-width:760px){.specimen-note{align-items:flex-start;flex-direction:column}.shell{padding:.65rem}.appbar nav a{display:none}.workspace-grid{grid-template-columns:1fr}.workspace-grid aside{display:none}.metric-grid,.operations-shell .metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.content-grid{grid-template-columns:1fr}.t-bento .metric-grid{grid-template-columns:1fr 1fr}.t-bento .metric-grid article:first-child{grid-row:auto;grid-column:span 2;min-height:108px}.t-bento .content-grid{margin:0}.table-row{grid-template-columns:54px minmax(140px,1fr) 72px}.table-row span:nth-child(3){display:none}.title-row h1{font-size:1.6rem}.phone{min-height:620px}.mobile-stage{padding:.5rem}}@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;scroll-behavior:auto!important;transition:none!important}}
"""


def render_specimen(style: dict[str, Any], group: dict[str, str]) -> str:
    markup = {
        "workspace": workspace_markup,
        "operations": operations_markup,
        "mobile": mobile_markup,
    }[style["comparison_group"]]()
    variables = css_variables(style["tokens"])
    note = " · ".join(style["observable_variables"][:3])
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(style['name'])} · UI Style Evidence</title><style>:root{{{variables}}}{BASE_CSS}{TREATMENT_CSS}</style></head>
<body class="t-{html.escape(style['treatment'])}" data-style-id="{html.escape(style['id'])}"><header class="specimen-note"><a href="../index.html" aria-label="返回风格目录">← {html.escape(style['name'])}</a><div><span>{html.escape(group['label'])}</span><span>{html.escape(style['upstream_status'])}</span><span title="视觉标本不能证明产品、可访问性或生产就绪">仅视觉证据</span></div></header>{markup}<footer class="specimen-note"><span>{html.escape(note)}</span><span>删除此风格后任务与状态语义应保持不变</span></footer></body></html>
"""


def render_index(catalog: dict[str, Any]) -> str:
    specimen_count = len(catalog["styles"])
    cards = []
    for style in catalog["styles"]:
        search_text = " ".join(
            [style["name"], style["summary"], *style["tags"], *style["best_for"]]
        ).casefold()
        cards.append(
            f"""<article class="style-card" data-type="{html.escape(style['type'])}" data-search="{html.escape(search_text)}"><div class="preview"><iframe loading="lazy" title="{html.escape(style['name'])} 视觉标本" src="{html.escape(style['specimen_path'])}"></iframe></div><div class="card-copy"><div><p>{html.escape(style['type'])} · {html.escape(style['upstream_status'])}</p><h2>{html.escape(style['name'])}</h2></div><p>{html.escape(style['summary'])}</p><div class="tags">{''.join(f'<span>{html.escape(tag)}</span>' for tag in style['tags'][:4])}</div><a href="{html.escape(style['specimen_path'])}">打开标本 <span aria-hidden="true">→</span></a></div></article>"""
        )
    source = catalog["source"]
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UI Style Evidence Gallery</title><style>
*{{box-sizing:border-box}}:root{{--bg:#f4f4f1;--surface:#fff;--text:#171917;--muted:#666b66;--line:#cfd3cd;--accent:#c9362a}}body{{margin:0;background:var(--bg);color:var(--text);font-family:Arial,Helvetica,sans-serif;letter-spacing:0}}a{{color:inherit}}header{{max-width:1500px;margin:auto;padding:1.25rem clamp(1rem,3vw,2rem) .9rem;display:grid;grid-template-columns:minmax(260px,1fr) auto;gap:1rem;align-items:end;border-bottom:1px solid var(--line)}}.kicker{{color:var(--accent);font-weight:800;font-size:.72rem;text-transform:uppercase;margin:0 0 .35rem}}h1{{font-size:clamp(1.7rem,4vw,2.7rem);line-height:1;margin:0;max-width:16ch}}header>p{{margin:0;max-width:58ch;color:var(--muted);line-height:1.55;font-size:.84rem}}.controls{{position:sticky;top:0;z-index:30;background:rgba(244,244,241,.96);border-bottom:1px solid var(--line);padding:.75rem clamp(1rem,3vw,2rem);display:flex;gap:.65rem;align-items:center;flex-wrap:wrap}}.search-wrap{{position:relative;flex:1 1 260px;max-width:520px}}.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}input{{width:100%;border:1px solid #858b84;border-radius:4px;background:#fff;padding:.68rem 2.4rem .68rem .75rem;color:var(--text);font:inherit}}button{{border:1px solid #858b84;background:#fff;color:var(--text);padding:.58rem .7rem;border-radius:4px;font:700 .78rem Arial,sans-serif;cursor:pointer}}button[aria-pressed="true"]{{background:var(--text);color:#fff;border-color:var(--text)}}button.icon{{position:absolute;right:.25rem;top:.22rem;width:34px;height:34px;padding:0;font-size:1.1rem}}button:focus-visible,input:focus-visible,a:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}main{{max-width:1500px;margin:auto;padding:1rem clamp(1rem,3vw,2rem) 2.5rem}}.result-line{{display:flex;justify-content:space-between;gap:1rem;color:var(--muted);font-size:.76rem;margin:.15rem 0 .8rem}}.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:.8rem}}.style-card{{background:var(--surface);border:1px solid var(--line);border-radius:6px;overflow:hidden;min-width:0}}.preview{{height:236px;border-bottom:1px solid var(--line);background:#dfe2dd;overflow:hidden;position:relative}}iframe{{display:block;width:1440px;height:900px;border:0;transform:scale(.29);transform-origin:0 0;pointer-events:none}}.style-card[data-type="mobile-system"] iframe{{position:absolute;top:0;left:50%;width:390px;height:430px;transform:translateX(-50%) scale(.55);transform-origin:top center}}.card-copy{{padding:.9rem;display:grid;gap:.72rem}}.card-copy>div:first-child{{display:flex;align-items:start;justify-content:space-between;gap:.8rem}}.card-copy p{{margin:0;color:var(--muted);font-size:.76rem;line-height:1.45}}.card-copy h2{{margin:.18rem 0 0;font-size:1.03rem}}.tags{{display:flex;gap:.35rem;flex-wrap:wrap}}.tags span{{border:1px solid var(--line);padding:.2rem .38rem;font-size:.68rem}}.card-copy>a{{font-weight:800;font-size:.78rem;text-underline-offset:3px}}.empty{{display:none;padding:2rem;border:1px dashed #858b84;text-align:center}}footer{{max-width:1500px;margin:auto;border-top:1px solid var(--line);padding:1rem clamp(1rem,3vw,2rem);color:var(--muted);font-size:.72rem;line-height:1.5}}@media(max-width:720px){{header{{grid-template-columns:1fr;align-items:start}}.preview{{height:210px}}iframe{{transform:scale(.25)}}.result-line{{align-items:flex-start;flex-direction:column}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important}}}}
</style></head><body><header><div><p class="kicker">本地视觉证据包 · {specimen_count} 个试点</p><h1>先看见，再决定采用什么</h1></div><p>风格页只帮助比较层级、排版、色彩、空间、材质和动效方向。它们不证明产品语义、任务可用、可访问性或生产实现已经成立。</p></header><section class="controls" aria-label="筛选标本"><div class="search-wrap"><label class="sr-only" for="search">搜索风格</label><input id="search" type="search" placeholder="搜索：仪表盘、自然、移动…" autocomplete="off"><button class="icon" id="reset" type="button" title="清空搜索" aria-label="清空搜索">×</button></div><button type="button" data-filter="all" aria-pressed="true">全部</button><button type="button" data-filter="visual-language" aria-pressed="false">视觉语言</button><button type="button" data-filter="data-task" aria-pressed="false">数据任务</button><button type="button" data-filter="mobile-system" aria-pressed="false">移动系统</button></section><main><div class="result-line"><span id="count">{specimen_count} 个标本</span><span>每次用于决策时只打开 3-5 个</span></div><section class="gallery" id="gallery">{''.join(cards)}</section><p class="empty" id="empty">没有匹配的标本。请换一个任务词或清除筛选。</p></main><footer>来源：nextlevelbuilder/ui-ux-pro-max-skill @ {html.escape(source['commit'][:7])} · MIT · 上游当前 88 条记录。本地仅蒸馏 {specimen_count} 条元数据并自建标本，未复制上游 gallery 实现。</footer><script>
const input=document.getElementById('search'),cards=[...document.querySelectorAll('.style-card')],buttons=[...document.querySelectorAll('[data-filter]')],count=document.getElementById('count'),empty=document.getElementById('empty');let active='all';function apply(){{const q=input.value.trim().toLocaleLowerCase();let shown=0;cards.forEach(card=>{{const visible=(active==='all'||card.dataset.type===active)&&(!q||card.dataset.search.includes(q));card.hidden=!visible;if(visible)shown++}});count.textContent=`${{shown}} 个标本`;empty.style.display=shown?'none':'block'}}buttons.forEach(button=>button.addEventListener('click',()=>{{active=button.dataset.filter;buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));apply()}}));input.addEventListener('input',apply);document.getElementById('reset').addEventListener('click',()=>{{input.value='';active='all';buttons.forEach((item,index)=>item.setAttribute('aria-pressed',String(index===0)));apply();input.focus()}});
</script></body></html>
"""


def render_files(catalog: dict[str, Any]) -> dict[str, str]:
    files = {"index.html": render_index(catalog)}
    groups = catalog["comparison_groups"]
    for style in catalog["styles"]:
        files[style["specimen_path"]] = render_specimen(
            style, groups[style["comparison_group"]]
        )
    return files


def build_gallery(catalog: dict[str, Any], output: Path) -> dict[str, Any]:
    files = render_files(catalog)
    for relative, content in files.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return {
        "status": "built",
        "output": str(output),
        "specimens": len(catalog["styles"]),
        "files": len(files),
        "proof_limit": catalog["proof_limit"],
    }


def check_gallery(
    catalog: dict[str, Any], catalog_path: Path, output: Path,
    relevance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors = validate_catalog(catalog, catalog_path)
    expected = render_files(catalog) if not errors else {}
    for relative, content in expected.items():
        target = output / relative
        if not target.is_file():
            errors.append(f"missing generated file: {relative}")
        elif target.read_text(encoding="utf-8") != content:
            errors.append(f"generated file differs: {relative}")
    expected_style_paths = {
        output / style["specimen_path"] for style in catalog.get("styles", [])
        if isinstance(style, dict) and isinstance(style.get("specimen_path"), str)
    }
    styles_dir = output / "styles"
    if styles_dir.is_dir():
        for path in styles_dir.glob("*.html"):
            if path not in expected_style_paths:
                errors.append(f"unexpected generated file: {path.relative_to(output)}")
    if output.is_dir():
        for path in output.rglob("*.html"):
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeError:
                errors.append(f"invalid UTF-8: {path.relative_to(output)}")
                continue
            for label, pattern in UNSAFE_HTML.items():
                if pattern.search(content):
                    errors.append(f"{label}: {path.relative_to(output)}")
    relevance_report = evaluate_relevance(catalog, relevance) if relevance else None
    if relevance_report and relevance_report["status"] != "passed":
        errors.append("relevance gate failed")
    return {
        "status": "failed" if errors else "passed",
        "errors": errors,
        "specimens": len(catalog.get("styles", [])),
        "comparison_groups": len(catalog.get("comparison_groups", {})),
        "proof_limit": catalog.get("proof_limit"),
        **({"relevance": relevance_report} if relevance_report else {}),
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("build", "check"):
        command = commands.add_parser(name)
        command.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
        command.add_argument("--output", type=Path, default=DEFAULT_ROOT)
        if name == "check":
            command.add_argument("--relevance", type=Path, default=DEFAULT_RELEVANCE)
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    search.add_argument("--type", choices=sorted(ALLOWED_TYPES))
    search.add_argument("--limit", type=int, default=5)
    relevance = commands.add_parser("relevance")
    relevance.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    relevance.add_argument("--cases", type=Path, default=DEFAULT_RELEVANCE)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        catalog = read_catalog(args.catalog)
        errors = validate_catalog(catalog, args.catalog)
        if errors:
            report = {
                "status": "failed",
                "errors": errors,
                "proof_limit": catalog.get("proof_limit"),
            }
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 1
        if args.command == "build":
            report = build_gallery(catalog, args.output)
        elif args.command == "check":
            relevance = json.loads(args.relevance.read_text(encoding="utf-8"))
            report = check_gallery(catalog, args.catalog, args.output, relevance)
        elif args.command == "search":
            if not 1 <= args.limit <= 5:
                raise CatalogError("--limit must be between 1 and 5")
            report = {
                "status": "passed",
                "query": args.query,
                "type": args.type,
                "results": search_catalog(catalog, args.query, args.type, args.limit),
                "proof_limit": catalog["proof_limit"],
            }
        else:
            relevance = json.loads(args.cases.read_text(encoding="utf-8"))
            report = evaluate_relevance(catalog, relevance)
    except CatalogError as exc:
        print(
            json.dumps(
                {"status": "failed", "errors": [str(exc)], "proof_limit": None},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] in {"passed", "built"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
