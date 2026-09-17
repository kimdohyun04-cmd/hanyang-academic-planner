# 입력 데이터 구조

## 최상위 필드

- `student`: 학생 기본정보와 데이터 기준일
- `requirements`: 판정할 졸업요건 배열
- `sources`: 적용한 공식 자료
- `limitations`: 보고서에 표시할 한계

## 학생 정보

```json
{
  "student": {
    "name": "이름",
    "student_id": "학번",
    "campus": "ERICA",
    "college": "대학",
    "department": "학과",
    "admission_year": 2023,
    "year": 2,
    "status": "재학생",
    "as_of": "YYYY-MM-DD"
  }
}
```

배포용 예시나 공개 보고서에는 실제 이름과 학번을 넣지 않는다.

## 최소값 요건

학점, 강좌 수, 평점처럼 기준 이상을 충족해야 하는 항목이다.

```json
{
  "id": "total_credits",
  "label": "졸업학점",
  "kind": "minimum",
  "required": 130,
  "completed": 60,
  "in_progress": 18,
  "unit": "학점",
  "priority": "high",
  "action": "남은 학기에 필요한 학점을 배치하세요.",
  "source_id": "graduation-requirements"
}
```

## 참·거짓 요건

논문, 필수과목, 재학 상태처럼 충족 여부로 판단하는 항목이다.

```json
{
  "id": "graduation_thesis",
  "label": "졸업논문·시험·작품",
  "kind": "boolean",
  "satisfied": false,
  "in_progress": false,
  "priority": "high",
  "action": "학과의 제출 일정과 형식을 확인하세요.",
  "source_id": "graduation-requirements"
}
```

## 확인 필요 표시

화면의 빈칸을 0으로 해석했거나 학과 내규가 필요한 항목은 다음 값을 추가한다.

```json
{
  "needs_official_confirmation": true,
  "note": "포털 표시와 학과 내규를 다시 확인해야 함"
}
```
