# 알바핀치 (alba_pinch)

대타/단기알바 매칭 사이트 — Django + 휴대폰 번호 기반 자체 회원가입

## 핵심 특징

- ✅ **휴대폰 번호로 가입/로그인** (이메일 X)
- ✅ **30일 자동 로그인** (체크박스로 선택 가능)
- ✅ **카카오/네이버 의존성 없음** (자체 인증)
- ✅ **모바일 우선 UI**

## 로컬 개발 환경 세팅

```bash
# 1. 가상환경 생성 + 활성화
python -m venv venv
venv\Scripts\activate

# 2. 의존성 설치
python -m pip install -r requirements.txt

# 3. .env 파일 생성 (다음 내용 복사)
# SECRET_KEY=django-insecure-local-only-1234567890
# DEBUG=True
# ALLOWED_HOSTS=localhost,127.0.0.1

# 4. 마이그레이션
python manage.py makemigrations users jobs reviews
python manage.py migrate

# 5. 관리자 계정 생성 (휴대폰 번호로!)
python manage.py createsuperuser
# Phone: 01012345678 (하이픈 없이)
# Nickname: 관리자
# Password: ...

# 6. 서버 실행
python manage.py runserver
```

## 폴더 구조

```
alba_pinch/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py        # 로컬 개발 (SQLite)
│   │   └── prod.py       # NHN Cloud 배포 (PostgreSQL)
│   └── urls.py
├── apps/
│   ├── users/            # 회원가입/로그인/프로필
│   ├── jobs/             # 구인글/지원 (개발 예정)
│   ├── reviews/          # 평점/신고
│   └── core/             # 공통
├── templates/
│   ├── users/
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── profile_detail.html
│   │   └── profile_edit.html
│   └── jobs/
│       └── list.html     # 메인 페이지
└── requirements.txt
```

## 자동 로그인 동작 방식

`config/settings/base.py` 의 3가지 설정:

```python
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30        # 30일
SESSION_EXPIRE_AT_BROWSER_CLOSE = False        # 브라우저 닫아도 유지
SESSION_SAVE_EVERY_REQUEST = True              # 활동 시 30일 자동 연장
```

로그인 화면의 "로그인 유지" 체크박스로 사용자가 선택 가능:
- ✅ 체크: 30일 유지 (`set_expiry(30일)`)
- ❌ 미체크: 브라우저 닫으면 만료 (`set_expiry(0)`)

## URL

| 경로 | 설명 |
|---|---|
| `/` | 메인 (구인글 목록) |
| `/users/signup/` | 회원가입 |
| `/users/login/` | 로그인 |
| `/users/logout/` | 로그아웃 |
| `/users/profile/` | 내 프로필 |
| `/users/profile/edit/` | 프로필 수정 |
| `/admin/` | 관리자 페이지 |

## 다음 단계

1. ✅ 회원가입/로그인 (휴대폰 번호 + 비밀번호)
2. ⬜ 구인글 작성/목록/상세 페이지
3. ⬜ 지원하기 + 수락/거절 (전화번호 공개)
4. ⬜ 평점 시스템
5. ⬜ NHN Cloud 배포
