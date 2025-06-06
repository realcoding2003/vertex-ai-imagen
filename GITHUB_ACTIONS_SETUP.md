# 🚀 GitHub Actions 자동 PyPI 배포 설정 가이드

## 📋 설정된 워크플로우

### 1. 🎉 자동 릴리스 배포 (`publish-pypi.yml`)
- **트리거**: GitHub Release 생성 시
- **기능**: PyPI와 TestPyPI에 자동 배포
- **보안**: Trusted Publishing 사용

### 2. 🧪 CI 테스트 (`test.yml`)
- **트리거**: Push, Pull Request
- **기능**: 다중 Python 버전 테스트, 코드 품질 검사
- **지원 버전**: Python 3.8-3.12

### 3. 🔧 수동 배포 (`manual-deploy.yml`)
- **트리거**: 수동 실행
- **기능**: 버전 업데이트 + 선택적 배포
- **옵션**: TestPyPI, PyPI, 또는 둘 다

## 🔑 Trusted Publishing 설정 (권장)

### PyPI 설정
1. [PyPI 계정](https://pypi.org)으로 로그인
2. [Publishing 설정](https://pypi.org/manage/account/publishing/)으로 이동
3. "Add a new pending publisher" 클릭
4. 다음 정보 입력:
   - **PyPI project name**: `vertex-ai-imagen`
   - **Owner**: `{당신의_GitHub_사용자명}`
   - **Repository name**: `vertex-ai-imagen`
   - **Workflow name**: `publish-pypi.yml`
   - **Environment name**: `pypi`

### TestPyPI 설정
1. [TestPyPI 계정](https://test.pypi.org) 생성/로그인
2. [TestPyPI Publishing 설정](https://test.pypi.org/manage/account/publishing/)으로 이동
3. 위와 동일하게 설정 (Environment name은 `testpypi`)

## 🛡️ GitHub Environment 설정

### Repository Settings 설정
1. GitHub 저장소 → Settings → Environments
2. 두 개의 Environment 생성:

#### 📦 `pypi` Environment
- **Protection rules**: 
  - ✅ Required reviewers (본인 추가)
  - ✅ Wait timer: 5분 (실수 방지)
- **Environment secrets**: 없음 (Trusted Publishing 사용)

#### 🧪 `testpypi` Environment  
- **Protection rules**: 
  - ❌ Required reviewers (자동 배포)
- **Environment secrets**: 없음 (Trusted Publishing 사용)

## 🔄 사용 방법

### 자동 릴리스 배포
1. 코드 변경 및 테스트
2. GitHub에서 [새 릴리스 생성](https://github.com/{사용자명}/vertex-ai-imagen/releases/new)
   - Tag: `v1.2.0` (버전에 맞게)
   - Title: `Release 1.2.0`
   - Description: 변경사항 설명
3. "Publish release" 클릭
4. 자동으로 PyPI와 TestPyPI에 배포됨

### 수동 배포
1. GitHub → Actions → "🔧 Manual Deploy"
2. "Run workflow" 클릭
3. 옵션 선택:
   - **배포 대상**: testpypi/pypi/both
   - **버전 업데이트**: none/patch/minor/major
4. "Run workflow" 실행

## 🔧 대체 방법: API Token 사용

Trusted Publishing이 작동하지 않는 경우:

### API Token 생성
1. **PyPI**: [API 토큰 생성](https://pypi.org/manage/account/token/)
2. **TestPyPI**: [TestPyPI 토큰 생성](https://test.pypi.org/manage/account/token/)

### GitHub Secrets 설정
1. Repository → Settings → Secrets and variables → Actions
2. Secrets 추가:
   - `PYPI_API_TOKEN`: PyPI API 토큰
   - `TESTPYPI_API_TOKEN`: TestPyPI API 토큰

### 워크플로우 수정
```yaml
# publish-pypi.yml에서 다음 부분을 수정:
- name: 🚀 Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    user: __token__
    password: ${{ secrets.PYPI_API_TOKEN }}
```

## 🎯 워크플로우 상태 확인

### Badge 추가
README.md에 상태 배지 추가:
```markdown
![Tests](https://github.com/{사용자명}/vertex-ai-imagen/workflows/🧪%20Tests%20and%20Quality%20Checks/badge.svg)
![PyPI](https://github.com/{사용자명}/vertex-ai-imagen/workflows/🚀%20Publish%20to%20PyPI/badge.svg)
```

### 실행 로그 확인
- GitHub → Actions 탭에서 워크플로우 실행 상태 확인
- 실패 시 로그에서 오류 원인 분석

## 🚨 문제 해결

### 일반적인 문제
1. **Trusted Publishing 실패**
   - PyPI/TestPyPI 설정 정보 재확인
   - Environment 이름 일치 확인
   - Repository 권한 확인

2. **버전 충돌**
   - PyPI는 동일 버전 재업로드 불가
   - 버전 번호를 증가시킨 후 재시도

3. **빌드 실패**
   - pyproject.toml 설정 확인
   - 의존성 문제 해결

### 로그 분석
```bash
# 로컬에서 워크플로우와 동일한 빌드 테스트
python -m build
twine check dist/*
```

## 📈 다음 단계

1. **릴리스 노트 자동화**: GitHub Release 설명 자동 생성
2. **의존성 업데이트**: Dependabot 설정
3. **보안 스캔**: CodeQL 설정
4. **성능 모니터링**: 패키지 다운로드 통계 추적

---

💡 **팁**: 처음에는 TestPyPI로 테스트한 후 실제 PyPI에 배포하는 것을 권장합니다! 