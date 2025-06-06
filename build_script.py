#!/usr/bin/env python3
"""
Vertex AI Imagen 패키지 빌드 및 PyPI 배포 스크립트
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv가 설치되지 않았습니다. pip install python-dotenv")
    print("   환경 변수를 수동으로 설정해주세요.")

def run_command(cmd, description="", check=True):
    """명령어 실행"""
    print(f"📋 {description}")
    print(f"🔧 실행: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"❌ 실패: {result.stderr}")
        if not input("계속 진행하시겠습니까? (y/N): ").lower().startswith('y'):
            sys.exit(1)
        return False
    else:
        print(f"✅ 성공")
        if result.stdout.strip():
            # 긴 출력은 줄여서 표시
            output = result.stdout.strip()
            if len(output) > 300:
                output = output[:300] + "..."
            print(f"📄 출력: {output}")
    print()
    return True

def clean_build():
    """빌드 디렉토리 정리"""
    print("🧹 빌드 디렉토리 정리...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info", "**/__pycache__"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"   🗑️  {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"   🗑️  {path}")
                path.unlink()
    
    # src 디렉토리 내 egg-info도 정리
    for path in Path("src").glob("*.egg-info"):
        if path.is_dir():
            print(f"   🗑️  {path}")
            shutil.rmtree(path)
    print()

def check_requirements():
    """필수 도구 확인"""
    print("🔍 필수 도구 확인...")
    
    required_tools = [
        ("python", "Python 인터프리터"),
        ("pip", "Python 패키지 관리자"),
        ("git", "Git 버전 관리")
    ]
    
    for tool, desc in required_tools:
        result = subprocess.run(f"which {tool}", shell=True, capture_output=True)
        if result.returncode != 0:
            print(f"❌ {tool}이 설치되지 않았습니다 ({desc})")
            sys.exit(1)
        else:
            print(f"✅ {tool} 확인됨")
    print()

def install_build_tools():
    """빌드 도구 설치"""
    print("🔧 빌드 도구 설치...")
    tools = ["build", "twine", "wheel", "setuptools"]
    for tool in tools:
        run_command(f"pip install --upgrade {tool}", f"{tool} 설치/업그레이드")

def build_package():
    """패키지 빌드"""
    print("📦 패키지 빌드...")
    return run_command("python -m build", "패키지 빌드 실행")

def check_package():
    """패키지 검증"""
    print("🔍 패키지 검증...")
    return run_command("python -m twine check dist/*", "패키지 검증")

def show_results():
    """결과 표시"""
    print("📊 빌드 결과:")
    dist_path = Path("dist")
    if dist_path.exists():
        total_size = 0
        for file in dist_path.iterdir():
            size = file.stat().st_size
            total_size += size
            print(f"   📄 {file.name} ({size:,} bytes)")
        print(f"   📦 총 크기: {total_size:,} bytes")
    print()

def test_local_install():
    """로컬 설치 테스트"""
    print("🧪 로컬 설치 테스트...")
    
    # wheel 파일 찾기
    wheel_files = list(Path("dist").glob("*.whl"))
    if not wheel_files:
        print("❌ wheel 파일을 찾을 수 없습니다")
        return False
    
    wheel_file = wheel_files[0]
    
    # 테스트 환경에서 설치
    print(f"   📦 설치: {wheel_file}")
    success = run_command(f"pip install --force-reinstall {wheel_file}", "패키지 설치", check=False)
    
    if success:
        # import 테스트
        test_cmd = (
            "python -c \"import vertex_ai_imagen; "
            "print(f'✅ 버전: {vertex_ai_imagen.__version__}'); "
            "from vertex_ai_imagen import ImagenClient; "
            "print('✅ 모든 클래스 import 성공')\""
        )
        return run_command(test_cmd, "패키지 import 테스트", check=False)
    
    return False

def upload_to_pypi(test_only=False):
    """PyPI 업로드"""
    repository = "testpypi" if test_only else "pypi"
    repo_name = "Test PyPI" if test_only else "PyPI"
    
    print(f"📤 {repo_name} 업로드...")
    
    # .env에서 API 토큰 읽기
    token_env = "TESTPYPI_API_TOKEN" if test_only else "PYPI_API_TOKEN"
    api_token = os.getenv(token_env)
    
    if api_token and api_token != "pypi-your-api-token-here" and api_token != "pypi-your-test-api-token-here":
        print(f"   🔑 환경 변수에서 API 토큰 확인됨 ({token_env})")
        username = "__token__"
        password = api_token
    else:
        print(f"   ⚠️  {token_env} 토큰이 설정되지 않았습니다")
        print(f"   💡 다음 중 하나를 선택하세요:")
        print(f"   1. .env 파일에 실제 토큰 설정")
        print(f"   2. 수동 인증으로 진행")
        
        choice = input("   토큰을 직접 입력하시겠습니까? (y/N): ").lower().strip()
        
        if choice.startswith('y'):
            print(f"\n   🔑 {repo_name} API 토큰을 입력하세요:")
            print(f"   토큰 생성: https://{'test.' if test_only else ''}pypi.org/manage/account/token/")
            try:
                import getpass
                api_token = getpass.getpass("   API 토큰: ").strip()
                if api_token:
                    username = "__token__"
                    password = api_token
                    print("   ✅ 토큰 입력 완료")
                else:
                    print("   ❌ 토큰이 입력되지 않았습니다. 수동 인증으로 진행합니다.")
                    username = None
                    password = None
            except KeyboardInterrupt:
                print("\n   ❌ 업로드 취소됨")
                return False
        else:
            print("   🔐 수동 인증으로 진행합니다 (사용자명/비밀번호 입력 필요)")
            username = None
            password = None
    
    if test_only:
        cmd_base = "python -m twine upload --repository testpypi"
        print("   ⚠️  Test PyPI에 업로드합니다 (테스트 목적)")
    else:
        cmd_base = "python -m twine upload"
        print("   🚨 실제 PyPI에 업로드합니다!")
        confirm = input("   정말 진행하시겠습니까? (yes 입력): ")
        if confirm != "yes":
            print("   ❌ 업로드 취소됨")
            return False
    
    # 토큰이 있으면 자동 인증, 없으면 수동 인증
    if username and password:
        # 보안을 위해 토큰을 직접 파라미터로 전달하지 않고 환경 변수 사용
        env = os.environ.copy()
        env['TWINE_USERNAME'] = username
        env['TWINE_PASSWORD'] = password
        cmd = f"{cmd_base} dist/*"
        print("   🔐 자동 인증으로 업로드")
        
        # 환경 변수를 사용한 실행
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✅ 성공")
            if result.stdout.strip():
                output = result.stdout.strip()
                if len(output) > 300:
                    output = output[:300] + "..."
                print(f"📄 출력: {output}")
            return True
        else:
            print(f"❌ 실패: {result.stderr}")
            return False
    else:
        cmd = f"{cmd_base} dist/*"
        print("   🔐 수동 인증 필요 (사용자명/비밀번호 입력)")
        return run_command(cmd, f"{repo_name} 업로드 실행", check=False)

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Vertex AI Imagen 패키지 빌드 및 배포")
    parser.add_argument("--upload", choices=["test", "prod"], help="PyPI 업로드 (test: TestPyPI, prod: 실제 PyPI)")
    parser.add_argument("--no-test", action="store_true", help="로컬 설치 테스트 건너뛰기")
    parser.add_argument("--clean-only", action="store_true", help="빌드 파일만 정리하고 종료")
    
    args = parser.parse_args()
    
    print("🚀 Vertex AI Imagen 패키지 빌드 및 배포 시작\n")
    
    # 1. 환경 확인
    check_requirements()
    
    # 2. 빌드 도구 설치
    install_build_tools()
    
    # 3. 이전 빌드 정리
    clean_build()
    
    if args.clean_only:
        print("🧹 정리 완료!")
        return
    
    # 4. 패키지 빌드
    if not build_package():
        print("❌ 빌드 실패")
        return
    
    # 5. 패키지 검증
    if not check_package():
        print("❌ 패키지 검증 실패")
        return
    
    # 6. 결과 표시
    show_results()
    
    # 7. 로컬 설치 테스트
    if not args.no_test:
        if not test_local_install():
            print("⚠️  로컬 테스트 실패, 계속 진행...")
    
    # 8. PyPI 업로드
    if args.upload:
        test_only = args.upload == "test"
        if upload_to_pypi(test_only):
            repo_name = "Test PyPI" if test_only else "PyPI"
            print(f"🎉 {repo_name} 업로드 성공!")
            
            if test_only:
                print("\n📋 테스트 설치 명령어:")
                print("   pip install --index-url https://test.pypi.org/simple/ vertex-ai-imagen")
            else:
                print("\n📋 설치 명령어:")
                print("   pip install vertex-ai-imagen")
        else:
            print("❌ 업로드 실패")
            return
    
    print("\n🎉 모든 작업 완료!")
    
    if not args.upload:
        print("\n📤 수동 업로드 명령어:")
        print("   테스트: python -m twine upload --repository testpypi dist/*")
        print("   실제:   python -m twine upload dist/*")
        print("\n📋 자동 업로드:")
        print("   테스트: python build_script.py --upload test")
        print("   실제:   python build_script.py --upload prod")

if __name__ == "__main__":
    main() 