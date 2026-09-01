#!/usr/bin/env python3
"""Maintain an explicit, offline review queue for one learning topic.

Inputs: CLI arguments and an optional JSON file passed with ``--file``.
Outputs: JSON on stdout.
Writes: only the declared ``--file`` path for ``add`` and ``grade``.
Network: never accessed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Sequence


VERSION = 1


def _required_text(value: str, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be non-empty")
    text = value.strip()
    if not text:
        raise ValueError(f"{label} must be non-empty")
    return text


def _date(value: str, label: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be YYYY-MM-DD") from exc


def _validate_state(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or data.get("version") != VERSION:
        raise ValueError(f"state must be an object with version={VERSION}")
    if not isinstance(data.get("topic"), str) or not isinstance(data.get("items"), list):
        raise ValueError("state must contain string topic and list items")
    seen_ids: set[int] = set()
    for index, item in enumerate(data["items"]):
        label = f"items[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{label} must be an object")
        item_id = item.get("id")
        if not isinstance(item_id, int) or isinstance(item_id, bool) or item_id <= 0:
            raise ValueError(f"{label}.id must be a positive integer")
        if item_id in seen_ids:
            raise ValueError(f"{label}.id must be unique")
        seen_ids.add(item_id)
        for field in ("question", "gap", "answer_ref"):
            _required_text(item.get(field), f"{label}.{field}")
        _date(item.get("due"), f"{label}.due")
        lapses = item.get("lapses")
        if not isinstance(lapses, int) or isinstance(lapses, bool) or lapses < 0:
            raise ValueError(f"{label}.lapses must be a non-negative integer")
        if not isinstance(item.get("history"), list):
            raise ValueError(f"{label}.history must be a list")
    return data


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": VERSION, "topic": "", "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON state: {path}") from exc
    return _validate_state(data)


def save_state(path: Path, data: dict[str, Any]) -> None:
    _validate_state(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def add_item(
    state: dict[str, Any],
    *,
    topic: str,
    question: str,
    gap: str,
    answer_ref: str,
    due: str,
) -> dict[str, Any]:
    _validate_state(state)
    topic = _required_text(topic, "topic")
    if state["topic"] and state["topic"] != topic:
        raise ValueError(f"topic mismatch: state={state['topic']!r} input={topic!r}")
    state["topic"] = topic
    item = {
        "id": max((int(item.get("id", 0)) for item in state["items"]), default=0) + 1,
        "question": _required_text(question, "question"),
        "gap": _required_text(gap, "gap"),
        "answer_ref": _required_text(answer_ref, "answer_ref"),
        "due": _date(due, "due"),
        "lapses": 0,
        "history": [],
    }
    state["items"].append(item)
    return item


def due_items(state: dict[str, Any], *, on: str) -> list[dict[str, Any]]:
    _validate_state(state)
    current = _date(on, "on")
    return sorted(
        (item for item in state["items"] if _date(item.get("due", ""), "item due") <= current),
        key=lambda item: (item["due"], item["id"]),
    )


def grade_item(
    state: dict[str, Any],
    *,
    item_id: int,
    result: str,
    on: str,
    next_due: str,
    note: str = "",
) -> dict[str, Any]:
    _validate_state(state)
    result = result.strip().lower()
    if result not in {"pass", "fail"}:
        raise ValueError("result must be pass or fail")
    reviewed_on = _date(on, "on")
    scheduled_for = _date(next_due, "next_due")
    if scheduled_for <= reviewed_on:
        raise ValueError("next_due must be after on")
    item = next((row for row in state["items"] if row.get("id") == item_id), None)
    if item is None:
        raise ValueError(f"unknown item id: {item_id}")
    clean_note = note.strip()
    item.setdefault("history", []).append(
        {"date": reviewed_on, "result": result, "note": clean_note}
    )
    if result == "fail":
        item["lapses"] = int(item.get("lapses", 0)) + 1
        if clean_note:
            item["gap"] = clean_note
    item["due"] = scheduled_for
    return item


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="add a question from an observed knowledge gap")
    add.add_argument("--file", type=Path, required=True)
    add.add_argument("--topic", required=True)
    add.add_argument("--question", required=True)
    add.add_argument("--gap", required=True)
    add.add_argument("--answer-ref", required=True)
    add.add_argument("--due", required=True)

    due = subparsers.add_parser("due", help="list questions due on or before a date")
    due.add_argument("--file", type=Path, required=True)
    due.add_argument("--on", required=True)

    grade = subparsers.add_parser("grade", help="record a result and explicit next date")
    grade.add_argument("--file", type=Path, required=True)
    grade.add_argument("--id", type=int, required=True)
    grade.add_argument("--result", choices=("pass", "fail"), required=True)
    grade.add_argument("--on", required=True)
    grade.add_argument("--next-due", required=True)
    grade.add_argument("--note", default="")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        state = load_state(args.file)
        if args.command == "add":
            payload = add_item(
                state,
                topic=args.topic,
                question=args.question,
                gap=args.gap,
                answer_ref=args.answer_ref,
                due=args.due,
            )
            save_state(args.file, state)
        elif args.command == "due":
            payload = due_items(state, on=args.on)
        else:
            payload = grade_item(
                state,
                item_id=args.id,
                result=args.result,
                on=args.on,
                next_due=args.next_due,
                note=args.note,
            )
            save_state(args.file, state)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
