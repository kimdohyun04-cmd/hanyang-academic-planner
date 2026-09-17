# 한양 아카데믹 플래너

한양대학교 ERICA 학부생의 졸업사정 자료를 공식 근거와 함께 해석해 `현재 상태 → 부족한 이유 → 다음 행동`으로 정리하는 AI 학사 스킬입니다.

2026 한양대학교 ERICA **AI 활용 학사제도 개선 아이디어 공모전** 제출용 MVP입니다. 학교의 공식 졸업 판정을 대체하지 않습니다.

## 무엇을 하나요

- 졸업요건을 충족 · 수강·진행 중 · 미충족 · 공식 확인 필요로 판정
- 먼저 할 일과 학기별 행동계획 정리
- 학사공지가 나에게 해당하는지 판단
- 휴학·다전공 같은 선택의 영향 정리
- 담당 부서에 보낼 문의문 작성

학점·자격·기한 계산은 `scripts/evaluate_requirements.py`가 맡고, AI는 계산 결과를 바꾸지 않은 채 설명과 계획만 작성합니다.

## 바로 실행해 보기

Python 3.9 이상, 외부 패키지 없음.

```bash
# 입력 검증
python3 scripts/evaluate_requirements.py assets/sample-student.json --validate-only

# 공개용 보고서 (이름·학번 가림)
python3 scripts/evaluate_requirements.py assets/sample-student.json --format markdown --privacy public

# 판정기 테스트
python3 -m unittest discover -s tests -v
```

`assets/sample-student.json`은 가상의 학생 데이터입니다.

## AI 에이전트에 설치

`SKILL.md`를 읽는 Agent Skills 형식입니다. Claude Code 기준:

```bash
git clone https://github.com/kimdohyun04-cmd/hanyang-academic-planner ~/.claude/skills/hanyang-academic-planner
```

설치 후 에이전트에게 이렇게 요청합니다.

- "내 졸업요건 점검해줘" (졸업사정조회 값을 `assets/input-template.json` 형식으로 입력)
- "이 학사공지 나한테 해당돼?" (공지 본문 붙여넣기)
- "전공심화 인정 여부를 학과에 물어볼 문의문 써줘"

## 폴더 구성

| 경로 | 역할 |
|---|---|
| `SKILL.md` | 작업 흐름, 결과 형식, 금지사항 |
| `scripts/evaluate_requirements.py` | 졸업요건 판정기 |
| `references/` | 공식 링크, 데이터 스키마, 개인정보·오답 방지 정책 |
| `assets/` | 입력 서식, 가상 학생 예시, 보고서 서식 |
| `tests/` | 판정기 회귀 테스트 |
| `agents/openai.yaml` | 에이전트 표시 정보 |

## 안전 원칙

- 포털 아이디·비밀번호·OTP·세션 주소를 요구하거나 저장하지 않습니다.
- 실제 학생 데이터는 이 저장소에 올리지 마세요.
- 수강신청·휴학·전공 포기 등은 대신 제출하지 않습니다.
- 공식 출처가 없는 규칙은 만들지 않고, 불확실한 항목은 `확인 필요`로 표시합니다.

## 한계

- 포털과 연동되지 않아 졸업사정 값을 직접 옮겨 입력해야 합니다.
- 판정기가 계산하는 범위는 졸업사정 요건이며, 공지 판단과 선택 비교는 AI 설명에 의존합니다.
- 학과별 세부 내규와 최신 공지는 `references/`를 갱신해야 반영됩니다.
