from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Text, CHAR, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.core.database import Base

class DetectionResult(Base):
    """탐지 결과 테이블"""
    __tablename__ = "tbl_detection_results"
    
    # 기본키
    detection_seq = Column(Integer, primary_key=True, autoincrement=True)
    
    # 연결관계
    device_seq = Column(Integer, ForeignKey('tbl_device.device_seq'), nullable=False)
    user_seq = Column(Integer, ForeignKey('tbl_user.user_seq'), nullable=False)
    model_product_seq = Column(Integer, ForeignKey('tbl_model_product.model_product_seq'), nullable=False)
    
    # 탐지 정보
    detection_class = Column(String(50), nullable=False)  # 탐지 대분류 (safety, security, transportation)
    detection_label = Column(String(32), nullable=False)  # 탐지 세부 라벨 (fire, helmet, weapon 등)
    confidence = Column(DECIMAL(5, 2), nullable=False)
    
    # 미디어 정보
    image_url = Column(String(255), nullable=True)          # 이미지 URL
    media_type = Column(Enum('image', 'video'), nullable=False, default='image')  # 미디어 타입
    video_url = Column(String(255), nullable=True)          # 비디오 URL
    video_duration = Column(Integer, nullable=False, default=10)  # 비디오 길이(초)
    thumbnail_url = Column(String(255), nullable=True)      # 썸네일 URL
    
    # 바운딩 박스 정보
    bbox_x = Column(Integer, nullable=False)          # X 좌표
    bbox_y = Column(Integer, nullable=False)          # Y 좌표
    bbox_width = Column(Integer, nullable=False)      # 너비
    bbox_height = Column(Integer, nullable=False)     # 높이
    
    # 상태 , 메타 정보
    is_read = Column(CHAR(1), nullable=False, default='N')
    detection_count = Column(Integer, nullable=False, default=1)
    detection_details = Column(LONGTEXT, nullable=True)
    
    # 타임스탬프
    detected_at = Column(DateTime, nullable=False)  # 탐지 시각
    reg_dt = Column(DateTime, nullable=False, default=func.current_timestamp())  # 등록 시각

    # 관계 정의
    device = relationship("Device")
    user = relationship("User")
    model_product = relationship("ModelProduct")