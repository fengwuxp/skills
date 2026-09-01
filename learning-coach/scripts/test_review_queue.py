from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("review_queue.py")
SPEC = importlib.util.spec_from_file_location("learning_coach_review_queue", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ReviewQueueTests(unittest.TestCase):
    def test_load_missing_file_returns_empty_versioned_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state = MODULE.load_state(Path(temp_dir) / "progress.json")

        self.assertEqual({"version": 1, "topic": "", "items": []}, state)

    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "progress.json"
            expected = {"version": 1, "topic": "RAG", "items": []}

            MODULE.save_state(path, expected)

            self.assertEqual(expected, MODULE.load_state(path))

    def test_load_rejects_a_malformed_item_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "progress.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "topic": "RAG",
                        "items": [
                            {
                                "id": 1,
                                "question": "问题",
                                "gap": "缺口",
                                "answer_ref": "checkpoint.md#1",
                                "due": "2026-09-02",
                                "lapses": 0,
                                "history": {},
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, r"items\[0\]"):
                MODULE.load_state(path)

    def test_add_item_requires_a_real_gap_and_explicit_due_date(self) -> None:
        state = {"version": 1, "topic": "", "items": []}

        with self.assertRaisesRegex(ValueError, "gap"):
            MODULE.add_item(
                state,
                topic="RAG",
                question="准备阶段包括什么？",
                gap=" ",
                answer_ref="checkpoints/rag.md#prepare",
                due="2026-09-02",
            )

        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            MODULE.add_item(
                state,
                topic="RAG",
                question="准备阶段包括什么？",
                gap="混淆了准备阶段和提问阶段",
                answer_ref="checkpoints/rag.md#prepare",
                due="tomorrow",
            )

    def test_add_item_rejects_topic_mismatch(self) -> None:
        state = {"version": 1, "topic": "RAG", "items": []}

        with self.assertRaisesRegex(ValueError, "topic"):
            MODULE.add_item(
                state,
                topic="动态规划",
                question="状态是什么？",
                gap="把状态当成循环变量",
                answer_ref="checkpoints/dp.md#state",
                due="2026-09-02",
            )

    def test_due_items_returns_due_and_overdue_only(self) -> None:
        state = {"version": 1, "topic": "RAG", "items": []}
        for due in ("2026-09-01", "2026-09-03", "2026-09-05"):
            MODULE.add_item(
                state,
                topic="RAG",
                question=f"问题 {due}",
                gap=f"缺口 {due}",
                answer_ref=f"checkpoint.md#{due}",
                due=due,
            )

        due = MODULE.due_items(state, on="2026-09-03")

        self.assertEqual([1, 2], [item["id"] for item in due])

    def test_grade_item_records_result_and_uses_explicit_next_due(self) -> None:
        state = {"version": 1, "topic": "", "items": []}
        MODULE.add_item(
            state,
            topic="RAG",
            question="为什么要切块？",
            gap="只记住了 token 限制，没有提到检索粒度",
            answer_ref="checkpoints/rag.md#chunking",
            due="2026-09-02",
        )

        item = MODULE.grade_item(
            state,
            item_id=1,
            result="fail",
            on="2026-09-02",
            next_due="2026-09-04",
            note="仍未解释召回与上下文完整性的取舍",
        )

        self.assertEqual("2026-09-04", item["due"])
        self.assertEqual("fail", item["history"][0]["result"])
        self.assertEqual(1, item["lapses"])
        self.assertIn("召回", item["gap"])

    def test_cli_add_writes_only_declared_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = root / "progress.json"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = MODULE.main(
                    [
                        "add",
                        "--file",
                        str(path),
                        "--topic",
                        "RAG",
                        "--question",
                        "检索发生在哪个阶段？",
                        "--gap",
                        "阶段混淆",
                        "--answer-ref",
                        "checkpoint.md#retrieval",
                        "--due",
                        "2026-09-02",
                    ]
                )

            self.assertEqual(0, exit_code)
            self.assertEqual({"progress.json"}, {item.name for item in root.iterdir()})
            payload = json.loads(stdout.getvalue())
            self.assertEqual(1, payload["id"])


if __name__ == "__main__":
    unittest.main()
