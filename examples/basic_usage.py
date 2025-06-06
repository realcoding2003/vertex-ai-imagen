#!/usr/bin/env python3
"""
기본 사용 예제

간단한 이미지 생성 방법을 보여줍니다.
"""

import asyncio
import os
from vertex_ai_imagen import ImagenClient

async def main():
    """기본 사용 예제"""
    
    # 환경 변수 확인
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not project_id or not credentials_path:
        print("❌ 환경 변수를 설정해주세요:")
        print("export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("export GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json'")
        return
    
    # 클라이언트 초기화
    print("🔧 클라이언트 초기화 중...")
    client = ImagenClient(project_id)
    
    # 인증 설정
    try:
        client.setup_credentials_from_env()
        print("✅ 인증 성공")
    except Exception as e:
        print(f"❌ 인증 실패: {e}")
        return
    
    # 간단한 이미지 생성
    print("🎨 이미지 생성 중...")
    try:
        image = await client.generate(
            prompt="A beautiful sunset over the ocean",
            aspect_ratio="16:9"
        )
        
        # 이미지 저장
        image.save("sunset.png")
        print(f"✅ 이미지 저장 완료!")
        print(f"   파일: sunset.png")
        print(f"   크기: {image.size:,} bytes")
        print(f"   프롬프트: {image.prompt}")
        
        if image.enhanced_prompt != image.prompt:
            print(f"   개선된 프롬프트: {image.enhanced_prompt}")
        
    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")

if __name__ == "__main__":
    asyncio.run(main())
