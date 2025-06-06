#!/usr/bin/env python3
"""
Basic Usage Example

Demonstrates simple image generation methods.
"""

import asyncio
import os
from vertex_ai_imagen import ImagenClient

async def main():
    """Basic usage example"""
    
    # Check environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not project_id or not credentials_path:
        print("❌ Please set environment variables:")
        print("export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("export GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json'")
        return
    
    # Initialize client
    print("🔧 Initializing client...")
    client = ImagenClient(project_id)
    
    # Setup authentication
    try:
        client.setup_credentials_from_env()
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Generate simple image
    print("🎨 Generating image...")
    try:
        image = await client.generate(
            prompt="A beautiful sunset over the ocean",
            aspect_ratio="16:9"
        )
        
        # Save image
        image.save("sunset.png")
        print(f"✅ Image saved successfully!")
        print(f"   File: sunset.png")
        print(f"   Size: {image.size:,} bytes")
        print(f"   Prompt: {image.prompt}")
        
        if image.enhanced_prompt != image.prompt:
            print(f"   Enhanced prompt: {image.enhanced_prompt}")
        
    except Exception as e:
        print(f"❌ Image generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
