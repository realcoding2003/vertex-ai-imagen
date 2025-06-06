#!/usr/bin/env python3
"""
Vertex AI Imagen 실제 이미지 생성 테스트
"""

import asyncio
import os
from pathlib import Path
from vertex_ai_imagen import ImagenClient

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv가 설치되지 않았습니다. pip install python-dotenv")

# 설정 (.env에서 우선 읽고, 없으면 기본값 사용)
CREDENTIALS_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", 
    "/Users/kevinpark/Downloads/gen-lang-client-0205070035-411d73857186.json"
)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0205070035")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "../generated_images")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")

async def test_image_generation():
    """이미지 생성 테스트"""
    print("🎨 Vertex AI Imagen 테스트 시작\n")
    
    try:
        # 1. 클라이언트 초기화
        print("📋 1. 클라이언트 초기화 중...")
        client = ImagenClient(project_id=PROJECT_ID, location=LOCATION)
        print(f"   ✅ 프로젝트 ID: {PROJECT_ID}")
        print(f"   ✅ 리전: {LOCATION}")
        
        # 2. 인증 설정
        print("🔐 2. GCP 인증 설정 중...")
        print(f"   📁 인증 파일: {CREDENTIALS_PATH}")
        
        # 환경 변수가 설정되어 있으면 환경 변수 인증 시도
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                success = client.setup_credentials_from_env()
                if success:
                    print("   ✅ 환경 변수로 인증 성공!")
                else:
                    raise Exception("환경 변수 인증 실패")
            except Exception as e:
                print(f"   ⚠️  환경 변수 인증 실패: {e}")
                print("   🔄 파일 인증으로 재시도...")
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {CREDENTIALS_PATH}")
                success = client.setup_credentials(CREDENTIALS_PATH)
                if success:
                    print("   ✅ 파일로 인증 성공!")
                else:
                    raise Exception("파일 인증 실패")
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {CREDENTIALS_PATH}")
            success = client.setup_credentials(CREDENTIALS_PATH)
            if success:
                print("   ✅ 파일로 인증 성공!")
            else:
                raise Exception("파일 인증 실패")
        
        # 3. 출력 디렉토리 생성
        print("📁 3. 출력 디렉토리 생성...")
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        print(f"   ✅ 디렉토리: {OUTPUT_DIR}")
        
        # 4. 간단한 이미지 생성 테스트
        print("🎯 4. 이미지 생성 테스트...")
        prompt = "A beautiful sunset over the ocean with waves"
        print(f"   📝 프롬프트: {prompt}")
        
        print("   ⏳ 이미지 생성 중... (시간이 걸릴 수 있습니다)")
        
        image = await client.generate(
            prompt=prompt,
            model="imagegeneration@006",
            aspect_ratio="16:9",
            count=1
        )
        
        print("   ✅ 이미지 생성 완료!")
        
        # 5. 이미지 저장
        print("💾 5. 이미지 저장...")
        filename = f"{OUTPUT_DIR}/test_sunset.png"
        image.save(filename)
        
        print(f"   ✅ 저장 완료: {filename}")
        print(f"   📊 파일 크기: {image.size:,} bytes")
        if image.enhanced_prompt != image.prompt:
            print(f"   ✨ 개선된 프롬프트: {image.enhanced_prompt}")
        
        # 6. 다중 이미지 생성 테스트
        print("\n🎨 6. 다중 이미지 생성 테스트...")
        prompt2 = "A cute cat playing with a ball"
        print(f"   📝 프롬프트: {prompt2}")
        
        images = await client.generate(
            prompt=prompt2,
            model="imagen-3.0-fast-generate-001",  # 빠른 모델 사용
            aspect_ratio="1:1",
            count=2
        )
        
        print(f"   ✅ {len(images)}개 이미지 생성 완료!")
        
        # 7. 이미지들 저장
        for i, img in enumerate(images):
            filename = f"{OUTPUT_DIR}/test_cat_{i+1}.png"
            img.save(filename)
            print(f"   💾 저장: {filename} ({img.size:,} bytes)")
        
        print("\n🎉 모든 테스트 완료!")
        print(f"📁 생성된 파일들을 확인하세요: {OUTPUT_DIR}/")
        
        # 8. 지원 모델 목록 출력
        print("\n📋 지원되는 모델 목록:")
        models = client.list_models()
        for model in models:
            print(f"   • {model}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """메인 함수"""
    success = await test_image_generation()
    
    if success:
        print("\n✅ 테스트 성공! 패키지가 정상적으로 작동합니다.")
    else:
        print("\n❌ 테스트 실패!")
    
    return success

if __name__ == "__main__":
    # 비동기 실행
    result = asyncio.run(main())
    exit(0 if result else 1) 