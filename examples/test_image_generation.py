#!/usr/bin/env python3
"""
Vertex AI Imagen Real Image Generation Test
"""

import asyncio
import os
from pathlib import Path
from vertex_ai_imagen import ImagenClient

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv is not installed. pip install python-dotenv")

# Configuration (read from .env first, fallback to defaults)
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "../generated_images")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")

async def test_image_generation():
    """Image generation test"""
    print("🎨 Starting Vertex AI Imagen test\n")
    
    # Check required environment variables
    if not PROJECT_ID:
        print("❌ Error: GOOGLE_CLOUD_PROJECT environment variable is required")
        print("   Please set: export GOOGLE_CLOUD_PROJECT='your-project-id'")
        return False
    
    if not CREDENTIALS_PATH:
        print("❌ Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is required")
        print("   Please set: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'")
        return False
    
    try:
        # 1. Initialize client
        print("📋 1. Initializing client...")
        client = ImagenClient(project_id=PROJECT_ID, location=LOCATION)
        print(f"   ✅ Project ID: {PROJECT_ID}")
        print(f"   ✅ Location: {LOCATION}")
        
        # 2. Setup authentication
        print("🔐 2. Setting up GCP authentication...")
        print(f"   📁 Credentials file: {CREDENTIALS_PATH}")
        
        # Try environment variable authentication first
        try:
            success = client.setup_credentials_from_env()
            if success:
                print("   ✅ Environment variable authentication successful!")
            else:
                raise Exception("Environment variable authentication failed")
        except Exception as e:
            print(f"   ⚠️  Environment variable authentication failed: {e}")
            print("   🔄 Retrying with file authentication...")
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_PATH}")
            success = client.setup_credentials(CREDENTIALS_PATH)
            if success:
                print("   ✅ File authentication successful!")
            else:
                raise Exception("File authentication failed")
        
        # 3. Create output directory
        print("📁 3. Creating output directory...")
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        print(f"   ✅ Directory: {OUTPUT_DIR}")
        
        # 4. Simple image generation test
        print("🎯 4. Image generation test...")
        prompt = "A beautiful sunset over the ocean with waves"
        print(f"   📝 Prompt: {prompt}")
        
        print("   ⏳ Generating image... (this may take a while)")
        
        image = await client.generate(
            prompt=prompt,
            model="imagegeneration@006",
            aspect_ratio="16:9",
            count=1
        )
        
        print("   ✅ Image generation completed!")
        
        # 5. Save image
        print("💾 5. Saving image...")
        filename = f"{OUTPUT_DIR}/test_sunset.png"
        image.save(filename)
        
        print(f"   ✅ Save completed: {filename}")
        print(f"   📊 File size: {image.size:,} bytes")
        if image.enhanced_prompt != image.prompt:
            print(f"   ✨ Enhanced prompt: {image.enhanced_prompt}")
        
        # 6. Multiple image generation test
        print("\n🎨 6. Multiple image generation test...")
        prompt2 = "A cute cat playing with a ball"
        print(f"   📝 Prompt: {prompt2}")
        
        images = await client.generate(
            prompt=prompt2,
            model="imagen-3.0-fast-generate-001",  # Use fast model
            aspect_ratio="1:1",
            count=2
        )
        
        print(f"   ✅ Generated {len(images)} images successfully!")
        
        # 7. Save images
        for i, img in enumerate(images):
            filename = f"{OUTPUT_DIR}/test_cat_{i+1}.png"
            img.save(filename)
            print(f"   💾 Saved: {filename} ({img.size:,} bytes)")
        
        print("\n🎉 All tests completed!")
        print(f"📁 Check generated files at: {OUTPUT_DIR}/")
        
        # 8. List supported models
        print("\n📋 Supported models:")
        models = client.list_models()
        for model in models:
            print(f"   • {model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    success = await test_image_generation()
    
    if success:
        print("\n✅ Test successful! Package is working correctly.")
    else:
        print("\n❌ Test failed!")
    
    return success

if __name__ == "__main__":
    # 비동기 실행
    result = asyncio.run(main())
    exit(0 if result else 1) 