# MCP 서버 구축 프로젝트 - 환경설정

## 프로젝트 개요

Microsoft의 MarkItDown을 벤치마킹하여 동일한 기능을 가진 MCP 서버를 구축하고, 더 나은 업그레이드 기능을 추가하는 프로젝트입니다.

## 목표

### 1차 목표: 완전한 기능 복제
- MarkItDown의 모든 기능을 MCP 서버로 구현
- 동일한 입력/출력 형식 지원
- 같은 변환 품질 제공

### 2차 목표: 업그레이드 기능
- 향상된 한국어 지원
- 더 많은 파일 형식 지원
- 성능 최적화
- 고급 메타데이터 추출

## 개발 환경 설정

### 필수 요구사항

```bash
# Python 3.10 이상
python --version

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 기본 의존성 설치
pip install --upgrade pip
pip install mcp
pip install fastapi
pip install uvicorn
```

### 시스템 의존성

```bash
# macOS
brew install exiftool
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install exiftool
sudo apt-get install ffmpeg

# Windows
# ExifTool: https://exiftool.org/
# FFmpeg: https://ffmpeg.org/download.html
```

### 개발 도구

```bash
# 코드 품질 도구
pip install black isort pylint mypy
pip install pytest pytest-cov
pip install pre-commit

# 문서화 도구
pip install mkdocs mkdocs-material

# 성능 모니터링
pip install memory-profiler
pip install py-spy
```

## 프로젝트 구조

```
428-MCP-서버-구축/
├── 01-환경설정/
│   ├── README.md                    # 현재 파일
│   ├── requirements.txt             # Python 의존성
│   ├── requirements-dev.txt         # 개발 의존성
│   ├── .env.example                 # 환경변수 예시
│   └── setup.py                     # 패키지 설정
├── 02-markitdown-분석/
│   ├── 01-코드분석보고서.md         # 상세 분석 보고서
│   ├── 02-아키텍처-분석.md          # 아키텍처 분석
│   ├── 03-API-분석.md               # API 구조 분석
│   └── 04-벤치마킹-계획.md          # 벤치마킹 계획
├── 03-기본-MCP-서버-구현/
│   ├── 01-MCP-서버-기본구조.md      # MCP 서버 기본 구조
│   ├── 02-도구-인터페이스.md        # 도구 인터페이스 설계
│   ├── 03-메시지-처리.md            # 메시지 처리 로직
│   └── 04-에러-핸들링.md            # 에러 처리 시스템
├── 04-문서변환-엔진/
│   ├── 01-변환기-아키텍처.md        # 변환기 아키텍처
│   ├── 02-파일-형식-지원.md         # 지원 파일 형식
│   ├── 03-스트림-처리.md            # 스트림 처리 시스템
│   └── 04-플러그인-시스템.md        # 플러그인 시스템
├── 05-업그레이드-기능/
│   ├── 01-한국어-지원.md            # 한국어 특화 기능
│   ├── 02-확장-파일-형식.md         # 추가 파일 형식
│   ├── 03-성능-최적화.md            # 성능 개선
│   └── 04-고급-메타데이터.md        # 메타데이터 추출
├── 06-테스트-및-검증/
│   ├── 01-단위-테스트.md            # 단위 테스트
│   ├── 02-통합-테스트.md            # 통합 테스트
│   ├── 03-성능-테스트.md            # 성능 테스트
│   └── 04-호환성-테스트.md          # 호환성 테스트
└── 07-배포-및-문서화/
    ├── 01-배포-가이드.md            # 배포 가이드
    ├── 02-사용자-매뉴얼.md          # 사용자 매뉴얼
    ├── 03-API-문서.md               # API 문서
    └── 04-유지보수-가이드.md        # 유지보수 가이드
```

## 개발 워크플로우

### 1. 환경 설정
```bash
# 저장소 클론 (가상)
git clone <repository-url>
cd 428-MCP-서버-구축

# 환경 설정
python -m venv venv
source venv/bin/activate
pip install -r 01-환경설정/requirements-dev.txt

# pre-commit 설정
pre-commit install
```

### 2. 개발 사이클
```bash
# 기능 개발
git checkout -b feature/new-converter

# 코드 작성
# ...

# 테스트 실행
pytest 06-테스트-및-검증/

# 코드 품질 확인
black .
isort .
pylint src/
mypy src/

# 커밋
git add .
git commit -m "feat: add new converter"
```

### 3. 배포 준비
```bash
# 문서 생성
mkdocs build

# 패키지 빌드
python setup.py sdist bdist_wheel

# 배포
twine upload dist/*
```

## 품질 관리

### 코드 스타일
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.pylint]
max-line-length = 88
disable = [
    "missing-docstring",
    "invalid-name",
]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 테스트 커버리지
```bash
# 커버리지 측정
pytest --cov=src --cov-report=html --cov-report=term-missing

# 목표: 90% 이상 커버리지
```

## 모니터링 및 디버깅

### 성능 모니터링
```python
# memory_profiler 사용
@profile
def convert_large_file(file_path):
    # 메모리 사용량 모니터링
    pass

# py-spy 사용
py-spy top --pid <process_id>
```

### 로깅 설정
```python
import logging

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
```

## 다음 단계

1. **markitdown 분석**: 세부 기능 분석 및 벤치마킹 계획 수립
2. **MCP 서버 구현**: 기본 MCP 서버 구조 구현
3. **변환 엔진**: 문서 변환 엔진 구현
4. **업그레이드 기능**: 추가 기능 개발
5. **테스트 및 배포**: 품질 보증 및 배포 준비

## 참고 자료

- [MarkItDown GitHub](https://github.com/microsoft/markitdown)
- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Python 패키징 가이드](https://packaging.python.org/)