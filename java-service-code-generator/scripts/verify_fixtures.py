#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "java-service-code-generator"
GENERATOR = SKILL_DIR / "scripts" / "generate_scaffold.py"
FIXTURE_DIR = SKILL_DIR / "fixtures"
BASE_PACKAGE = "com.example.skill.codegen"


CASES = [
    {
        "name": "ddl",
        "args": ["--ddl-file", str(FIXTURE_DIR / "sample_order.sql")],
        "table": "t_sample_order",
        "class": "SampleOrder",
        "checks": {
            "impl/com/example/skill/codegen/dal/entities/SampleOrder.java": [
                '@Table(SampleOrder.TABLE_NAME)',
                'private Long id;',
                'import com.wind.transaction.core.enums.CurrencyIsoCode;',
                'private CurrencyIsoCode currency;',
                '@Column(value = "is_deleted", isLogicDelete = true)',
            ],
            "face/com/example/skill/codegen/model/request/CreateSampleOrderRequest.java": [
                "private String orderNo;",
                "private BigDecimal amount;",
                "private CurrencyIsoCode currency;",
            ],
            "face/com/example/skill/codegen/services/SampleOrderService.java": [
                "SampleOrderDTO getSampleOrderById",
            ],
            "impl/com/example/skill/codegen/services/impl/SampleOrderServiceImpl.java": [
                "sampleOrderMapper.updateSelective(entity)",
            ],
        },
        "golden_hashes": {
            "impl/com/example/skill/codegen/dal/entities/SampleOrder.java": "bf0bcefcc15aadcd026766ba3faef8722893fdb094803cefcc9046ea64eccc82",
            "impl/com/example/skill/codegen/services/impl/SampleOrderServiceImpl.java": "80a8612d1a3bfeb18acf192cad7f2fba8927618ac97813a9f58f06243ae8dbf5",
            "face/com/example/skill/codegen/services/SampleOrderService.java": "158d589e2d01d911a78665cb2232541a3002b09667049774547e8f955087853f",
        },
    },
    {
        "name": "java",
        "args": [
            "--input-file",
            str(FIXTURE_DIR / "SampleChannel.java"),
            "--input-type",
            "java",
            "--table-name",
            "t_sample_channel",
            "--table-comment",
            "示例通道",
        ],
        "table": "t_sample_channel",
        "class": "SampleChannel",
        "emit_ddl": True,
        "checks": {
            "impl/com/example/skill/codegen/dal/entities/SampleChannel.java": [
                "public class SampleChannel implements Serializable",
                "private String channelCode;",
                "private Boolean enabled;",
            ],
            "face/com/example/skill/codegen/services/SampleChannelService.java": [
                "SampleChannelDTO getSampleChannelById",
            ],
            "impl/com/example/skill/codegen/services/impl/SampleChannelServiceImpl.java": [
                "sampleChannelMapper.updateSelective(entity)",
            ],
        },
        "golden_hashes": {
            "impl/com/example/skill/codegen/dal/entities/SampleChannel.java": "a13d32ee0a7d3e3ad5cde36ee65c97cd6bb81f140339a49bfa1fa530f24fb16d",
            "impl/com/example/skill/codegen/services/mapstruct/SampleChannelConverter.java": "e21e1307512adef43d2dabdb2e01b2af7e83bbc0388328c4497ccb8eafa5c03a",
            "impl/com/example/skill/codegen/services/impl/SampleChannelServiceImpl.java": "cd968148e29b3c8f86afd89b9e56978a0af3c4596ab28f4c335461986301482d",
            "face/com/example/skill/codegen/model/query/SampleChannelQuery.java": "6ae445ced82b7eb419fab48c2b7cfe3862dad643a754df7ec25b502361b73a1e",
            "face/com/example/skill/codegen/services/SampleChannelService.java": "a3cddb82b11233b60c7374a26b0193bdfeec87121091eccefb484943acb92767",
        },
    },
    {
        "name": "table",
        "args": [
            "--input-file",
            str(FIXTURE_DIR / "sample_batch_fields.md"),
            "--input-type",
            "table",
            "--table-name",
            "t_sample_batch",
            "--table-comment",
            "示例批次",
        ],
        "table": "t_sample_batch",
        "class": "SampleBatch",
        "emit_ddl": True,
        "checks": {
            "impl/com/example/skill/codegen/dal/entities/SampleBatch.java": [
                "public class SampleBatch implements Serializable",
                "private String batchNo;",
                "private BigDecimal totalAmount;",
            ],
            "face/com/example/skill/codegen/services/SampleBatchService.java": [
                "SampleBatchDTO getSampleBatchById",
                "WindPagination<SampleBatchDTO> querySampleBatchs",
            ],
            "impl/com/example/skill/codegen/services/impl/SampleBatchServiceImpl.java": [
                "sampleBatchMapper.updateSelective(entity)",
            ],
        },
        "golden_hashes": {
            "impl/com/example/skill/codegen/dal/entities/SampleBatch.java": "595864b4760c4fff7a374d15d187bd74c45fc709874efbfded0a3aeef474735f",
            "impl/com/example/skill/codegen/services/impl/SampleBatchServiceImpl.java": "7f53987eebcfe5e980f328a16f0e6153d71ee7308f8470382ec3f28111f29d3e",
            "face/com/example/skill/codegen/services/SampleBatchService.java": "8dc393c29a193876b8aecd37bc709f905ddd56eb3ea7ec582a06ccbd953bc717",
        },
    },
]


def normalized_generated_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"@date \d{4}-\d{2}-\d{2}", "@date <DATE>", text)
    text = re.sub(r"private static final long serialVersionUID = -?\d+L;", "private static final long serialVersionUID = <SERIAL>;", text)
    return text


def generated_hash(path: Path) -> str:
    text = normalized_generated_text(path.read_text(encoding="utf-8"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_case(case: dict[str, object], base_tmp: Path) -> None:
    out = base_tmp / case["name"]
    ddl_out = base_tmp / f"{case['name']}.sql"
    cmd = [
        sys.executable,
        str(GENERATOR),
        *case["args"],
        "--base-package",
        BASE_PACKAGE,
        "--author",
        "codex",
        "--output-dir",
        str(out),
    ]
    if case.get("emit_ddl"):
        cmd.extend(["--emit-ddl", str(ddl_out)])
    subprocess.run(cmd, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    java_files = sorted(out.rglob("*.java"))
    if len(java_files) != 9:
        raise AssertionError(f"{case['name']}: expected 9 Java files, got {len(java_files)}")
    for rel, snippets in case["checks"].items():
        target = out / rel
        if not target.exists():
            raise AssertionError(f"{case['name']}: missing {rel}")
        text = target.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                raise AssertionError(f"{case['name']}: {rel} missing snippet: {snippet}")
    for rel, expected_hash in case.get("golden_hashes", {}).items():
        target = out / rel
        if not target.exists():
            raise AssertionError(f"{case['name']}: missing golden file {rel}")
        actual_hash = generated_hash(target)
        if actual_hash != expected_hash:
            raise AssertionError(f"{case['name']}: {rel} golden hash changed: {actual_hash}")
    if case.get("emit_ddl"):
        ddl = ddl_out.read_text(encoding="utf-8")
        if f"CREATE TABLE `{case['table']}`" not in ddl:
            raise AssertionError(f"{case['name']}: emitted DDL missing expected table")
    print(f"OK fixture {case['name']}")


def run_generator(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GENERATOR), *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def expect_failure(name: str, args: list[str], expected: str) -> None:
    result = run_generator(args)
    output = result.stdout + result.stderr
    if result.returncode == 0:
        raise AssertionError(f"{name}: expected command to fail")
    if expected not in output:
        raise AssertionError(f"{name}: expected error containing {expected!r}, got {output!r}")
    print(f"OK negative fixture {name}")


def create_ambiguous_module_repo(base_tmp: Path) -> Path:
    repo = base_tmp / "ambiguous-repo"
    module = repo / "multi-domain"
    for stem in ("sample-alpha", "sample-beta"):
        (module / f"{stem}-face" / "src/main/java").mkdir(parents=True)
        (module / f"{stem}-impl" / "src/main/java").mkdir(parents=True)
    return repo


def run_negative_cases(base_tmp: Path) -> None:
    overwrite_out = base_tmp / "negative-overwrite"
    overwrite_args = [
        "--ddl-file",
        str(FIXTURE_DIR / "sample_order.sql"),
        "--base-package",
        BASE_PACKAGE,
        "--author",
        "codex",
        "--output-dir",
        str(overwrite_out),
    ]
    first = run_generator(overwrite_args)
    if first.returncode != 0:
        raise AssertionError(f"overwrite guard setup failed: {first.stdout}{first.stderr}")
    expect_failure("existing file requires overwrite", overwrite_args, "exists; pass --overwrite")

    ambiguous_repo = create_ambiguous_module_repo(base_tmp)
    expect_failure(
        "ambiguous face impl module pairs",
        [
            "--ddl-file",
            str(FIXTURE_DIR / "sample_order.sql"),
            "--business-module",
            "multi-domain",
            "--repo-root",
            str(ambiguous_repo),
            "--author",
            "codex",
        ],
        "存在歧义",
    )
    expect_failure(
        "field table requires table name",
        [
            "--input-file",
            str(FIXTURE_DIR / "sample_batch_fields.md"),
            "--input-type",
            "table",
            "--base-package",
            BASE_PACKAGE,
            "--output-dir",
            str(base_tmp / "negative-missing-table"),
        ],
        "字段表格输入必须通过 --table-name",
    )


def main() -> int:
    if not GENERATOR.exists():
        raise SystemExit(f"missing generator: {GENERATOR}")
    if not FIXTURE_DIR.exists():
        raise SystemExit(f"missing fixtures: {FIXTURE_DIR}")
    base_tmp = Path(tempfile.mkdtemp(prefix="java-service-codegen-fixtures-"))
    try:
        for case in CASES:
            run_case(case, base_tmp)
        run_negative_cases(base_tmp)
    finally:
        shutil.rmtree(base_tmp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
