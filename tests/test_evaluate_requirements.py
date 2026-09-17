import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from evaluate_requirements import evaluate, evaluate_requirement, validate_input


class RequirementEvaluationTest(unittest.TestCase):
    def test_minimum_requirement_statuses(self):
        complete = evaluate_requirement(
            {"id": "a", "label": "완료", "kind": "minimum", "required": 3, "completed": 3}
        )
        in_progress = evaluate_requirement(
            {
                "id": "b",
                "label": "진행",
                "kind": "minimum",
                "required": 3,
                "completed": 1,
                "in_progress": 2,
            }
        )
        incomplete = evaluate_requirement(
            {"id": "c", "label": "부족", "kind": "minimum", "required": 3, "completed": 1}
        )

        self.assertEqual(complete["display_status"], "complete")
        self.assertEqual(in_progress["display_status"], "in_progress")
        self.assertEqual(incomplete["remaining_after_current"], 2)
        self.assertEqual(incomplete["display_status"], "incomplete")

    def test_official_confirmation_overrides_calculated_status(self):
        result = evaluate_requirement(
            {
                "id": "unknown",
                "label": "확인 필요",
                "kind": "boolean",
                "satisfied": True,
                "needs_official_confirmation": True,
            }
        )

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["display_status"], "unknown")

    def test_summary_counts_all_statuses(self):
        data = {
            "student": {"campus": "ERICA", "department": "테스트", "as_of": "2026-09-17"},
            "requirements": [
                {"id": "a", "label": "완료", "kind": "boolean", "satisfied": True},
                {
                    "id": "b",
                    "label": "진행",
                    "kind": "boolean",
                    "satisfied": False,
                    "in_progress": True,
                },
                {"id": "c", "label": "부족", "kind": "boolean", "satisfied": False},
                {
                    "id": "d",
                    "label": "확인",
                    "kind": "boolean",
                    "satisfied": False,
                    "needs_official_confirmation": True,
                },
            ],
        }

        self.assertEqual(validate_input(data), [])
        self.assertEqual(
            evaluate(data)["summary"],
            {"complete": 1, "in_progress": 1, "incomplete": 1, "unknown": 1},
        )

    def test_rejects_negative_values(self):
        data = {
            "student": {"campus": "ERICA", "department": "테스트", "as_of": "2026-09-17"},
            "requirements": [
                {"id": "a", "label": "오류", "kind": "minimum", "required": 3, "completed": -1}
            ],
        }

        self.assertIn("requirements[0].completed는 0 이상이어야 합니다.", validate_input(data))


if __name__ == "__main__":
    unittest.main()
