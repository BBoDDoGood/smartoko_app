"""대시보드 api 응답 데이터 형식 정의"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# 메인 대시보드 응답 모델들
class DashboardOverview(BaseModel):
    """대시보드 전체 개요 - 실제 DB 스키마 반영"""
    today_total_detections: int = Field(..., description="오늘 총 탐지 건수")
    devices_detected_today: int = Field(..., description="오늘 탐지가 있었던 디바이스 수")
    total_registered_devices: int = Field(..., description="전체 등록 디바이스 수")
    risk_level_critical_count: int = Field(..., description="위험 수준: Critical 탐지 수")
    risk_level_high_count: int = Field(..., description="위험 수준: High 탐지 수")
    risk_level_medium_count: int = Field(..., description="위험 수준: Medium 탐지 수")
    security_safe_count: int = Field(..., description="보안 안전 탐지 수")
    general_detection_count: int = Field(..., description="일반 객체 탐지 수")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")

class HourlyChartData(BaseModel):
    """시간별 탐지 차트 데이터 (개별 시간)"""
    hour: int = Field(..., description="시간 (0-23)")
    hour_display: str = Field(..., description="표시용 시간 (예: 09:00)")
    detection_count: int = Field(..., description="해당 시간 탐지 건수")
    
class DeviceModelSubscription(BaseModel):
    """등록된 디바이스별 활성화된 모델 상품명"""
    device_seq: int = Field(..., description="디바이스 고유 번호")
    device_label: str = Field(..., description="디바이스 이름")
    device_type: Optional[str] = Field(None, description="디바이스 타입")
    activated_model_products: List[str] = Field(..., description="활성화된 AI 모델 상품명 목록")
    today_detection_count: int = Field(..., description="오늘 탐지 건수")
    last_detection_time: Optional[datetime] = Field(None, description="마지막 탐지 시간")

class DeviceStatus(BaseModel):
    """디바이스 상태 요약 (레거시)"""
    device_seq: int = Field(..., description="디바이스 고유 번호")
    device_label: str = Field(..., description="디바이스 이름")
    device_type: Optional[str] = Field(None, description="디바이스 타입")
    status: str = Field(..., description="상태 (registered, active, inactive)")
    today_detection_count: int = Field(..., description="오늘 탐지 건수")
    last_detection_time: Optional[datetime] = Field(None, description="마지막 탐지 시간")
    
class RecentRiskDetection(BaseModel):
    """최근 긴급 알림 -  critical / high만 표시 (medium 제외)"""
    detection_seq: int = Field(..., description="탐지 고유 번호")
    device_label: str = Field(..., description="디바이스 이름")
    detection_class: str = Field(..., description="탐지 대분류 (safety, security, transportation)")
    detection_label: str = Field(..., description="탐지 세부 라벨 (fire, helmet, weapon 등)")
    danger_level: str = Field(..., description="위험 레벨 (critical / high)")
    detection_confidence: float = Field(..., description="탐지 신뢰도 (0.0~1.0)")
    thumbnail_image_path: Optional[str] = Field(None, description="썸네일 이미지 경로")
    detection_time: datetime = Field(..., description="탐지 시간")
    ai_detection_guide: Optional[str] = Field(None, description="AI 안내 메시지")
    location_info: Optional[str] = Field(None, description="위치 정보")
    bounding_box_info: Optional[Dict[str, Any]] = Field(None, description="바운딩 박스 정보")

class RecentAlert(BaseModel):
    """최근 알림 목록"""
    alert_seq: int = Field(..., description="알림 고유 번호")
    device_label: str = Field(..., description="디바이스 이름")
    alert_type: str = Field(..., description="알림 타입 (critical, emergency)")
    alert_message: str = Field(..., description="알림 메시지")
    alert_time: datetime = Field(..., description="알림 시간")
    is_read: bool = Field(default=False, description="읽음 여부")
    related_detection_seq: Optional[int] = Field(None, description="연관된 탐지 결과 번호")

# 통합 대시보드 데이터 스키마
class DashboardCompleteData(BaseModel):
    """대시보드 전체 데이터 - DashboardService 전용"""
    overview: DashboardOverview = Field(..., description="대시보드 개요 통계")
    hourly_chart: List[HourlyChartData] = Field(..., description="시간별 차트 데이터 (24시간)")
    device_model_subscriptions: List[DeviceModelSubscription] = Field(..., description="등록된 디바이스별 활성화된 모델 상품명")
    recent_detections: List[RecentRiskDetection] = Field(..., description="최근 위험 탐지 목록")
    recent_alerts: List[RecentAlert] = Field(..., description="최근 알림 목록")
    last_updated: datetime = Field(..., description="데이터 마지막 업데이트 시간")
    user_language: str = Field(..., description="사용자 UI 언어")

# 레거시 응답
class DashboardResponse(BaseModel):
    """메인 대시보드 단일 api 응답 (레거시)"""
    success: bool = Field(..., description="api 호출 성공 여부")
    overview: DashboardOverview = Field(..., description="전체 개요 통계")
    hourly_chart: List[HourlyChartData] = Field(..., description="시간대별 차트 데이터")
    device_status: List[DeviceStatus] = Field(..., description="디바이스 상태 요약")
    recent_risks: List[RecentRiskDetection] = Field(..., description="최근 긴급 상황")