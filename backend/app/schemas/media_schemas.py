from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

class MediaType(str, Enum):
    """미디어 파일 분류
     - IMAGE: ai 탐지 이미지
     - THUMBNAIL: 썸네일 이미지 <- 카드뷰
     - VIDEO_CLIP: 상세뷰용 탐지 전후 동영상 (10초 클립)
    """
    IMAGE = "image"
    THUMBNAIL = "thumbnail"
    VIDEO_CLIP = "video_clip"
    
class MediaFile(BaseModel):
    url: str = Field(..., description="미디어 파일 URL", examples=["/uploads/images/2024/09/device_001/YYYYMMDD_~~~~~_~~~~.jpg"])
    type: MediaType = Field(..., description="미디어 파일 타입")
    size_bytes: int = Field(..., ge=0, description="미디어 파일 크기(바이트)")
    created_at: datetime = Field(..., description="미디어 파일 생성 시간")
    
    # 장동 계산 필드
    size_mb: Optional[float] = Field(None, description="미디어 파일 크기(MB)")
    
    @field_validator('size_mb', mode='before')
    @classmethod
    def calculate_size_mb(cls, v, info):
        """ 파일 크기 MB 단위 자동 계산
        - v: size_mb 필드 값
        - info: 검증 컨텍스트 정보
        """
        if hasattr(info, 'data') and 'size_bytes' in info.data:
            return round(info.data['size_bytes'] / (1024 * 1024), 2)
        return v
    
    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
    
class DetectionMedia(BaseModel):
    """탐지 결과와 연관된 미디어 정보
    - 모든 탐지 3개 파일 보유 (원본 이미지, 썸네일, 탐지 전후 동영상 클립)
    """
    detection_id: int = Field(..., description="탐지 결과 ID")
    detection_time: datetime = Field(..., description="탐지 발생 시간")
    device_name: str = Field(..., description="탐지 장치명")
    model_name: Optional[str] = Field(None, description="사용된 모델명")
    
    # 필수 미디어 파일
    original_image: MediaFile = Field(..., description="원본 탐지 이미지")
    thumbnail: MediaFile = Field(..., description="썸네일 이미지")
    video_clip: MediaFile = Field(..., description="탐지 전후 동영상 클립")
    
    @field_validator('detection_time', mode='before')
    @classmethod
    def parse_detection_time(cls, v):
        """timestamp 형식 처리"""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
class UploadRequest(BaseModel):
    """파일 업로드 요청 메타 데이터"""
    detection_id: Optional[int] = Field(None, description="기존 탐지 ID (새 탐지 시 None)")
    device_name: str = Field(..., description="업로드 장치명")
    file_type: MediaType = Field(..., description="업로드할 파일 타입")
    detection_time: datetime = Field(..., description="탐지 발생 시점 (동영상 클립 추출용)")
    
class UploadResponse(BaseModel):
    """파일 업로드 처리 결과
    - 업로드 성공 / 실패 구분
    - 자동 생성된 모든 파일 정보 제공
    - 처리 성능 모니터링 데이터
    """
    success: bool = Field(..., description="업로드 성공 여부")
    message: str = Field(..., description="결과 메시지")
    
    # 생성된 미디어 세트 (3개 파일 모두 포함)
    detection_media: Optional[DetectionMedia] = Field(None, description="완성된 탐지 미디어 세트")
    
    # 에러 정보 (실패 시)
    error_code: Optional[str] = Field(None, description="에러 코드")
    error_details: Optional[Dict[str, Any]] = Field(None, description="상세 에러 정보")
    
    # 성능 메트릭
    processing_time_ms: Optional[float] = Field(None, description="처리 시간(밀리초)")
    
class MediaListQuery(BaseModel):
    """미디어 목록 조회 쿼리"""
    
    # 페이징
    page: int = Field(1, ge=1, description="페이지 번호")
    page_size: int = Field(20, ge=1, le=100, description="페이지 크기")
    
    # 사용자 필터링 옵션
    device_name: Optional[str] = Field(None, description="장치별 필터")
    media_type: Optional[MediaType] = Field(None, description="미디어 타입별 필터")
    date_from: Optional[datetime] = Field(None, description="시작 날짜")
    date_to: Optional[datetime] = Field(None, description="종료 날짜")
    
    # 정렬
    sort_by: str = Field("created_at", description="정렬 기준", pattern="^(created_at|size_bytes|device_name)$")
    sort_order: str = Field("desc", description="정렬 순서", pattern="^(asc|desc)$")
    
    @field_validator('page_size')
    @classmethod
    def validate_page_size(cls, v):
        """페이지 크기 비즈니스 규칙 검증"""
        if not 1 <= v <= 100:
            raise ValueError("페이지 크기는 1~100 사이여야 합니다.")
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """날짜 범위 논리 검증"""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("시작일이 종료일보다 늦을 수 없습니다.")
        return self
    
class MediaListResult(BaseModel):
    """미디어 목록 조회 결과"""
    #페이징 메타 데이터
    total_count: int = Field(..., ge=0, description="전체 항목 수")
    page: int = Field(..., ge=1, description="현재 페이지")
    page_size: int = Field(..., ge=1, description="페이지 크기")
    total_pages: int = Field(..., ge=1, description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재")
    has_previous: bool = Field(..., description="이전 페이지 존재")
    
    # 실제 데이터
    items: List[DetectionMedia] = Field(default_factory=list, description="탐지 미디어 목록")
    
    @field_validator('total_pages', mode='before')
    @classmethod
    def calculate_total_pages(cls, v, info):
        """전체 페이지 수 자동 계산"""
        import math
        if hasattr(info, 'data'):
            total_count = info.data.get('total_count', 0)
            page_size = info.data.get('page_size', 1)
            return max(1, math.ceil(total_count / page_size))
        return v
    
class MediaStats(BaseModel):
    """미디어 통계 정보"""
    # 사용자 관심 통계
    total_detections: int = Field(..., ge=0, description="전체 탐지 수")
    total_files: int = Field(..., ge=0, description="전체 파일 수")
    image_count: int = Field(..., ge=0, description="이미지 파일 수")
    thumbnail_count: int = Field(..., ge=0, description="썸네일 파일 수")
    video_clip_count: int = Field(..., ge=0, description="동영상 클립 수")
    
    # 사용자 편의 정보
    total_size_mb: float = Field(..., ge=0, description="전체 사용 용량 (MB)")
    device_stats: Dict[str, int] = Field(default_factory=dict, description="장치별 탐지 수")
    latest_detection: Optional[datetime] = Field(None, description="최근 탐지 시간")
    
    # 통계 생성 정보
    generated_at: datetime = Field(default_factory=datetime.now, description="통계 생성 시간")
    
class DeleteRequest(BaseModel):
    """개별 파일 삭제 요청"""
    detection_id: int = Field(..., description="삭제할 탐지 ID")
    confirm: bool = Field(..., description="삭제 확인")
    
    @field_validator('confirm')
    @classmethod
    def validate_confirmation(cls, v):
        """삭제 시 실수 방지 확인"""
        if not v:
            raise ValueError("삭제 확인이 필요합니다")
        return v
    
class DeleteResult(BaseModel):
    """개별 삭제 결과"""
    success: bool = Field(..., description="삭제 성공 여부")
    message: str = Field(..., description="결과 메시지")
    deleted_detection_id: Optional[int] = Field(None, description="삭제된 탐지 ID")
    deleted_files_count: int = Field(0, description="삭제된 파일 수")
    
    # 에러 정보
    error_code: Optional[str] = Field(None, description="에러 코드")
    error_details: Optional[Dict[str, Any]] = Field(None, description="상세 에러 정보")
    
class ErrorResponse(BaseModel):
    """표준 에러 응답"""
    success: bool = Field(False, description="처리 성공 여부")
    error_code: str = Field(..., description="표준 에러 코드")
    message: str = Field(..., description="사용자 표시용 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="디버깅용 상세정보")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시간")
    request_id: Optional[str] = Field(None, description="요청 추적 ID")