# 김누리 프로필 사이트 — CLAUDE.md

## 프로젝트 개요

김누리(Nuri Kim) 테크 트레이너의 개인 프로필 웹사이트 및 강사 자료 관리 폴더.
GitHub Pages로 배포 중: **profile.skilleat.com**

---

## 파일 구조

### HTML 웹사이트 (3개 파일)

| 파일 | 제목 | 역할 |
|------|------|------|
| `index.html` | 김누리 · Nuri Kim — 감 잡아주는 테크 트레이너 | 메인 프로필 페이지 |
| `calendar.html` | 교육 일정 문의 · 김누리 | 월별 강의 일정 캘린더 (외부 공개용) |
| `admin.html` | 관리자 · 일정 관리 | 일정 데이터 관리용 어드민 패널 (비밀번호 보호) |

### 정적 자산

| 파일 | 설명 |
|------|------|
| `nrkim.png` | 프로필 사진 |
| `CNAME` | GitHub Pages 커스텀 도메인 (`profile.skilleat.com`) |
| `Nuri Kim Profile _standalone_.html` | 독립 실행형 프로필 HTML (이메일/오프라인 배포용) |

### 강사 소개서 / 이력서 문서

| 파일 | 설명 |
|------|------|
| `강사소개서_김누리_MS-Copilot-AI_2026_v4.docx` | MS Copilot/AI 강의용 최신 강사 소개서 (한국어) |
| `강사소개서_김누리_Azure-Kubernetes-AI_2026_v3.docx` | Azure/Kubernetes/AI 강의용 강사 소개서 (한국어) |
| `강사소개서_김누리_Azure-Kubernetes-AI_2026.docx` | 위의 이전 버전 |
| `김누리_강사소개서_v2.docx` | 범용 강사 소개서 v2 (한국어) |
| `김누리_강사소개서.docx` | 범용 강사 소개서 v1 (한국어) |
| `김누리_Technical_Trainer_v2.pdf` | 기술 트레이너 프로필 PDF v2 |
| `김누리_Technical_Trainer.pdf` | 기술 트레이너 프로필 PDF v1 |
| `Nuri_Kim_Instructor_Profile_Ko.pdf` | 강사 프로필 PDF (한국어) |
| `Nuri_Kim_Instructor_Profile_En.pdf` | 강사 프로필 PDF (영어) |
| `Nuri_Kim_Instructor_Profile_MS-Copilot-AI_2026_v4_EN.docx` | MS Copilot/AI 강의용 강사 소개서 (영어) |
| `nuri_kim_resume.docx` | 영문 이력서 |
| `사전설문지_교육개선.docx` | 교육 개선을 위한 사전 설문지 |

---

## 사이트 디자인 시스템

### 컬러 토큰

```css
--bg:            #FFFFFF
--bg-alt:        #F6F7F9
--text-heading:  #1A1A35  (Navy)
--text-body:     #4A4E5A
--text-muted:    #8A8F98
--accent:        #E04E12  (Orange — 브랜드 컬러)
--accent-hover:  #C4430E
--navy:          #1A1A35
```

### 레이아웃

- 최대 너비: `1100px` (index.html), `1400px` (calendar.html)
- 네비게이션: Navy 배경 고정, 스크롤 시 반투명 흰색으로 전환
- 폰트: Inter (Google Fonts)
- 프레임워크 없음 — 순수 HTML/CSS/JS

---

## 캘린더 데이터 관리

`calendar.html`에는 강의 일정이 JavaScript 배열 `EVENTS`로 하드코딩되어 있음.

```js
// 이벤트 구조 예시
{ date: '2026-08-11', label: '직무 강연', time: '14:00~16:00', mode: '오프라인' }
```

- `mode`: `'온라인'` | `'오프라인'` | `'휴무'` 등
- 같은 날짜에 여러 이벤트 등록 가능 (다중 이벤트 지원)
- `admin.html`에서 관리자가 일정을 추가/수정 가능

---

## 배포

- **플랫폼**: GitHub Pages
- **도메인**: profile.skilleat.com (CNAME 파일로 설정)
- **브랜치**: `main`
- 변경 후 `git push` 하면 자동 배포됨

## 작업 규칙

- **일정 관련 변경 요청** (추가/수정/삭제 등)은 파일 수정 후 `git commit` + `git push`까지 자동으로 처리한다. 별도로 요청하지 않아도 됨.
