---
name: hanyang-academic-planner
description: Analyze Hanyang University ERICA undergraduate degree-audit data and official academic notices to explain unmet graduation requirements, calculate remaining requirements, create grounded next-action plans, and compare academic choices. Use when a user asks in Korean or English to check 졸업요건, 남은 학점, 필수과목, 사회봉사·산학협력·PBL 요건, 학사공지 applicability, semester planning, or the impact of leave or multiple-major choices. Accept structured JSON or user-provided redacted portal screenshots; never request portal passwords or submit academic applications.
---

# 한양 아카데믹 플래너

## 목적

한양대학교 ERICA 학부생의 졸업사정 데이터를 공식 근거와 함께 해석하고, `현재 상태 → 부족한 이유 → 다음 행동`으로 변환한다. 학교의 공식 졸업 판정을 대체하지 않는다.

## 작업 흐름

1. 입력이 JSON이면 `references/data-schema.md`에 따라 필드를 확인한다.
2. 입력이 포털 화면이면 이름·학번 등 불필요한 개인정보를 기록하지 말고, 표시된 값만 구조화한다.
3. 다음 명령으로 확정 계산을 수행한다.

```bash
python3 scripts/evaluate_requirements.py INPUT.json --format json
```

4. 계산 결과를 바꾸지 말고 쉬운 한국어로 설명한다.
5. 미충족·진행 중 요건을 우선순위와 시점에 따라 행동계획으로 배열한다.
6. 답변마다 적용한 근거, 기준일, 확인이 필요한 예외를 표시한다.
7. 중요한 선택은 사용자의 최종 확인과 담당 부서 검토로 연결한다.

## 결과 형식

`assets/report-template.md` 순서를 따른다.

- 한 줄 진단
- 충족·진행 중·미충족 요약
- 우선 행동 3개
- 요건별 계산표
- 이번 학기와 다음 학기 계획
- 공식 근거와 기준일
- 불확실성 및 담당 부서 확인사항

## 규칙

- 학점·기한·자격 같은 확정 조건은 스크립트 결과를 사용한다.
- 생성형 AI는 설명, 우선순위 정리, 계획 문장 작성에만 사용한다.
- 공식 출처가 없는 규칙을 만들지 않는다.
- `needs_official_confirmation`이 참인 항목은 확정적으로 표현하지 않는다.
- 수강 중 학점은 취득 학점과 분리한다.
- 규정 기준일이 입력 데이터보다 오래되었으면 최신 공지를 다시 확인하도록 안내한다.
- 개인정보 보호 기준은 `references/safety-policy.md`를 따른다.
- 공식 자료를 갱신할 때는 `references/official-sources.md`를 확인한다.

## 주요 명령

공개용 요약:

```bash
python3 scripts/evaluate_requirements.py INPUT.json --format markdown --privacy public
```

개인용 상세 보고서:

```bash
python3 scripts/evaluate_requirements.py INPUT.json --format markdown --privacy private --output REPORT.md
```

입력 검증만 수행:

```bash
python3 scripts/evaluate_requirements.py INPUT.json --validate-only
```

판정기 회귀 테스트:

```bash
python3 -m unittest discover -s tests -v
```

## 금지사항

- 포털 아이디, 비밀번호, OTP, 세션 URL을 요청하거나 저장하지 않는다.
- 학생 확인 없이 수강신청, 휴학, 전공 포기 등을 제출하지 않는다.
- AI 추론만으로 졸업 가능 여부를 확정하지 않는다.
- 배포용 스킬 폴더에 실제 학생 데이터를 포함하지 않는다.
