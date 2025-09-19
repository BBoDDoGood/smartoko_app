from sqlalchemy import Column, Integer, String, DateTime, Text, CHAR, Enum, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.core.database import Base

class AIAlert(Base):
    """AI 알림 테이블"""
    __tablename__ = "tbl_ai_alerts"
    
    # 기본 키
    alert_seq = Column(Integer, primary_key=True, autoincrement=True)
    
    # 외래 키 및 연결 관계
    detection_seq = Column(Integer, ForeignKey("tbl_detection_results.detection_seq"), nullable=True)  # 탐지 결과
    user_seq = Column(Integer, ForeignKey("tbl_user.user_seq"), nullable=False)  # 사용자
    model_product_seq = Column(Integer, ForeignKey("tbl_model_product.model_product_seq"), nullable=False)  # 모델 제품
    guidance_model_product_seq = Column(Integer, ForeignKey("tbl_guidance_model_product.guidance_model_product_seq"), nullable=True)  # 사용된 안내문 모델
    
    # 모델 및 안내 정보
    guidance_model_name = Column(String(50), nullable=True)  # AI 안내 모델명
    ai_detection_guide = Column(Text, nullable=False)  # 안내문 텍스트

    # 알림 타입 및 상태
    alert_type = Column(Enum('detection', 'emergency', 'warning', 'info'), nullable=False)  # 알림 타입
    is_read = Column(CHAR(1), nullable=False, default='N')  # 읽음 여부 (Y/N)

    # 언어 및 생성 결과
    lang_tag = Column(String(10), nullable=True, default='en-US')  # 언어 태그
    guidance_status = Column(CHAR(1), nullable=True, default='P')  # 안내 단계: P(대기), Y(성공), N(실패)
    generation_time_ms = Column(Integer, nullable=True)  # 안내문 생성 소요 시간(ms)
    
    # 타임스탬프
    reg_dt = Column(DateTime, nullable=False, default=func.current_timestamp())
    read_dt = Column(DateTime, nullable=True)

    # 관계 설정
    detection_result = relationship("DetectionResult")
    user = relationship("User")
    guidance_model = relationship("GuidanceModel", back_populates="ai_alerts")

    # 제약조건
    __table_args__ = (
        CheckConstraint("guidance_status IN ('P','Y','N')", name="chk_guidance_status"),
    )

#Alert로 import 하는 경우를 대비한 별칭
Alert = AIAlert