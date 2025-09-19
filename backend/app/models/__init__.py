# SQLAlchemy 모델 통합 import
from .user import User, LoginLog
from .device import Device
from .group import Group
from .detection_result import DetectionResult
from .alert import AIAlert, Alert  # 하위 호환성을 위한 별칭 포함
from .detection_mapping import ModelDetectionMapping
from .model_product import ModelProduct, ModelProductLang
from .subscription import DeviceProductSubscription
from .guidance_model import GuidanceModel, GuidanceModelLang

# 모든 모델을 __all__에 등록하여 외부에서 import 가능하도록 설정
__all__ = [
    # 사용자 관련
    "User", 
    "LoginLog",
    
    # 디바이스 관련
    "Device", 
    "Group",
    
    # 탐지 및 알림
    "DetectionResult",
    "AIAlert",
    "Alert",  # 하위 호환성
    "ModelDetectionMapping",
    
    # 모델 제품
    "ModelProduct",
    "ModelProductLang",
    
    # 구독 관리
    "DeviceProductSubscription",
    
    # AI 안내 모델
    "GuidanceModel",
    "GuidanceModelLang"
]