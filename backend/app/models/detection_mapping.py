from sqlalchemy import Column, Integer, String, DateTime, CHAR, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ModelDetectionMapping(Base):
    """모델 탐지 매핑 테이블 - 모델별 탐지 라벨, 위험도 매핑"""
    __tablename__ = "tbl_model_detection_mappings"
    
    # 기본 키
    mapping_seq = Column(Integer, primary_key=True, autoincrement=True)
    
    # 연결 관계
    model_product_seq = Column(Integer, ForeignKey('tbl_model_product.model_product_seq'), nullable=False)  # 모델 제품
    
    # 탐지 정보
    detection_label = Column(String(32), nullable=False)  # 탐지 라벨 (DB 실제 컬럼명)
    danger_level = Column(Enum('critical', 'high', 'medium', 'low', 'safe', 'normal'), nullable=False)  # 위험도 normal은 일반일 때 사용
    
    # 상태 및 언어 설정
    is_active = Column(CHAR(1), nullable=False, default='Y')  # 활성화 여부 (Y/N)
    language_model_type = Column(String(50), nullable=True, default='general')  # 언어 모델 타입
    language_code = Column(String(10), nullable=True, default='en-US')  # 언어 태그
    guidance_model_product_seq = Column(Integer, ForeignKey("tbl_guidance_model_product.guidance_model_product_seq"), nullable=True)  # 안내문 모델
    
    # 타임스탬프
    reg_dt = Column(DateTime, nullable=False, default=func.current_timestamp())  # 등록 시각

    # 관계 정의
    model_product = relationship("ModelProduct", back_populates="detection_mappings")