# Windows 서버 설정 가이드

## 🖥️ 다른 Windows PC에서 MCP 서버 실행하기

이 가이드는 다른 Windows 컴퓨터에서 Voidlight 마크다운 MCP 서버를 설치하고 실행하는 방법을 설명합니다.

## 📋 사전 요구사항

### 1. 필수 소프트웨어 설치

#### Node.js 설치
1. **Node.js 다운로드**: https://nodejs.org/
2. **LTS 버전 선택** (권장)
3. **설치 과정에서 "Add to PATH" 체크**
4. **설치 확인**:
   ```cmd
   node --version
   npm --version
   ```

#### Python 설치
1. **Python 다운로드**: https://www.python.org/downloads/
2. **Python 3.8 이상 버전 선택**
3. **설치 시 중요 옵션**:
   - ✅ "Add Python to PATH" 체크
   - ✅ "Install pip" 체크
4. **설치 확인**:
   ```cmd
   python --version
   pip --version
   ```

## 🚀 설치 방법

### 방법 1: NPX로 자동 설치 (권장)

#### 1-1. 명령 프롬프트에서
```cmd
npx markitdown-mcp-enhanced
```

#### 1-2. PowerShell에서
```powershell
npx markitdown-mcp-enhanced
```

### 방법 2: GitHub에서 직접 다운로드

#### 2-1. 저장소 복제 (Git 필요)
```cmd
git clone https://github.com/VoidLight00/voidlight-markdown-mcp-server.git
cd voidlight-markdown-mcp-server
```

#### 2-2. ZIP 다운로드
1. GitHub 저장소에서 "Code" → "Download ZIP"
2. 압축 해제 후 폴더로 이동

#### 2-3. 의존성 설치
```cmd
npm install
pip install -r requirements.txt
```

## ⚙️ Claude Desktop 설정

### 1. Claude Desktop 설치
1. **Claude Desktop 다운로드**: https://claude.ai/download
2. **Windows 버전 설치**
3. **계정 로그인**

### 2. 설정 파일 편집

#### 2-1. 설정 파일 위치
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### 2-2. 파일 열기 방법
**방법 A: 명령 프롬프트**
```cmd
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**방법 B: 파일 탐색기**
1. `Win + R` → `%APPDATA%\Claude` 입력
2. `claude_desktop_config.json` 파일 메모장으로 열기

#### 2-3. 설정 내용 추가
```json
{
  "mcpServers": {
    "markitdown-mcp-enhanced": {
      "command": "npx",
      "args": ["markitdown-mcp-enhanced"],
      "env": {
        "KOREAN_SUPPORT": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Claude Desktop 재시작
- Claude Desktop 완전 종료 후 재시작
- 시스템 트레이에서도 완전히 종료 확인

## 🔧 고급 설정

### API 키 설정 (선택사항)

#### OpenAI API 키 (이미지 설명)
```json
{
  "mcpServers": {
    "markitdown-mcp-enhanced": {
      "command": "npx",
      "args": ["markitdown-mcp-enhanced"],
      "env": {
        "KOREAN_SUPPORT": "true",
        "LOG_LEVEL": "INFO",
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

#### Azure Document Intelligence (고급 PDF 처리)
```json
{
  "env": {
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "your-endpoint",
    "AZURE_DOCUMENT_INTELLIGENCE_KEY": "your-key"
  }
}
```

### 환경 변수 설정

#### 시스템 환경 변수 (영구 설정)
1. `Win + X` → "시스템"
2. "고급 시스템 설정"
3. "환경 변수"
4. "새로 만들기"에서 추가:
   - `KOREAN_SUPPORT` = `true`
   - `OPENAI_API_KEY` = `your-key`

#### PowerShell 세션 변수 (임시 설정)
```powershell
$env:KOREAN_SUPPORT = "true"
$env:OPENAI_API_KEY = "your-api-key"
```

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. "npx를 찾을 수 없습니다"
**원인**: Node.js가 설치되지 않았거나 PATH에 없음  
**해결**:
```cmd
# Node.js 설치 확인
node --version

# PATH 확인
echo %PATH%

# Node.js 재설치 (PATH 포함)
```

#### 2. "Python을 찾을 수 없습니다"
**원인**: Python이 설치되지 않았거나 PATH에 없음  
**해결**:
```cmd
# Python 설치 확인
python --version
py --version

# PATH에 Python 추가 또는 재설치
```

#### 3. PowerShell 실행 정책 오류
**오류**: `이 시스템에서 스크립트를 실행할 수 없습니다`  
**해결**:
```powershell
# 현재 정책 확인
Get-ExecutionPolicy

# 정책 변경 (관리자 권한)
Set-ExecutionPolicy RemoteSigned

# 현재 사용자만 변경
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 임시 우회 (현재 세션만)
Set-ExecutionPolicy Bypass -Scope Process
```

#### 4. Windows Defender 차단
**증상**: 스크립트 실행이 차단됨  
**해결**:
1. Windows Defender → "바이러스 및 위협 방지"
2. "바이러스 및 위협 방지 설정 관리"
3. "제외 항목 추가 또는 제거"
4. 프로젝트 폴더를 제외 목록에 추가

#### 5. 방화벽 문제
**증상**: 네트워크 연결 실패  
**해결**:
1. Windows Defender 방화벽
2. "앱 또는 기능이 Windows Defender 방화벽을 통과하도록 허용"
3. Node.js와 Python 허용

### 디버깅 방법

#### 1. 상세 로그 확인
```json
{
  "env": {
    "LOG_LEVEL": "DEBUG"
  }
}
```

#### 2. 수동 테스트
```cmd
# 버전 확인
npx markitdown-mcp-enhanced --version

# 도움말 확인
npx markitdown-mcp-enhanced --help

# 직접 실행 (프로젝트 폴더에서)
node bin\markitdown-mcp-enhanced.js --version
```

#### 3. Claude Desktop 로그 확인
**로그 위치**:
```
%APPDATA%\Claude\logs\mcp.log
```

**로그 보기**:
```cmd
type %APPDATA%\Claude\logs\mcp.log
```

## 🌐 네트워크 환경별 설정

### 회사/학교 네트워크 (프록시 환경)

#### NPM 프록시 설정
```cmd
npm config set proxy http://proxy-server:port
npm config set https-proxy http://proxy-server:port
```

#### Python pip 프록시 설정
```cmd
pip install --proxy http://proxy-server:port package-name
```

### 방화벽이 엄격한 환경

#### 오프라인 설치 패키지 준비
1. 인터넷 연결된 PC에서 의존성 다운로드
2. 오프라인 PC로 전송
3. 로컬 설치 실행

## 📊 성능 최적화

### Windows 특화 최적화

#### 1. Windows Terminal 사용
- 기본 cmd보다 성능 우수
- UTF-8 인코딩 지원
- 한국어 표시 개선

#### 2. SSD 사용 권장
- 파일 읽기/쓰기 성능 향상
- 변환 속도 개선

#### 3. 메모리 최적화
```json
{
  "env": {
    "NODE_OPTIONS": "--max_old_space_size=4096"
  }
}
```

## 🔒 보안 고려사항

### 1. API 키 보안
- 환경 변수 사용 (설정 파일에 직접 입력 금지)
- 키 파일 별도 보관
- 정기적 키 교체

### 2. 네트워크 보안
- HTTPS 연결 확인
- 신뢰할 수 없는 URL 변환 주의
- 방화벽 예외 최소화

### 3. 파일 보안
- 민감한 문서 변환 시 주의
- 임시 파일 자동 삭제 확인
- 로그 파일 정기 정리

## 📱 사용 예시

### Claude Desktop에서 테스트

#### 1. 기본 기능 테스트
```
지원되는 파일 형식을 알려주세요
```

#### 2. 파일 변환 테스트
```
C:\Users\사용자명\Documents\테스트.pdf 파일을 마크다운으로 변환해주세요
```

#### 3. 한국어 기능 테스트
```
한국어가 포함된 이미지에서 텍스트를 추출해주세요: C:\Users\사용자명\Pictures\한글이미지.jpg
```

## 📞 지원 및 문의

### 자주 묻는 질문
1. **Q**: 인터넷 없이 사용 가능한가요?  
   **A**: 초기 설치 후에는 오프라인 사용 가능 (API 기능 제외)

2. **Q**: 회사 PC에서 관리자 권한 없이 설치 가능한가요?  
   **A**: npx 사용 시 사용자 권한으로 설치 가능

3. **Q**: 여러 사용자가 동시 사용 가능한가요?  
   **A**: 각 사용자별로 개별 설치 필요

### 문제 신고
- **GitHub Issues**: https://github.com/VoidLight00/voidlight-markdown-mcp-server/issues
- **문제 신고 시 포함 정보**:
  - Windows 버전
  - Node.js/Python 버전
  - 오류 메시지 전문
  - 실행 환경 (회사/개인 PC 등)

---

**가이드 업데이트**: 2025-07-18  
**지원 Windows 버전**: Windows 10/11  
**테스트 완료**: ✅ 다양한 Windows 환경에서 검증