#!/usr/bin/env python3
"""Validate the repository's Codex agent profiles and global merge boundary."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
import tomllib


REQUIRED_FIELDS = ("name", "description", "developer_instructions")
EXPECTED_PROFILES = {
    "implementer.toml": {
        "name": "implementer",
        "model": "gpt-5.6-terra",
        "model_reasoning_effort": "high",
        "sandbox_mode": "workspace-write",
    },
    "batch-worker.toml": {
        "name": "batch_worker",
        "model": "gpt-5.6-luna",
        "model_reasoning_effort": "medium",
        "sandbox_mode": "workspace-write",
    },
}


def load_profile(path: Path) -> dict[str, object]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"{path}: invalid TOML: {exc}") from exc
    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{path}: missing or empty {field}")
    return data


def ensure_unique_names(profiles: list[tuple[Path, dict[str, object]]]) -> None:
    owners: dict[str, Path] = {}
    for path, data in profiles:
        name = str(data["name"])
        if name in owners:
            raise ValueError(f"duplicate agent name {name!r}: {owners[name]} and {path}")
        owners[name] = path


def validate(source_dir: Path, target_dir: Path | None = None) -> None:
    if not source_dir.is_dir():
        raise ValueError(f"agent source directory not found: {source_dir}")

    source_profiles = [(path, load_profile(path)) for path in sorted(source_dir.glob("*.toml"))]
    source_by_file = {path.name: (path, data) for path, data in source_profiles}
    for filename, expected in EXPECTED_PROFILES.items():
        if filename not in source_by_file:
            raise ValueError(f"required agent profile not found: {source_dir / filename}")
        path, data = source_by_file[filename]
        for field, expected_value in expected.items():
            if data.get(field) != expected_value:
                raise ValueError(
                    f"{path}: expected {field}={expected_value!r}, got {data.get(field)!r}"
                )
    ensure_unique_names(source_profiles)

    if target_dir is not None and target_dir.is_dir():
        replaced_files = set(EXPECTED_PROFILES)
        preserved_profiles = [
            (path, load_profile(path))
            for path in sorted(target_dir.glob("*.toml"))
            if path.name not in replaced_files
        ]
        ensure_unique_names(source_profiles + preserved_profiles)


def profile_text(name: str, model: str, effort: str) -> str:
    return (
        f'name = "{name}"\n'
        'description = "test"\n'
        'developer_instructions = "test"\n'
        f'model = "{model}"\n'
        f'model_reasoning_effort = "{effort}"\n'
        'sandbox_mode = "workspace-write"\n'
    )


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source"
        target = root / "target"
        source.mkdir()
        target.mkdir()
        (source / "implementer.toml").write_text(
            profile_text("implementer", "gpt-5.6-terra", "high"), encoding="utf-8"
        )
        batch_path = source / "batch-worker.toml"
        batch_path.write_text(
            profile_text("batch_worker", "gpt-5.6-luna", "medium"), encoding="utf-8"
        )
        validate(source, target)

        batch_path.write_text(
            profile_text("batch_worker", "gpt-5.6-terra", "medium"), encoding="utf-8"
        )
        try:
            validate(source, target)
        except ValueError as exc:
            assert "gpt-5.6-luna" in str(exc)
        else:
            raise AssertionError("wrong batch_worker model was accepted")

        batch_path.write_text(
            profile_text("batch_worker", "gpt-5.6-luna", "medium"), encoding="utf-8"
        )
        (target / "legacy.toml").write_text(
            'name = "batch_worker"\ndescription = "test"\ndeveloper_instructions = "test"\n',
            encoding="utf-8",
        )
        try:
            validate(source, target)
        except ValueError as exc:
            assert "duplicate agent name" in str(exc)
        else:
            raise AssertionError("duplicate target agent name was accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--target-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            print("OK Codex agent profile validator self-test")
            return 0
        if args.source_dir is None:
            parser.error("--source-dir is required unless --self-test is used")
        validate(args.source_dir, args.target_dir)
    except (AssertionError, ValueError) as exc:
        print(f"FAIL {exc}")
        return 1
    print(f"OK Codex agent profiles: {args.source_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
