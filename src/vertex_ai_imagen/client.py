"""
Vertex AI Imagen 클라이언트
"""

import asyncio
import os
import logging
from typing import List, Optional, Union

try:
    import requests
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
except ImportError:
    raise ImportError(
        "필요한 라이브러리를 설치해주세요: "
        "pip install requests google-auth google-auth-oauthlib google-auth-httplib2"
    )

from .models import GeneratedImage, ImageRequest
from .exceptions import ImagenError, AuthenticationError, APIError, ValidationError

logger = logging.getLogger(__name__)

class ImagenClient:
    """Vertex AI Imagen 클라이언트"""
    
    # 지원되는 모델 목록
    SUPPORTED_MODELS = [
        "imagegeneration@006",
        "imagegeneration@005", 
        "imagegeneration@002",
        "imagen-3.0-generate-001",
        "imagen-3.0-generate-002",
        "imagen-3.0-fast-generate-001"
    ]
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        Args:
            project_id: Google Cloud 프로젝트 ID
            location: Vertex AI 리전 (기본값: us-central1)
        """
        self.project_id = project_id
        self.location = location
        self.credentials = None
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1"
        
    def setup_credentials(self, key_path: str) -> bool:
        """
        서비스 계정 키로 인증 설정
        
        Args:
            key_path: 서비스 계정 키 파일 경로
            
        Returns:
            bool: 인증 성공 여부
        """
        try:
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")
            
            self.credentials = service_account.Credentials.from_service_account_file(
                key_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            if not self.credentials.valid:
                self.credentials.refresh(Request())
            
            logger.info("Google Cloud 인증 성공")
            return True
            
        except Exception as e:
            logger.error(f"인증 실패: {e}")
            raise AuthenticationError(f"인증 실패: {e}")
    
    def setup_credentials_from_env(self) -> bool:
        """
        환경 변수에서 인증 설정
        GOOGLE_APPLICATION_CREDENTIALS 환경 변수 사용
        
        Returns:
            bool: 인증 성공 여부
        """
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise AuthenticationError(
                "GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다"
            )
        
        return self.setup_credentials(credentials_path)
    
    async def generate(
        self,
        prompt: str,
        *,
        model: str = "imagegeneration@006",
        aspect_ratio: str = "1:1",
        count: int = 1,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        safety_setting: str = "block_medium_and_above",
        enhance_prompt: bool = True
    ) -> Union[GeneratedImage, List[GeneratedImage]]:
        """
        이미지 생성 - 깔끔한 API
        
        Args:
            prompt: 이미지 생성 프롬프트 (필수)
            model: AI 모델 (기본값: imagegeneration@006)
            aspect_ratio: 가로세로 비율 (1:1, 16:9, 9:16, 4:3, 3:4)
            count: 생성할 이미지 개수 (1-4)
            negative_prompt: 제외할 내용
            seed: 재현성을 위한 시드
            safety_setting: 안전 필터 수준
            enhance_prompt: 프롬프트 자동 개선 여부
            
        Returns:
            count=1이면 GeneratedImage, 그 외에는 List[GeneratedImage]
        """
        if not self.credentials:
            raise AuthenticationError("인증이 설정되지 않았습니다. setup_credentials() 호출 필요")
        
        # 요청 객체 생성 (검증 포함)
        request = ImageRequest(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            count=count,
            negative_prompt=negative_prompt,
            seed=seed,
            safety_setting=safety_setting,
            enhance_prompt=enhance_prompt
        )
        
        # 모델 검증
        if request.model not in self.SUPPORTED_MODELS:
            raise ValidationError(f"지원되지 않는 모델: {request.model}")
        
        # API 호출
        try:
            result = await self._call_api(request)
            
            # 결과 파싱
            predictions = result.get("predictions", [])
            if not predictions:
                raise APIError("이미지가 생성되지 않았습니다")
            
            images = [GeneratedImage.from_api_response(pred) for pred in predictions]
            
            logger.info(f"이미지 {len(images)}개 생성 완료")
            
            return images[0] if count == 1 else images
            
        except Exception as e:
            if isinstance(e, (ImagenError, ValidationError)):
                raise
            else:
                raise APIError(f"이미지 생성 실패: {e}")
    
    async def _call_api(self, request: ImageRequest) -> dict:
        """실제 API 호출"""
        url = (
            f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/"
            f"publishers/google/models/{request.model}:predict"
        )
        
        # 요청 데이터 구성
        request_data = {
            "instances": [{"prompt": request.prompt}],
            "parameters": {
                "sampleCount": request.count,
                "aspectRatio": request.aspect_ratio,
                "addWatermark": False,
                "enhancePrompt": request.enhance_prompt
            }
        }
        
        # 선택적 매개변수 추가
        if request.negative_prompt:
            request_data["parameters"]["negativePrompt"] = request.negative_prompt
        
        if request.safety_setting:
            request_data["parameters"]["safetySetting"] = request.safety_setting
        
        if request.seed is not None:
            request_data["parameters"]["seed"] = request.seed
        
        headers = {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "application/json"
        }
        
        # 비동기 HTTP 요청
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.post(url, json=request_data, headers=headers, timeout=180)
        )
        
        if response.status_code != 200:
            error_message = f"HTTP {response.status_code}: {response.text}"
            raise APIError(error_message, response.status_code)
        
        return response.json()
    
    def list_models(self) -> List[str]:
        """지원되는 모델 목록 반환"""
        return self.SUPPORTED_MODELS.copy()
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        return self.credentials is not None and self.credentials.valid
