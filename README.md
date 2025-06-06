# 🎨 Vertex AI Imagen Python Client

[![PyPI version](https://badge.fury.io/py/vertex-ai-imagen.svg)](https://badge.fury.io/py/vertex-ai-imagen)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Simple and clean Python client for Google Cloud Vertex AI Imagen**

Generate AI images with just a few lines of code!

## 🚀 Quick Start

### Installation

```bash
pip install vertex-ai-imagen
```

### Basic Usage

```python
import asyncio
from vertex_ai_imagen import ImagenClient

async def main():
    # Initialize client
    client = ImagenClient(project_id="your-project-id")
    client.setup_credentials("path/to/service-account-key.json")
    
    # Generate image
    image = await client.generate(
        prompt="A beautiful sunset over the ocean",
        aspect_ratio="16:9"
    )
    
    # Save image
    image.save("sunset.png")
    print(f"Image saved! Size: {image.size:,} bytes")

# Run
asyncio.run(main())
```

## ✨ Features

- 🚀 **Simple API**: Generate images with just a few lines
- 🎯 **Type Safe**: Full type hints support
- 🔒 **Secure**: Google Cloud service account authentication
- 📦 **Clean Models**: Intuitive data classes
- ⚡ **Async Support**: Built-in async/await patterns
- 🎛️ **Full Control**: Access to all Imagen parameters

## 📖 Advanced Usage

### Multiple Images

```python
# Generate multiple images
images = await client.generate(
    prompt="A futuristic city with flying cars",
    model="imagen-3.0-fast-generate-001",
    aspect_ratio="16:9",
    count=3,
    negative_prompt="blurry, low quality",
    seed=12345
)

# Save all images
for i, image in enumerate(images):
    image.save(f"city_{i+1}.png")
```

### Authentication Options

```python
# Method 1: Direct key file
client.setup_credentials("path/to/key.json")

# Method 2: Environment variable (GOOGLE_APPLICATION_CREDENTIALS)
client.setup_credentials_from_env()
```

### Supported Models

```python
# List available models
models = client.list_models()
print(models)

# Output:
# ['imagegeneration@006', 'imagen-3.0-generate-001', 'imagen-3.0-fast-generate-001', ...]
```

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `imagen-3.0-fast-generate-001` | ⚡ Fast | 🟢 Good | Prototyping, batch generation |
| `imagegeneration@006` | 🟡 Medium | 🔵 Great | General purpose |
| `imagen-3.0-generate-002` | 🟡 Medium | 🟣 Best | High-quality work |

### Aspect Ratios

- `1:1` - Square
- `16:9` - Widescreen 
- `9:16` - Portrait (mobile)
- `4:3` - Traditional landscape
- `3:4` - Traditional portrait

## 🔧 Setup

### Google Cloud Setup

1. **Enable the API**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

2. **Create Service Account**
   ```bash
   gcloud iam service-accounts create imagen-client \
     --display-name="Imagen Client"
   
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:imagen-client@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

3. **Create Service Account Key**
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=imagen-client@PROJECT_ID.iam.gserviceaccount.com
   ```

### Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

## 📝 Examples

Check out the [examples](examples/) directory for more usage patterns:

- [Basic Usage](examples/basic_usage.py) - Simple image generation
- [Advanced Usage](examples/test_image_generation.py) - Complete feature demo

### Jupyter Notebook

```python
# Display image directly in notebook
image = await client.generate("A cute cat")
image.show()  # Shows image inline
```

### Error Handling

```python
from vertex_ai_imagen.exceptions import ImagenError, AuthenticationError

try:
    image = await client.generate("A beautiful landscape")
    image.save("landscape.png")
except AuthenticationError:
    print("Please check your credentials")
except ImagenError as e:
    print(f"Image generation failed: {e}")
```

## 📊 API Reference

### ImagenClient

```python
client = ImagenClient(
    project_id="your-project-id",
    location="us-central1"  # optional
)
```

### Generate Images

```python
await client.generate(
    prompt="Image description",                # required
    model="imagegeneration@006",              # optional
    aspect_ratio="1:1",                       # optional
    count=1,                                  # 1-4
    negative_prompt="Things to exclude",      # optional
    seed=12345,                              # optional
    safety_setting="block_medium_and_above",  # optional
    enhance_prompt=True                       # optional
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/vertex-ai-imagen/)
- [GitHub Repository](https://github.com/realcoding2003/vertex-ai-imagen)
- [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai)
- [Imagen Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)
