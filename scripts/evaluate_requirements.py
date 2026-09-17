#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


STATUS_LABELS = {
    "complete": "충족",
    "in_progress": "수강·진행 중",
    "incomplete": "미충족",
    "unknown": "확인 필요",
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate Hanyang ERICA academic requirements from structured JSON."
    )
    parser.add_argument("input", type=Path, help="Input JSON file")
    parser.add_argument(
        "--format", choices=("json", "markdown"), default="markdown"
    )
    parser.add_argument(
        "--privacy", choices=("public", "private"), default="public"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def load_input(path):
    with path.open(encoding="utf-8") as input_file:
        return json.load(input_file)


def validate_input(data):
    errors = []
    if not isinstance(data, dict):
        return ["최상위 값은 객체여야 합니다."]

    student = data.get("student")
    if not isinstance(student, dict):
        errors.append("student 객체가 필요합니다.")
    else:
        for field in ("campus", "department", "as_of"):
            if not student.get(field):
                errors.append(f"student.{field} 값이 필요합니다.")

    requirements = data.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements는 하나 이상의 항목을 가진 배열이어야 합니다.")
        return errors

    seen_ids = set()
    for index, requirement in enumerate(requirements):
        prefix = f"requirements[{index}]"
        if not isinstance(requirement, dict):
            errors.append(f"{prefix}는 객체여야 합니다.")
            continue

        requirement_id = requirement.get("id")
        if not requirement_id:
            errors.append(f"{prefix}.id 값이 필요합니다.")
        elif requirement_id in seen_ids:
            errors.append(f"중복된 requirement id: {requirement_id}")
        else:
            seen_ids.add(requirement_id)

        if not requirement.get("label"):
            errors.append(f"{prefix}.label 값이 필요합니다.")

        kind = requirement.get("kind")
        if kind not in ("minimum", "boolean"):
            errors.append(f"{prefix}.kind는 minimum 또는 boolean이어야 합니다.")
        elif kind == "minimum":
            for field in ("required", "completed"):
                value = requirement.get(field)
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    errors.append(f"{prefix}.{field}는 숫자여야 합니다.")
                elif value < 0:
                    errors.append(f"{prefix}.{field}는 0 이상이어야 합니다.")
            in_progress = requirement.get("in_progress", 0)
            if not isinstance(in_progress, (int, float)) or isinstance(
                in_progress, bool
            ):
                errors.append(f"{prefix}.in_progress는 숫자여야 합니다.")
            elif in_progress < 0:
                errors.append(f"{prefix}.in_progress는 0 이상이어야 합니다.")
        elif kind == "boolean" and not isinstance(
            requirement.get("satisfied"), bool
        ):
            errors.append(f"{prefix}.satisfied는 불리언이어야 합니다.")

    return errors


def evaluate_requirement(requirement):
    result = dict(requirement)
    kind = requirement["kind"]

    if kind == "minimum":
        required = float(requirement["required"])
        completed = float(requirement["completed"])
        in_progress = float(requirement.get("in_progress", 0))
        projected = completed + in_progress
        remaining_now = max(required - completed, 0)
        remaining_after_current = max(required - projected, 0)

        if completed >= required:
            status = "complete"
        elif projected >= required:
            status = "in_progress"
        else:
            status = "incomplete"

        result.update(
            {
                "status": status,
                "projected": projected,
                "remaining_now": remaining_now,
                "remaining_after_current": remaining_after_current,
            }
        )
    else:
        satisfied = requirement["satisfied"]
        in_progress = bool(requirement.get("in_progress", False))
        if satisfied:
            status = "complete"
        elif in_progress:
            status = "in_progress"
        else:
            status = "incomplete"
        result["status"] = status

    if requirement.get("needs_official_confirmation"):
        result["display_status"] = "unknown"
    else:
        result["display_status"] = result["status"]
    return result


def evaluate(data):
    evaluated = [evaluate_requirement(item) for item in data["requirements"]]
    evaluated.sort(
        key=lambda item: (
            0 if item["display_status"] in ("incomplete", "unknown") else 1,
            PRIORITY_ORDER.get(item.get("priority", "medium"), 2),
            item["label"],
        )
    )

    counts = {status: 0 for status in STATUS_LABELS}
    for requirement in evaluated:
        counts[requirement["display_status"]] += 1

    return {
        "student": data["student"],
        "summary": counts,
        "requirements": evaluated,
        "sources": data.get("sources", []),
        "limitations": data.get("limitations", []),
    }


def format_number(value):
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def mask_student_id(student_id):
    text = str(student_id or "")
    if len(text) <= 4:
        return "비공개"
    return f"{text[:4]}{'*' * (len(text) - 4)}"


def format_markdown(result, privacy):
    student = result["student"]
    if privacy == "private":
        name = student.get("name", "학생")
        student_id = str(student.get("student_id", "미입력"))
    else:
        name = "비식별 학생"
        student_id = mask_student_id(student.get("student_id"))

    summary = result["summary"]
    lines = [
        "# 한양 아카데믹 플래너 학사 보고서",
        "",
        f"- 대상: {name} ({student_id})",
        f"- 소속: {student.get('campus')} {student.get('department')}",
        f"- 학적 기준일: {student.get('as_of')}",
        "- 주의: 본 보고서는 학사계획 지원용이며 공식 졸업 판정을 대체하지 않습니다.",
        "",
        "## 요약",
        "",
        f"- 충족: {summary['complete']}개",
        f"- 수강·진행 중: {summary['in_progress']}개",
        f"- 미충족: {summary['incomplete']}개",
        f"- 공식 확인 필요: {summary['unknown']}개",
        "",
        "## 우선 행동",
        "",
    ]

    actionable = [
        item
        for item in result["requirements"]
        if item["display_status"] in ("incomplete", "in_progress", "unknown")
    ]
    for index, item in enumerate(actionable[:5], start=1):
        action = item.get("action", "공식 안내와 담당 부서에서 이수 방법을 확인하세요.")
        lines.append(f"{index}. **{item['label']}** — {action}")

    current_actions = [
        item for item in actionable if item["display_status"] == "in_progress"
    ]
    next_actions = [
        item
        for item in actionable
        if item["display_status"] in ("incomplete", "unknown")
    ]
    lines.extend(["", "## 학기별 행동계획", "", "### 이번 학기", ""])
    if current_actions:
        for item in current_actions:
            lines.append(f"- **{item['label']}**: {item.get('action', '진행 상태를 확인하세요.')}")
    else:
        lines.append("- 현재 진행 중으로 입력된 요건이 없습니다.")

    lines.extend(["", "### 다음 수강신청 전", ""])
    if next_actions:
        for item in next_actions[:5]:
            lines.append(f"- **{item['label']}**: {item.get('action', '이수 방법을 확인하세요.')}")
    else:
        lines.append("- 추가로 계획할 미충족 요건이 없습니다.")

    lines.extend(
        [
            "",
            "## 요건별 결과",
            "",
            "| 상태 | 요건 | 현재 | 수강·진행 반영 | 남은 값 | 다음 행동 |",
            "|---|---|---:|---:|---:|---|",
        ]
    )

    for item in result["requirements"]:
        display_status = STATUS_LABELS[item["display_status"]]
        if item["kind"] == "minimum":
            current = f"{format_number(item['completed'])}/{format_number(item['required'])}"
            projected = format_number(item["projected"])
            remaining = format_number(item["remaining_after_current"])
        else:
            current = "충족" if item["satisfied"] else "미충족"
            projected = "진행 중" if item.get("in_progress") else "-"
            remaining = "-"
        action = item.get("action", "-").replace("|", "/")
        lines.append(
            f"| {display_status} | {item['label']} | {current} | {projected} | {remaining} | {action} |"
        )

    lines.extend(["", "## 공식 근거", ""])
    if result["sources"]:
        for source in result["sources"]:
            lines.append(
                f"- [{source['title']}]({source['url']}) — 기준일 {source.get('as_of', '미상')}"
            )
    else:
        lines.append("- 공식 근거가 입력되지 않았습니다.")

    lines.extend(["", "## 한계 및 확인사항", ""])
    limitations = result["limitations"] or [
        "최종 졸업 가능 여부는 포털과 담당 부서에서 다시 확인해야 합니다."
    ]
    for limitation in limitations:
        lines.append(f"- {limitation}")

    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as error:
        print(f"입력 파일을 읽을 수 없습니다: {error}", file=sys.stderr)
        return 2

    errors = validate_input(data)
    if errors:
        for error in errors:
            print(f"오류: {error}", file=sys.stderr)
        return 2

    if args.validate_only:
        print("입력 데이터가 유효합니다.")
        return 0

    result = evaluate(data)
    if args.format == "json":
        output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    else:
        output = format_markdown(result, args.privacy)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
