#!/usr/bin/env python3
"""Validate a Markdown logical timeline for a fiction project.

Input: an explicit project root and one timeline Markdown file inside it.
Output: a local structural/readiness summary or validation errors.
Writes/network: none.
Authority paths: bare paths use the project root; dot-relative paths and Markdown links use the timeline directory.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


REQUIRED_COLUMNS = (
    "Event ID",
    "Authority",
    "Canon Status",
    "Record Status",
    "Open Fields",
    "T Anchor",
    "Line Role",
    "Time Relation",
    "Depends On",
    "Interface",
    "State Delta",
    "P Anchor",
)
NATURAL_DURATION_COLUMN = "Natural Duration"
TIME_AXIS_DECLARATION = re.compile(
    r"^[ \t]*Time Axis:[ \t]*(?:`(?P<quoted>[A-Za-z0-9][A-Za-z0-9._-]{0,63})`|"
    r"(?P<plain>[A-Za-z0-9][A-Za-z0-9._-]{0,63}))[ \t]*$",
    re.MULTILINE,
)
EVENT_ID = re.compile(r"EV-[0-9]{3,}")
T_ANCHOR = re.compile(
    r"T(?P<start>[0-9]{3,})(?:~(?P<end>[0-9]{3,}))?\."
    r"(?P<line>[0-9]{2})\.(?P<local>[0-9]{3})"
)
P_ANCHORS = re.compile(r"P[0-9]{3,}(?:\s*,\s*P[0-9]{3,})*")
RELATION = re.compile(
    r"(?:same-window|unknown-order|overlap:EV-[0-9]{3,}|exact-sync:EV-[0-9]{3,})"
)
MARKDOWN_HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
CANON_STATUSES = {"confirmed", "candidate", "pending", "retired"}
RECORD_STATUSES = {"aligned", "pending-writeback", "conflict"}
LINE_ROLES = {"main", "side", "global"}
EMPTY_VALUES = {"", "-"}


@dataclass(frozen=True)
class Anchor:
    start: int
    end: int
    line: int
    local: int


@dataclass(frozen=True)
class Event:
    event_id: str
    authority: str
    canon_status: str
    record_status: str
    open_fields: str
    t_anchor: str
    anchor: Anchor
    line_role: str
    relation: str
    dependencies: tuple[str, ...]
    interface: str
    state_delta: str
    natural_duration: str | None
    line_number: int


def clean_cell(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        return value[1:-1].strip()
    return value


def split_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [clean_cell(cell) for cell in stripped[1:-1].split("|")]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_anchor(value: str) -> Anchor | None:
    match = T_ANCHOR.fullmatch(value)
    if not match:
        return None
    start = int(match.group("start"))
    end = int(match.group("end") or start)
    if end < start:
        return None
    return Anchor(start, end, int(match.group("line")), int(match.group("local")))


def parse_time_axis(text: str, relative: Path) -> tuple[str | None, list[str]]:
    matches = [match.group("quoted") or match.group("plain") for match in TIME_AXIS_DECLARATION.finditer(text)]
    if not matches:
        return None, [f"exactly one Time Axis declaration is required in {relative}"]
    if len(matches) > 1:
        return None, [f"multiple Time Axis declarations found in {relative}"]
    return matches[0], []


def local_authority_target(value: str) -> tuple[str, str, bool] | None:
    markdown_link = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", value)
    target = markdown_link.group(1) if markdown_link else value
    path, separator, fragment = target.partition("#")
    path = unquote(path.strip())
    if not path.lower().endswith(".md"):
        return None
    return path, unquote(fragment.strip()) if separator else "", markdown_link is not None


def heading_key(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def markdown_heading_keys(path: Path) -> set[str]:
    return {
        heading_key(match.group(1))
        for line in path.read_text(encoding="utf-8").splitlines()
        if (match := MARKDOWN_HEADING.fullmatch(line))
    }


def parse_events(text: str, relative: Path) -> tuple[list[Event], list[str]]:
    lines = text.splitlines()
    errors: list[str] = []
    header_index: int | None = None
    columns: dict[str, int] = {}
    natural_duration_position: int | None = None

    for index, line in enumerate(lines):
        cells = split_table_row(line)
        if cells and all(column in cells for column in REQUIRED_COLUMNS):
            header_index = index
            columns = {column: cells.index(column) for column in REQUIRED_COLUMNS}
            if NATURAL_DURATION_COLUMN in cells:
                natural_duration_position = cells.index(NATURAL_DURATION_COLUMN)
            break

    if header_index is None:
        return [], [f"timeline table with required columns not found in {relative}"]

    events: list[Event] = []
    for index in range(header_index + 1, len(lines)):
        cells = split_table_row(lines[index])
        if cells is None:
            if lines[index].strip() and events:
                break
            continue
        if is_separator(cells):
            continue
        line_number = index + 1
        required_position = max(columns.values())
        if natural_duration_position is not None:
            required_position = max(required_position, natural_duration_position)
        if len(cells) <= required_position:
            errors.append(f"incomplete timeline row at {relative}:{line_number}")
            continue

        values = {column: cells[position] for column, position in columns.items()}
        event_id = values["Event ID"]
        anchor_text = values["T Anchor"]
        anchor = parse_anchor(anchor_text)

        if not EVENT_ID.fullmatch(event_id):
            errors.append(f"invalid event ID {event_id!r} at {relative}:{line_number}")
        if anchor is None:
            errors.append(f"invalid T anchor {anchor_text!r} at {relative}:{line_number}")
            continue
        if values["Canon Status"] not in CANON_STATUSES:
            errors.append(
                f"invalid canon status {values['Canon Status']!r} at {relative}:{line_number}"
            )
        if values["Record Status"] not in RECORD_STATUSES:
            errors.append(
                f"invalid record status {values['Record Status']!r} at {relative}:{line_number}"
            )
        if values["Line Role"] not in LINE_ROLES:
            errors.append(
                f"invalid line role {values['Line Role']!r} at {relative}:{line_number}"
            )
        elif anchor.line == 0 and values["Line Role"] != "global":
            errors.append(f"line 00 must use role global at {relative}:{line_number}")
        elif anchor.line != 0 and values["Line Role"] == "global":
            errors.append(
                f"line {anchor.line:02d} cannot use role global at {relative}:{line_number}"
            )
        if not RELATION.fullmatch(values["Time Relation"]):
            errors.append(
                f"invalid time relation {values['Time Relation']!r} at {relative}:{line_number}"
            )
        if values["P Anchor"] not in EMPTY_VALUES and not P_ANCHORS.fullmatch(
            values["P Anchor"]
        ):
            errors.append(f"invalid P anchor {values['P Anchor']!r} at {relative}:{line_number}")
        if values["Canon Status"] == "confirmed" and values["Authority"] in EMPTY_VALUES:
            errors.append(f"confirmed event {event_id} has no authority at {relative}:{line_number}")
        if values["State Delta"] in EMPTY_VALUES:
            errors.append(f"event {event_id} has no state delta at {relative}:{line_number}")

        dependencies = tuple(
            dependency.strip()
            for dependency in values["Depends On"].split(",")
            if dependency.strip() not in EMPTY_VALUES
        )
        events.append(
            Event(
                event_id=event_id,
                authority=values["Authority"],
                canon_status=values["Canon Status"],
                record_status=values["Record Status"],
                open_fields=values["Open Fields"],
                t_anchor=anchor_text,
                anchor=anchor,
                line_role=values["Line Role"],
                relation=values["Time Relation"],
                dependencies=dependencies,
                interface=values["Interface"],
                state_delta=values["State Delta"],
                natural_duration=(
                    cells[natural_duration_position]
                    if natural_duration_position is not None
                    else None
                ),
                line_number=line_number,
            )
        )

    if not events:
        errors.append(f"no timeline events found in {relative}")
    return events, errors


def has_cycle(events: dict[str, Event]) -> bool:
    state: dict[str, int] = {}

    def visit(event_id: str) -> bool:
        if state.get(event_id) == 1:
            return True
        if state.get(event_id) == 2:
            return False
        state[event_id] = 1
        for dependency in events[event_id].dependencies:
            if dependency in events and visit(dependency):
                return True
        state[event_id] = 2
        return False

    return any(visit(event_id) for event_id in events if event_id not in state)


def count_parallel_groups(events: list[Event], by_id: dict[str, Event]) -> int:
    neighbors: dict[str, set[str]] = defaultdict(set)

    def link(left: Event, right: Event) -> None:
        if left.anchor.line == 0 or right.anchor.line == 0 or left.anchor.line == right.anchor.line:
            return
        neighbors[left.event_id].add(right.event_id)
        neighbors[right.event_id].add(left.event_id)

    by_window: dict[tuple[int, int], list[Event]] = defaultdict(list)
    for event in events:
        if event.anchor.line != 0:
            by_window[(event.anchor.start, event.anchor.end)].append(event)
    for window_events in by_window.values():
        for event in window_events[1:]:
            link(window_events[0], event)

    for event in events:
        relation_type, separator, related_id = event.relation.partition(":")
        if separator and relation_type in {"overlap", "exact-sync"}:
            link(event, by_id[related_id])

    groups = 0
    visited: set[str] = set()
    for event_id in neighbors:
        if event_id in visited:
            continue
        groups += 1
        pending = [event_id]
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            pending.extend(neighbors[current] - visited)
    return groups


def check(
    root: Path,
    timeline: Path,
    require_ready: bool = False,
    ready_events: tuple[str, ...] = (),
) -> list[str]:
    root = root.resolve(strict=True)
    timeline = timeline.resolve(strict=True)
    relative = timeline.relative_to(root)
    text = timeline.read_text(encoding="utf-8")
    time_axis, errors = parse_time_axis(text, relative)
    events, parse_errors = parse_events(text, relative)
    errors.extend(parse_errors)

    by_id: dict[str, Event] = {}
    anchors: dict[str, Event] = {}
    authority_headings: dict[Path, set[str]] = {}
    previous_global = -1
    previous_local: dict[int, int] = {}

    for event in events:
        if event.event_id in by_id:
            errors.append(
                f"duplicate event ID {event.event_id}: {relative}:"
                f"{by_id[event.event_id].line_number} and {event.line_number}"
            )
        else:
            by_id[event.event_id] = event
        if event.t_anchor in anchors:
            errors.append(
                f"duplicate T anchor {event.t_anchor}: {relative}:"
                f"{anchors[event.t_anchor].line_number} and {event.line_number}"
            )
        else:
            anchors[event.t_anchor] = event
        if event.anchor.start < previous_global:
            errors.append(f"T anchor order decreases at {relative}:{event.line_number}")
        previous_global = max(previous_global, event.anchor.start)
        if event.anchor.line in previous_local and event.anchor.local <= previous_local[event.anchor.line]:
            errors.append(
                f"line {event.anchor.line:02d} local order does not increase at "
                f"{relative}:{event.line_number}"
            )
        previous_local[event.anchor.line] = event.anchor.local

        authority_target = local_authority_target(event.authority)
        if authority_target is not None:
            authority_path, authority_fragment, is_markdown_link = authority_target
            candidate = Path(authority_path)
            if candidate.is_absolute():
                errors.append(
                    f"authority path must stay under project root for {event.event_id} at "
                    f"{relative}:{event.line_number}"
                )
                continue
            is_document_relative = is_markdown_link or authority_path.startswith(("./", "../"))
            base = timeline.parent if is_document_relative else root
            resolved = (base / candidate).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(
                    f"authority path must stay under project root for {event.event_id} at "
                    f"{relative}:{event.line_number}"
                )
            else:
                if not resolved.is_file():
                    errors.append(
                        f"authority path does not exist for {event.event_id}: "
                        f"{authority_path} at {relative}:{event.line_number}"
                    )
                elif authority_fragment:
                    headings = authority_headings.get(resolved)
                    if headings is None:
                        headings = markdown_heading_keys(resolved)
                        authority_headings[resolved] = headings
                    if heading_key(authority_fragment) not in headings:
                        errors.append(
                            f"authority heading does not exist for {event.event_id}: "
                            f"{authority_path}#{authority_fragment} at "
                            f"{relative}:{event.line_number}"
                        )

    cross_line_events: set[str] = set()
    for event in events:
        for dependency_id in event.dependencies:
            dependency = by_id.get(dependency_id)
            if dependency is None:
                errors.append(
                    f"unresolved dependency {dependency_id} for {event.event_id} at "
                    f"{relative}:{event.line_number}"
                )
                continue
            if dependency.anchor.end > event.anchor.start:
                errors.append(
                    f"dependency {dependency_id} occurs after {event.event_id} at "
                    f"{relative}:{event.line_number}"
                )
            if dependency.anchor.line == event.anchor.line:
                if dependency.anchor.local >= event.anchor.local:
                    errors.append(
                        f"dependency {dependency_id} is not earlier on line "
                        f"{event.anchor.line:02d} at {relative}:{event.line_number}"
                    )
            else:
                cross_line_events.add(event.event_id)
                if event.interface in EMPTY_VALUES:
                    errors.append(
                        f"cross-line dependency {dependency_id} -> {event.event_id} "
                        f"has no interface at {relative}:{event.line_number}"
                    )

        relation_type, separator, related_id = event.relation.partition(":")
        if separator:
            if related_id == event.event_id:
                errors.append(
                    f"time relation {event.relation} cannot reference itself at "
                    f"{relative}:{event.line_number}"
                )
                continue
            related = by_id.get(related_id)
            if related is None:
                errors.append(
                    f"unresolved time relation {related_id} for {event.event_id} at "
                    f"{relative}:{event.line_number}"
                )
            else:
                if related.anchor.line != event.anchor.line:
                    if event.interface not in EMPTY_VALUES:
                        cross_line_events.add(event.event_id)
                if relation_type == "overlap" and max(
                    event.anchor.start, related.anchor.start
                ) > min(event.anchor.end, related.anchor.end):
                    errors.append(
                        f"non-overlapping anchors for {event.relation} at "
                        f"{relative}:{event.line_number}"
                    )
                elif relation_type == "exact-sync" and not (
                    event.anchor.start
                    == event.anchor.end
                    == related.anchor.start
                    == related.anchor.end
                ):
                    errors.append(
                        f"exact-sync requires one shared global point at "
                        f"{relative}:{event.line_number}"
                    )

    if by_id and has_cycle(by_id):
        errors.append("timeline dependencies contain a cycle")

    if ready_events and not require_ready:
        errors.append("ready events require --require-ready")

    duplicate_ready_ids = sorted(
        event_id for event_id in set(ready_events) if ready_events.count(event_id) > 1
    )
    for event_id in duplicate_ready_ids:
        errors.append(f"duplicate ready event ID {event_id}")

    explicit_ready_ids: set[str] = set()
    if require_ready:
        if ready_events:
            for event_id in ready_events:
                if not EVENT_ID.fullmatch(event_id):
                    errors.append(f"invalid ready event ID {event_id!r}")
                elif event_id not in by_id:
                    errors.append(f"ready event {event_id} does not exist")
                else:
                    explicit_ready_ids.add(event_id)
        else:
            explicit_ready_ids = {
                event.event_id for event in events if event.canon_status != "retired"
            }

    dependency_ready_ids: set[str] = set()
    if ready_events:
        pending = list(explicit_ready_ids)
        visited = set(explicit_ready_ids)
        while pending:
            current = by_id[pending.pop()]
            for dependency_id in current.dependencies:
                if dependency_id not in by_id or dependency_id in visited:
                    continue
                visited.add(dependency_id)
                dependency_ready_ids.add(dependency_id)
                pending.append(dependency_id)

    for event_id in sorted(explicit_ready_ids):
        event = by_id[event_id]
        if event.canon_status == "retired":
            errors.append(f"ready event {event_id} is retired")
            continue
        if event.canon_status != "confirmed":
            errors.append(f"{event.event_id} canon status is {event.canon_status}")
        if event.record_status != "aligned":
            errors.append(f"{event.event_id} record status is {event.record_status}")
        if any(
            field.strip().startswith("blocker:")
            for field in event.open_fields.split(",")
        ):
            errors.append(f"{event.event_id} has open blocker: {event.open_fields}")
        if event.natural_duration is not None and event.natural_duration in EMPTY_VALUES:
            errors.append(f"{event.event_id} has empty Natural Duration")

    for event_id in sorted(dependency_ready_ids - explicit_ready_ids):
        event = by_id[event_id]
        if event.canon_status != "confirmed":
            errors.append(
                f"ready dependency {event.event_id} canon status is {event.canon_status}"
            )
        if event.record_status != "aligned":
            errors.append(
                f"ready dependency {event.event_id} record status is {event.record_status}"
            )

    if not errors:
        parallel_groups = count_parallel_groups(events, by_id)
        interface_count = len(cross_line_events)
        interface_word = "interface" if interface_count == 1 else "interfaces"
        print(
            f"OK timeline {time_axis}: {len(events)} events, {parallel_groups} parallel groups, "
            f"{interface_count} cross-line {interface_word}"
        )
        if require_ready and ready_events:
            print(
                f"OK readiness scope: {len(explicit_ready_ids)} explicit events, "
                f"{len(dependency_ready_ids - explicit_ready_ids)} dependencies"
            )
    return errors


def parse_ready_event_ids(value: str) -> tuple[str, ...]:
    event_ids = tuple(part.strip() for part in value.split(","))
    if not event_ids or any(not event_id for event_id in event_ids):
        raise argparse.ArgumentTypeError("expected a comma-separated list of event IDs")
    invalid = [event_id for event_id in event_ids if not EVENT_ID.fullmatch(event_id)]
    if invalid:
        raise argparse.ArgumentTypeError(f"invalid event ID: {invalid[0]}")
    duplicates = sorted(event_id for event_id in set(event_ids) if event_ids.count(event_id) > 1)
    if duplicates:
        raise argparse.ArgumentTypeError(f"duplicate event ID: {duplicates[0]}")
    return event_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check one declared Time Axis, logical anchors, authority state, dependencies, and parallel scenes."
    )
    parser.add_argument("--root", type=Path, required=True, help="fiction project root")
    parser.add_argument(
        "--timeline", type=Path, required=True, help="timeline Markdown path relative to root"
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help=(
            "also require every parsed active row to be confirmed, aligned, and free of "
            "declared blockers; this does not prove prose readiness"
        ),
    )
    parser.add_argument(
        "--ready-events",
        type=parse_ready_event_ids,
        help=(
            "comma-separated event IDs whose blocker readiness should be checked; the full "
            "table is still structurally validated and upstream dependencies must remain "
            "confirmed and aligned; requires --require-ready"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    timeline = (root / args.timeline).resolve()

    if not root.is_dir():
        print(f"FAIL project root is not a directory: {root}", file=sys.stderr)
        return 1
    try:
        timeline.relative_to(root)
    except ValueError:
        print(f"FAIL timeline is outside project root: {timeline}", file=sys.stderr)
        return 1
    if timeline.suffix.lower() != ".md" or not timeline.is_file():
        print(f"FAIL timeline is not a Markdown file: {timeline}", file=sys.stderr)
        return 1
    if args.ready_events and not args.require_ready:
        print("FAIL --ready-events requires --require-ready", file=sys.stderr)
        return 1

    try:
        errors = check(
            root,
            timeline,
            require_ready=args.require_ready,
            ready_events=args.ready_events or (),
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"FAIL cannot read timeline: {error}", file=sys.stderr)
        return 1

    for error in errors:
        print(f"FAIL {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
