"""
데이터 모델들
"""

from dataclasses import dataclass
from typing import Optional, Union
from pathlib import Path
import base64

@dataclass
class ImageRequest:
    """이미지 생성 요청"""
    prompt: str
    model: str = "imagegeneration@006" 
    aspect_ratio: str = "1:1"
    count: int = 1
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    safety_setting: str = "block_medium_and_above"
    enhance_prompt: bool = True

    def __post_init__(self):
        """입력 검증"""
        if not self.prompt or not self.prompt.strip():
            raise ValueError("프롬프트는 필수입니다")
        
        if self.count < 1 or self.count > 4:
            raise ValueError("이미지 개수는 1-4개여야 합니다")
        
        valid_ratios = ["1:1", "3:4", "4:3", "16:9", "9:16"]
        if self.aspect_ratio not in valid_ratios:
            raise ValueError(f"지원되는 비율: {valid_ratios}")

class GeneratedImage:
    """생성된 이미지"""
    
    def __init__(self, base64_data: str, prompt: str, enhanced_prompt: str = None):
        self.base64_data = base64_data
        self.prompt = prompt
        self.enhanced_prompt = enhanced_prompt or prompt
        self._image_data = None
        
    @property 
    def image_data(self) -> bytes:
        """이미지 바이너리 데이터"""
        if self._image_data is None:
            self._image_data = base64.b64decode(self.base64_data)
        return self._image_data
    
    @property
    def size(self) -> int:
        """이미지 크기 (bytes)"""
        return len(self.image_data)
    
    def save(self, path: Union[str, Path]) -> None:
        """이미지 저장"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "wb") as f:
            f.write(self.image_data)
    
    def show(self):
        """이미지 표시 (Jupyter/IPython에서)"""
        try:
            from IPython.display import Image, display
            display(Image(data=self.image_data))
        except ImportError:
            print("IPython이 설치되지 않았습니다. .save()로 파일에 저장하세요.")
            
    @classmethod
    def from_api_response(cls, prediction: dict) -> "GeneratedImage":
        """API 응답에서 이미지 객체 생성"""
        return cls(
            base64_data=prediction["bytesBase64Encoded"],
            prompt=prediction.get("prompt", ""),
            enhanced_prompt=prediction.get("prompt")
        )
    
    def __repr__(self):
        return f"GeneratedImage(prompt='{self.prompt[:30]}...', size={self.size:,} bytes)"
