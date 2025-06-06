"""
예외 클래스들
"""

class ImagenError(Exception):
    """Imagen API 관련 기본 예외"""
    pass

class AuthenticationError(ImagenError):
    """인증 관련 예외"""
    pass

class APIError(ImagenError):
    """API 호출 관련 예외"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class ValidationError(ImagenError):
    """입력 검증 관련 예외"""
    pass
