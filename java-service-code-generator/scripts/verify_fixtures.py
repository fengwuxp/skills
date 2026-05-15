#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "java-service-code-generator"
GENERATOR = SKILL_DIR / "scripts" / "generate_scaffold.py"
FIXTURE_DIR = SKILL_DIR / "fixtures"


CASES = [
    {
        "name": "ddl",
        "args": ["--ddl-file", str(FIXTURE_DIR / "payment_order.sql")],
        "table": "t_payment_order",
        "class": "PaymentOrder",
        "checks": {
            "impl/com/capte/nobe/payment/dal/entities/PaymentOrder.java": [
                '@Table(PaymentOrder.TABLE_NAME)',
                'private Long id;',
                '@Column(value = "is_deleted", isLogicDelete = true)',
            ],
            "face/com/capte/nobe/payment/model/request/CreatePaymentOrderRequest.java": [
                "private String orderNo;",
                "private BigDecimal amount;",
            ],
        },
    },
    {
        "name": "java",
        "args": [
            "--input-file",
            str(FIXTURE_DIR / "PaymentChannel.java"),
            "--input-type",
            "java",
            "--table-name",
            "t_payment_channel",
            "--table-comment",
            "支付通道",
        ],
        "table": "t_payment_channel",
        "class": "PaymentChannel",
        "emit_ddl": True,
        "checks": {
            "impl/com/capte/nobe/payment/dal/entities/PaymentChannel.java": [
                "public class PaymentChannel implements Serializable",
                "private String channelCode;",
                "private Boolean enabled;",
            ],
        },
    },
    {
        "name": "table",
        "args": [
            "--input-file",
            str(FIXTURE_DIR / "settlement_batch_fields.md"),
            "--input-type",
            "table",
            "--table-name",
            "t_settlement_batch",
            "--table-comment",
            "结算批次",
        ],
        "table": "t_settlement_batch",
        "class": "SettlementBatch",
        "emit_ddl": True,
        "checks": {
            "impl/com/capte/nobe/payment/dal/entities/SettlementBatch.java": [
                "public class SettlementBatch implements Serializable",
                "private String batchNo;",
                "private BigDecimal totalAmount;",
            ],
            "face/com/capte/nobe/payment/services/SettlementBatchService.java": [
                "WindPagination<SettlementBatchDTO> querySettlementBatchs",
            ],
        },
    },
]


def run_case(case: dict[str, object], base_tmp: Path) -> None:
    out = base_tmp / case["name"]
    ddl_out = base_tmp / f"{case['name']}.sql"
    cmd = [
        sys.executable,
        str(GENERATOR),
        *case["args"],
        "--base-package",
        "com.capte.nobe.payment",
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
    if case.get("emit_ddl"):
        ddl = ddl_out.read_text(encoding="utf-8")
        if f"CREATE TABLE `{case['table']}`" not in ddl:
            raise AssertionError(f"{case['name']}: emitted DDL missing expected table")
    print(f"OK fixture {case['name']}")


def main() -> int:
    if not GENERATOR.exists():
        raise SystemExit(f"missing generator: {GENERATOR}")
    if not FIXTURE_DIR.exists():
        raise SystemExit(f"missing fixtures: {FIXTURE_DIR}")
    base_tmp = Path(tempfile.mkdtemp(prefix="java-service-codegen-fixtures-"))
    try:
        for case in CASES:
            run_case(case, base_tmp)
    finally:
        shutil.rmtree(base_tmp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
