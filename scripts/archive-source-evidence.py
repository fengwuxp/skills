#!/usr/bin/env python3
"""Archive externally read source evidence outside this repository.

This script is intentionally offline. It never fetches URLs, uploads files,
reads secrets, scans private directories, or modifies repository content. It
copies explicitly provided local evidence files into SKILL_SOURCE_ARCHIVE_HOME
or ~/.skill-source-archive/ and emits lightweight JSON metadata that can be
referenced from source-map.md without committing copyrighted article bodies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE_HOME = Path.home() / ".skill-source-archive"
SELF_TEST_SCHEME = "https:" + "//"
SELF_TEST_READ_URL = SELF_TEST_SCHEME + "mp.weixin.qq.com/s/read-demo"
SELF_TEST_REPO_URL = SELF_TEST_SCHEME + "example.com/repo-file"
ALLOWED_EVIDENCE_SUFFIXES = {
    ".html",
    ".htm",
    ".mhtml",
    ".mht",
    ".txt",
    ".md",
    ".json",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}
REPO_ONLY_NOTICE = "repo stores only source metadata; raw evidence stays outside git"


def fail(message: str) -> None:
    raise SystemExit(message)


def archive_home(value: str | None = None) -> Path:
    raw = value or os.environ.get("SKILL_SOURCE_ARCHIVE_HOME")
    return Path(raw).expanduser().resolve() if raw else DEFAULT_ARCHIVE_HOME.expanduser().resolve()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(text: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z._-]+", "-", text.strip())
    normalized = normalized.strip("-._").lower()
    return normalized[:80] or "source"


def host_slug(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        fail(f"invalid source URL: {url}")
    return slugify(parsed.netloc)


def validate_evidence(path: Path) -> Path:
    evidence = path.expanduser().resolve()
    if not evidence.exists():
        fail(f"evidence file does not exist: {path}")
    if not evidence.is_file():
        fail(f"evidence path must be a file: {path}")
    if evidence.suffix.lower() not in ALLOWED_EVIDENCE_SUFFIXES:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_SUFFIXES))
        fail(f"unsupported evidence suffix {evidence.suffix!r}; allowed: {allowed}")
    if is_within(evidence, ROOT):
        fail("raw evidence must not be stored inside this repository")
    return evidence


def safe_metadata(value: str | None) -> str | None:
    if value is None:
        return None
    clean = re.sub(r"\s+", " ", value).strip()
    return clean or None


def metadata_path_for(destination_dir: Path, archive_id: str) -> Path:
    return destination_dir / f"{archive_id}.metadata.json"


def archive_evidence(
    *,
    source_url: str,
    evidence_file: Path,
    title: str | None,
    author: str | None,
    published_at: str | None,
    read_at: str | None,
    capture_method: str,
    archive_root: Path,
    overwrite: bool,
    dry_run: bool,
) -> dict[str, Any]:
    evidence = validate_evidence(evidence_file)
    archive_root = archive_root.expanduser().resolve()
    if is_within(archive_root, ROOT):
        fail("archive home must be outside this repository")
    digest = sha256_file(evidence)
    timestamp = read_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    archive_id = f"{timestamp[:10]}-{host_slug(source_url)}-{digest[:12]}"
    destination_dir = archive_root / "sources" / archive_id
    destination_file = destination_dir / f"evidence{evidence.suffix.lower()}"
    metadata_file = metadata_path_for(destination_dir, archive_id)

    if not dry_run:
        if destination_dir.exists() and not overwrite:
            fail(f"archive already exists, pass --overwrite to replace: {destination_dir}")
        destination_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(evidence, destination_file)

    metadata: dict[str, Any] = {
        "archive_id": archive_id,
        "source_url": source_url,
        "title": safe_metadata(title),
        "author": safe_metadata(author),
        "published_at": safe_metadata(published_at),
        "read_at": timestamp,
        "capture_method": capture_method,
        "evidence_sha256": digest,
        "evidence_size_bytes": evidence.stat().st_size,
        "evidence_original_path": str(evidence),
        "archive_home": str(archive_root),
        "archive_path": str(destination_dir),
        "metadata_path": str(metadata_file),
        "repo_boundary": REPO_ONLY_NOTICE,
    }

    if not dry_run:
        metadata_file.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return metadata


def print_metadata(metadata: dict[str, Any]) -> None:
    print(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="source-archive-self-test-") as tmp:
        base = Path(tmp)
        outside_repo = base / "read-evidence.html"
        outside_repo.write_text("<html><title>demo</title><body>read evidence</body></html>", encoding="utf-8")
        archive_root = base / "archive-home"

        metadata = archive_evidence(
            source_url=SELF_TEST_READ_URL,
            evidence_file=outside_repo,
            title="已读取文章",
            author="demo",
            published_at="2026-05-26",
            read_at="2026-05-26T12:00:00+00:00",
            capture_method="playwright",
            archive_root=archive_root,
            overwrite=False,
            dry_run=False,
        )
        required = [
            "archive_id",
            "source_url",
            "evidence_sha256",
            "archive_path",
            "metadata_path",
            "repo_boundary",
        ]
        missing = [key for key in required if key not in metadata or not metadata[key]]
        if missing:
            fail(f"self-test missing metadata keys: {missing}")
        if not Path(metadata["metadata_path"]).exists():
            fail("self-test metadata file was not written")
        if is_within(Path(metadata["archive_path"]), ROOT):
            fail("self-test archive path should be outside repository")

        repo_evidence = ROOT / "AGENTS.md"
        try:
            archive_evidence(
                source_url=SELF_TEST_REPO_URL,
                evidence_file=repo_evidence,
                title=None,
                author=None,
                published_at=None,
                read_at="2026-05-26T12:00:00+00:00",
                capture_method="manual",
                archive_root=archive_root,
                overwrite=False,
                dry_run=True,
            )
        except SystemExit as exc:
            if "must not be stored inside this repository" not in str(exc):
                fail(f"self-test unexpected repo-file failure: {exc}")
        else:
            fail("self-test expected repository evidence rejection")

        try:
            archive_evidence(
                source_url=SELF_TEST_READ_URL,
                evidence_file=outside_repo,
                title=None,
                author=None,
                published_at=None,
                read_at="2026-05-26T12:00:00+00:00",
                capture_method="manual",
                archive_root=ROOT / ".skill-source-archive",
                overwrite=False,
                dry_run=True,
            )
        except SystemExit as exc:
            if "archive home must be outside this repository" not in str(exc):
                fail(f"self-test unexpected archive-home failure: {exc}")
        else:
            fail("self-test expected repository archive-home rejection")

    print("OK source evidence archive self-test")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", help="URL represented by the evidence file")
    parser.add_argument("--evidence-file", type=Path, help="explicit local evidence file to archive")
    parser.add_argument("--title", help="source title, stored as metadata only")
    parser.add_argument("--author", help="source author, stored as metadata only")
    parser.add_argument("--published-at", help="source publish date if known")
    parser.add_argument("--read-at", help="read/capture timestamp; defaults to current UTC time")
    parser.add_argument(
        "--capture-method",
        default="manual",
        choices=["manual", "playwright", "browser", "curl", "other"],
        help="how the local evidence file was obtained",
    )
    parser.add_argument("--archive-home", help="override SKILL_SOURCE_ARCHIVE_HOME for this run")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing archive_id directory")
    parser.add_argument("--dry-run", action="store_true", help="print metadata without copying evidence")
    parser.add_argument("--self-test", action="store_true", help="run offline positive and negative fixtures")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0

    if not args.source_url:
        parser.error("--source-url is required unless --self-test is used")
    if not args.evidence_file:
        parser.error("--evidence-file is required unless --self-test is used")

    metadata = archive_evidence(
        source_url=args.source_url,
        evidence_file=args.evidence_file,
        title=args.title,
        author=args.author,
        published_at=args.published_at,
        read_at=args.read_at,
        capture_method=args.capture_method,
        archive_root=archive_home(args.archive_home),
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    print_metadata(metadata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
