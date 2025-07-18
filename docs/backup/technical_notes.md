# 기술 노트 백업

## 🔧 해결된 기술적 문제들

### 1. MCP 의존성 호환성 문제

**문제 상황:**
```python
# 오류 메시지
ERROR: No matching distribution found for mcp>=1.0.0
ModuleNotFoundError: No module named 'mcp'
```

**원인 분석:**
- MCP 라이브러리가 Python 3.10+ 요구
- 개발 환경이 Python 3.9 사용
- __init__.py에서 server 모듈 import 시 전체 패키지 실패

**해결 방법:**
```python
# __init__.py 수정
# 기존 코드
from .server import MarkItDownMCPServer, create_server

# 수정된 코드
try:
    from .server import MarkItDownMCPServer, create_server
    _MCP_AVAILABLE = True
except ImportError:
    MarkItDownMCPServer = None
    create_server = None
    _MCP_AVAILABLE = False
```

**추가 조치:**
- requirements-basic.txt 생성으로 Python 3.8+ 호환성 확보
- 핵심 기능은 MCP 없이도 작동하도록 구조 개선

### 2. HTML 변환기 파라미터 충돌

**문제 상황:**
```python
# 오류 메시지
ValueError: You may specify either tags to strip or tags to convert, but not both.
```

**원인 분석:**
- markdownify 라이브러리에서 strip과 convert 파라미터 동시 사용 불가
- 라이브러리 API 변경으로 인한 호환성 문제

**해결 방법:**
```python
# 기존 코드 (문제 있음)
markdown = markdownify.markdownify(
    str(soup),
    heading_style="ATX",
    bullets="-",
    strip=['script', 'style', 'meta', 'link', 'noscript'],
    convert=['a', 'b', 'blockquote', 'br', 'code', ...]
)

# 수정된 코드
markdown = markdownify.markdownify(
    str(soup),
    heading_style="ATX",
    bullets="-"
)
```

**대안 구현:**
- BeautifulSoup만 사용하는 fallback 함수 구현
- 원하지 않는 태그는 사전에 제거

### 3. 파일 경로 인코딩 문제

**문제 상황:**
- 한글 폴더명에서 pip install 실패
- Windows/macOS 경로 처리 차이

**해결 방법:**
- Node.js 래퍼에서 상대 경로 사용
- 절대 경로 변환 로직 추가

## 🏗️ 아키텍처 설계 원칙

### 1. 우선순위 기반 변환기 시스템

```python
# 변환기 우선순위 (낮을수록 높은 우선순위)
PDF: 0.0      # 최고 우선순위
DOCX: 0.1
Image: 1.0
HTML: 2.0
Audio: 3.0
Text: 10.0    # 최저 우선순위 (fallback)
```

**장점:**
- 파일 형식별 최적 변환기 자동 선택
- 새로운 변환기 추가 시 우선순위만 설정
- fallback 메커니즘으로 안정성 확보

### 2. 스트림 기반 처리

```python
def make_stream_seekable(stream: BinaryIO) -> BinaryIO:
    """Make stream seekable for multiple reads"""
    if hasattr(stream, 'seekable') and stream.seekable():
        return stream
    
    # Copy to BytesIO for seekability
    content = stream.read()
    return io.BytesIO(content)
```

**장점:**
- 메모리 효율적인 대용량 파일 처리
- 네트워크 스트림과 로컬 파일 통일 처리
- 여러 변환기에서 동일한 스트림 재사용 가능

### 3. 한국어 최적화 구조

```python
def normalize_korean_spacing(text: str) -> str:
    """Normalize Korean text spacing"""
    # 한글과 영문/숫자 사이 공백 정규화
    text = re.sub(r'([가-힣])([a-zA-Z0-9])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z0-9])([가-힣])', r'\1 \2', text)
    return text
```

**특징:**
- EasyOCR 한국어 우선 사용
- Whisper 한국어 언어 설정
- 한국어 텍스트 간격 자동 정규화

## 🔌 플러그인 시스템 설계

### Entry Point 기반 로딩

```python
# setup.py
entry_points={
    "markitdown_mcp_converters": [
        "custom_converter = custom_package.converter:CustomConverter",
    ],
}

# 플러그인 로딩
for entry_point in pkg_resources.iter_entry_points('markitdown_mcp_converters'):
    converter_class = entry_point.load()
    converter = converter_class()
    self.register_converter(converter)
```

**장점:**
- 표준 Python 패키지 시스템 활용
- 버전 관리 및 의존성 자동 처리
- 동적 로딩으로 선택적 기능 제공

## 🌍 크로스 플랫폼 호환성

### Node.js 래퍼 구조

```javascript
// Python 자동 감지
function findPython() {
  const pythonCommands = ['python3', 'python'];
  
  for (const cmd of pythonCommands) {
    try {
      const result = execSync(`${cmd} --version`);
      if (result.includes('Python 3.')) {
        return cmd;
      }
    } catch (error) {
      // 다음 명령어 시도
    }
  }
  
  throw new Error('Python 3.8+ required');
}
```

**특징:**
- 플랫폼별 Python 명령어 자동 감지
- 의존성 자동 설치
- 환경 변수 통합 처리

### Windows 특수 처리

```powershell
# PowerShell 스크립트 (.ps1)
param(
    [switch]$Help,
    [switch]$Version
)

# 실행 정책 자동 확인
if ((Get-ExecutionPolicy) -eq "Restricted") {
    Write-Warning "PowerShell execution policy is restricted"
    Write-Host "Run: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"
}
```

**고려사항:**
- PowerShell 실행 정책 문제
- Windows Defender 스크립트 차단
- 경로 구분자 차이 (\\ vs /)

## 📊 성능 최적화

### 1. 지연 로딩 (Lazy Loading)

```python
class ImageConverter(DocumentConverter):
    def __init__(self):
        # 의존성은 실제 사용 시점에 로딩
        self._easyocr_reader = None
        
    @property
    def easyocr_reader(self):
        if self._easyocr_reader is None:
            import easyocr
            self._easyocr_reader = easyocr.Reader(['ko', 'en'])
        return self._easyocr_reader
```

**장점:**
- 초기 로딩 시간 단축
- 미사용 기능의 메모리 절약
- 선택적 의존성 처리

### 2. 캐싱 전략

```python
@lru_cache(maxsize=128)
def detect_file_type(file_signature: bytes) -> str:
    """Cache file type detection results"""
    return _detect_from_signature(file_signature)
```

**적용 영역:**
- 파일 형식 감지 결과
- 변환기 등록 정보
- 설정 파일 파싱 결과

## 🔍 디버깅 및 로깅

### 구조화된 로깅

```python
logger = logging.getLogger(__name__)

def convert(self, file_stream, stream_info, **kwargs):
    logger.info(f"Converting {stream_info.filename} with {self.__class__.__name__}")
    
    try:
        result = self._do_conversion(file_stream, stream_info)
        logger.debug(f"Conversion successful: {len(result.markdown)} characters")
        return result
    except Exception as e:
        logger.error(f"Conversion failed: {e}", exc_info=True)
        raise
```

**로그 레벨:**
- DEBUG: 상세한 처리 과정
- INFO: 주요 작업 진행 상황
- WARNING: 복구 가능한 문제
- ERROR: 변환 실패 및 예외

## 🧪 테스트 전략

### 단위 테스트 구조

```python
def test_text_converter():
    converter = TextConverter(korean_support=True)
    
    # 한국어 텍스트 테스트
    test_content = "테스트 제목\n\n한국어 내용입니다."
    stream = io.BytesIO(test_content.encode('utf-8'))
    stream_info = StreamInfo(extension='.txt')
    
    result = converter.convert(stream, stream_info)
    
    assert result.title == "테스트 제목"
    assert "한국어 내용" in result.markdown
```

**테스트 범위:**
- 각 변환기별 기본 기능
- 한국어 텍스트 처리
- 오류 상황 처리
- 크로스 플랫폼 호환성

---

**기술 노트 작성일**: 2025-07-18
**프로젝트**: Voidlight 마크다운 MCP 서버
**상태**: 모든 문제 해결 완료