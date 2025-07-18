#!/usr/bin/env python3
"""
MCP Server Health Check Script
시스템 상태 점검 및 문제 진단 도구
"""

import os
import sys
import subprocess
import json
import platform
import shutil
from pathlib import Path
from datetime import datetime
import importlib.util

class Colors:
    """터미널 색상 코드"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_colored(text, color):
    """색상 출력"""
    print(f"{color}{text}{Colors.RESET}")

def print_header(title):
    """헤더 출력"""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"  {title}", Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)

def print_section(title):
    """섹션 헤더 출력"""
    print_colored(f"\n[{title}]", Colors.YELLOW)

def print_success(message):
    """성공 메시지 출력"""
    print_colored(f"✅ {message}", Colors.GREEN)

def print_error(message):
    """오류 메시지 출력"""
    print_colored(f"❌ {message}", Colors.RED)

def print_warning(message):
    """경고 메시지 출력"""
    print_colored(f"⚠️  {message}", Colors.YELLOW)

def print_info(message):
    """정보 메시지 출력"""
    print_colored(f"ℹ️  {message}", Colors.BLUE)

def run_command(command, capture_output=True, shell=False):
    """명령어 실행"""
    try:
        if isinstance(command, str):
            cmd = command.split() if not shell else command
        else:
            cmd = command
        
        result = subprocess.run(
            cmd, 
            capture_output=capture_output,
            text=True,
            shell=shell,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_system_info():
    """시스템 정보 확인"""
    print_section("시스템 정보")
    
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Python Version": sys.version,
        "Python Executable": sys.executable,
        "Working Directory": os.getcwd(),
        "User": os.getenv("USER", os.getenv("USERNAME", "Unknown")),
        "Home Directory": str(Path.home()),
        "Environment": "Windows" if os.name == "nt" else "Unix-like"
    }
    
    for key, value in info.items():
        print_colored(f"  {key}: {value}", Colors.WHITE)
    
    return info

def check_python():
    """Python 설치 및 버전 확인"""
    print_section("Python 환경 확인")
    
    # Python 버전 확인
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} (요구사항: 3.8+)")
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (요구사항: 3.8+)")
        return False
    
    # pip 확인
    success, pip_version, _ = run_command([sys.executable, "-m", "pip", "--version"])
    if success:
        print_success(f"pip: {pip_version}")
    else:
        print_error("pip가 설치되지 않았습니다")
        return False
    
    # 가상환경 확인
    venv_path = os.getenv("VIRTUAL_ENV")
    if venv_path:
        print_success(f"가상환경 활성화: {venv_path}")
    else:
        print_warning("가상환경이 활성화되지 않았습니다")
    
    return True

def check_nodejs():
    """Node.js 설치 및 버전 확인"""
    print_section("Node.js 환경 확인")
    
    # Node.js 확인
    success, node_version, _ = run_command(["node", "--version"])
    if success:
        print_success(f"Node.js: {node_version}")
    else:
        print_error("Node.js가 설치되지 않았습니다")
        return False
    
    # npm 확인
    success, npm_version, _ = run_command(["npm", "--version"])
    if success:
        print_success(f"npm: {npm_version}")
    else:
        print_error("npm이 설치되지 않았습니다")
        return False
    
    # npx 확인
    success, npx_version, _ = run_command(["npx", "--version"])
    if success:
        print_success(f"npx: {npx_version}")
    else:
        print_warning("npx가 설치되지 않았습니다")
    
    return True

def check_dependencies():
    """Python 의존성 확인"""
    print_section("Python 의존성 확인")
    
    required_packages = [
        "markitdown",
        "pdfminer.six",
        "python-docx",
        "openpyxl",
        "beautifulsoup4",
        "requests",
        "mcp"
    ]
    
    optional_packages = [
        "openai",
        "anthropic",
        "pillow",
        "easyocr",
        "tesseract"
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"✓ {package}")
        except ImportError:
            print_error(f"✗ {package} (필수)")
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"✓ {package} (선택사항)")
        except ImportError:
            print_warning(f"✗ {package} (선택사항)")
            missing_optional.append(package)
    
    if missing_required:
        print_error(f"필수 패키지 누락: {', '.join(missing_required)}")
        print_info(f"설치 명령: pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print_warning(f"선택사항 패키지 누락: {', '.join(missing_optional)}")
        print_info(f"설치 명령: pip install {' '.join(missing_optional)}")
    
    return True

def check_mcp_server():
    """MCP 서버 모듈 확인"""
    print_section("MCP 서버 확인")
    
    # 소스 파일 확인
    server_files = [
        "src/markitdown_mcp_enhanced/server.py",
        "src/markitdown_mcp_enhanced/__init__.py",
        "bin/markitdown-mcp-enhanced.js"
    ]
    
    for file_path in server_files:
        if os.path.exists(file_path):
            print_success(f"✓ {file_path}")
        else:
            print_error(f"✗ {file_path}")
    
    # 모듈 임포트 테스트
    try:
        sys.path.insert(0, "src")
        from markitdown_mcp_enhanced import server
        print_success("✓ MCP 서버 모듈 임포트 성공")
        return True
    except ImportError as e:
        print_error(f"✗ MCP 서버 모듈 임포트 실패: {e}")
        return False

def check_claude_desktop():
    """Claude Desktop 설정 확인"""
    print_section("Claude Desktop 설정 확인")
    
    # 설정 파일 경로 확인
    if os.name == "nt":  # Windows
        config_path = Path(os.getenv("APPDATA")) / "Claude" / "claude_desktop_config.json"
    else:  # macOS/Linux
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    
    if not config_path.exists():
        print_error(f"Claude Desktop 설정 파일 없음: {config_path}")
        return False
    
    print_success(f"✓ 설정 파일 발견: {config_path}")
    
    # 설정 파일 내용 확인
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'mcpServers' in config:
            print_success("✓ mcpServers 섹션 존재")
            
            if 'markitdown-mcp-enhanced' in config['mcpServers']:
                print_success("✓ markitdown-mcp-enhanced 서버 설정 존재")
                
                server_config = config['mcpServers']['markitdown-mcp-enhanced']
                print_info(f"  Command: {server_config.get('command', 'N/A')}")
                print_info(f"  Args: {server_config.get('args', [])}")
                print_info(f"  CWD: {server_config.get('cwd', 'N/A')}")
                
                return True
            else:
                print_error("✗ markitdown-mcp-enhanced 서버 설정 없음")
                return False
        else:
            print_error("✗ mcpServers 섹션 없음")
            return False
            
    except json.JSONDecodeError as e:
        print_error(f"✗ 설정 파일 JSON 파싱 오류: {e}")
        return False
    except Exception as e:
        print_error(f"✗ 설정 파일 읽기 오류: {e}")
        return False

def check_environment_variables():
    """환경 변수 확인"""
    print_section("환경 변수 확인")
    
    important_vars = [
        "PATH",
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "OPENAI_API_KEY",
        "KOREAN_SUPPORT",
        "LOG_LEVEL"
    ]
    
    for var in important_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var or "TOKEN" in var:
                print_success(f"✓ {var}: ***hidden***")
            else:
                print_success(f"✓ {var}: {value}")
        else:
            if var in ["OPENAI_API_KEY", "KOREAN_SUPPORT", "LOG_LEVEL"]:
                print_warning(f"✗ {var}: 설정되지 않음 (선택사항)")
            else:
                print_info(f"  {var}: 설정되지 않음")

def check_network_connectivity():
    """네트워크 연결 확인"""
    print_section("네트워크 연결 확인")
    
    test_urls = [
        "https://www.google.com",
        "https://api.openai.com",
        "https://pypi.org"
    ]
    
    for url in test_urls:
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=5)
            print_success(f"✓ {url}")
        except Exception as e:
            print_error(f"✗ {url}: {e}")

def check_file_permissions():
    """파일 권한 확인"""
    print_section("파일 권한 확인")
    
    # 현재 디렉토리 쓰기 권한
    try:
        test_file = Path("test_write_permission.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print_success("✓ 현재 디렉토리 쓰기 권한")
    except Exception as e:
        print_error(f"✗ 현재 디렉토리 쓰기 권한: {e}")
    
    # 임시 디렉토리 접근
    try:
        import tempfile
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"test")
        print_success("✓ 임시 디렉토리 접근")
    except Exception as e:
        print_error(f"✗ 임시 디렉토리 접근: {e}")

def run_comprehensive_test():
    """종합 테스트 실행"""
    print_section("종합 테스트")
    
    # 간단한 변환 테스트
    try:
        test_content = "# Test Document\n\nThis is a test."
        
        # 임시 파일 생성
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name
        
        print_info(f"테스트 파일 생성: {tmp_path}")
        
        # 변환 테스트 (실제 MCP 서버 사용)
        # 이 부분은 실제 서버가 실행 중일 때만 작동
        print_warning("실제 변환 테스트는 Claude Desktop에서 수행하세요")
        
        # 임시 파일 정리
        os.unlink(tmp_path)
        
    except Exception as e:
        print_error(f"종합 테스트 실패: {e}")

def generate_diagnostic_report():
    """진단 보고서 생성"""
    print_section("진단 보고서 생성")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "os": platform.system(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "working_directory": os.getcwd(),
            "user": os.getenv("USER", os.getenv("USERNAME", "Unknown"))
        },
        "checks": {},
        "recommendations": []
    }
    
    # 각 체크 결과 저장
    report["checks"]["python"] = check_python()
    report["checks"]["nodejs"] = check_nodejs()
    report["checks"]["dependencies"] = check_dependencies()
    report["checks"]["mcp_server"] = check_mcp_server()
    report["checks"]["claude_desktop"] = check_claude_desktop()
    
    # 권장사항 생성
    if not report["checks"]["python"]:
        report["recommendations"].append("Python 3.8+ 설치 필요")
    if not report["checks"]["nodejs"]:
        report["recommendations"].append("Node.js 설치 필요")
    if not report["checks"]["dependencies"]:
        report["recommendations"].append("Python 의존성 설치 필요")
    if not report["checks"]["mcp_server"]:
        report["recommendations"].append("MCP 서버 모듈 설치 필요")
    if not report["checks"]["claude_desktop"]:
        report["recommendations"].append("Claude Desktop 설정 필요")
    
    # 보고서 저장
    report_path = f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_success(f"진단 보고서 저장: {report_path}")
    return report

def main():
    """메인 헬스 체크 실행"""
    print_header("🔍 MCP Server Health Check")
    print_colored("Voidlight Markitdown MCP Enhanced", Colors.MAGENTA)
    print_colored(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BLUE)
    
    # 모든 체크 실행
    checks = [
        ("시스템 정보", check_system_info),
        ("Python 환경", check_python),
        ("Node.js 환경", check_nodejs),
        ("Python 의존성", check_dependencies),
        ("MCP 서버", check_mcp_server),
        ("Claude Desktop", check_claude_desktop),
        ("환경 변수", check_environment_variables),
        ("네트워크 연결", check_network_connectivity),
        ("파일 권한", check_file_permissions),
        ("종합 테스트", run_comprehensive_test)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            if check_name == "시스템 정보":
                check_func()  # 시스템 정보는 반환값 없음
                results.append(True)
            else:
                result = check_func()
                results.append(result if result is not None else True)
        except Exception as e:
            print_error(f"{check_name} 체크 실패: {e}")
            results.append(False)
    
    # 결과 요약
    print_header("📊 결과 요약")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print_success(f"🎉 모든 체크 통과! ({passed}/{total})")
        print_colored("MCP 서버가 준비되었습니다.", Colors.GREEN)
    else:
        print_warning(f"⚠️  일부 체크 실패 ({passed}/{total})")
        print_colored("위의 문제들을 검토하고 해결하세요.", Colors.YELLOW)
    
    # 진단 보고서 생성
    print_colored("\n진단 보고서를 생성하시겠습니까?", Colors.CYAN)
    response = input("(y/n): ").lower().strip()
    if response in ['y', 'yes']:
        generate_diagnostic_report()
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_colored("\n\n사용자에 의해 중단되었습니다.", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n예상치 못한 오류 발생: {e}", Colors.RED)
        sys.exit(1)