# 문서 폴더 안내

이 폴더에는 Voidlight 마크다운 MCP 서버 프로젝트의 모든 개발 과정과 대화 내용이 보관되어 있습니다.

## 📁 파일 구조

### 메인 문서
- **PROJECT_HISTORY.md**: 전체 프로젝트 개발 과정 기록

### 백업 폴더 (`backup/`)
- **conversation_backup.txt**: 사용자와의 전체 대화 내용 텍스트 백업
- **technical_notes.md**: 해결된 기술적 문제들과 아키텍처 설계 노트
- **claude_desktop_setup_backup.json**: Claude Desktop 설정 모든 옵션 백업
- **quick_reference.md**: 빠른 참조 가이드 (설치, 사용법, 문제해결)

## 📅 생성 일시
- **날짜**: 2025-07-18
- **프로젝트**: Microsoft MarkItDown 벤치마킹 MCP 서버
- **개발자**: Voidlight + Claude Code 협업

## 🎯 주요 내용

### 개발 과정
1. **기본 구조 설계**: 6개 변환기, 플러그인 시스템
2. **MCP 서버 통합**: 5개 도구, Claude Desktop 호환
3. **NPX 통합**: 한 줄 설치 지원
4. **Windows 지원**: 크로스 플랫폼 완성
5. **검증 및 버그 수정**: 모든 오류 해결

### 해결된 문제들
- MCP 의존성 호환성 문제
- HTML 변환기 파라미터 충돌
- 파일 경로 인코딩 이슈

### 최종 성과
- ✅ 완전한 기능 구현 및 테스트
- ✅ 크로스 플랫폼 지원
- ✅ Claude Desktop 완벽 통합
- ✅ 한국어 특화 기능
- ✅ npx 한 줄 설치

## 🔄 활용 방법

### 미래 개발 참조
- 기술적 문제 해결 방법 참조
- 아키텍처 설계 원칙 적용
- 사용자 피드백 반영 사례 학습

### 문제 해결
- 오류 발생 시 technical_notes.md 참조
- 설치 문제 시 quick_reference.md 확인
- 전체 맥락은 conversation_backup.txt 참조

### 새로운 기능 추가
- PROJECT_HISTORY.md에서 확장 계획 확인
- 플러그인 시스템 활용 방법 참조
- 한국어 지원 강화 방법 적용

## 🔗 관련 파일들

### 프로젝트 루트
- `README.md`: 프로젝트 기본 설명
- `CLAUDE_DESKTOP_SETUP.md`: Claude Desktop 설정 가이드
- `WINDOWS_SETUP.md`: Windows 설치 가이드
- `DEVELOPMENT_LOG.md`: 개발 로그 (GitHub 버전)
- `CONVERSATION_SUMMARY.md`: 대화 요약 (GitHub 버전)

### 소스 코드
- `src/markitdown_mcp_enhanced/`: 전체 Python 소스 코드
- `bin/`: Node.js 래퍼 스크립트들
- `requirements.txt`: Python 의존성

## 💾 백업 정책

### 로컬 백업
- 이 `docs/` 폴더: 프로젝트와 함께 로컬 보관
- 다양한 형식으로 중복 저장 (MD, TXT, JSON)

### 원격 백업
- GitHub Private Repository: 버전 관리와 함께 안전 보관
- 커밋 히스토리: 모든 변경 과정 추적 가능

## 📞 문의
프로젝트 관련 문의나 추가 개발이 필요한 경우, 이 문서들을 참조하여 전체 맥락을 파악한 후 진행하시기 바랍니다.

---
**마지막 업데이트**: 2025-07-18  
**프로젝트 상태**: ✅ 완료 (운영 준비됨)  
**GitHub**: https://github.com/VoidLight00/voidlight-markdown-mcp-server (Private)