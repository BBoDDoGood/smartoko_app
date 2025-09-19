from sqlite3 import Date
from sqlalchemy import Column, Integer, String, DateTime, CHAR, DECIMAL, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.core.database import Base

class GuidanceModel(Base):
    """ai 언어 모델 테이블 - 로컬 ai 언어모델 정보"""
    __tablename__ = "tbl_guidance_model_product"
    
    # 기본 키
    guidance_model_product_seq = Column(Integer, primary_key=True, autoincrement=True)
    model_product_seq = Column(Integer, ForeignKey('tbl_model_product.model_product_seq'), nullable=False)
    
    # 언어모델 기본 정보
    guidance_model_name = Column(String(100), nullable=False)       # AI 모델명
    guidance_product_code = Column(String(32), nullable=False)      # 제품 코드 (UNIQUE)
    target_detection_label = Column(String(32), nullable=False)     # 대상 탐지 라벨
    
    # ai 모델 파라미터
    max_output_length = Column(Integer, nullable=False, default=200)     # 최대 출력 길이
    temperature = Column(DECIMAL(3,2), nullable=False, default=0.25)     # AI 온도 (0.0-1.0)
    
    # 상태 및 관리 정보
    is_active = Column(CHAR(1), nullable=False, default='Y')        # 활성 상태 (Y/N)
    reg_dt = Column(DateTime, nullable=False, default=func.current_timestamp())
    lastup_dt = Column(DateTime, nullable=False, default=func.current_timestamp())
    
    # 관계 정의
    # ModelProduct와의 관계
    model_product = relationship("ModelProduct", backref="guidance_models")

    # 다국어 테이블과의 관계
    languages = relationship("GuidanceModelLang", back_populates="guidance_model", cascade="all, delete-orphan")
    # AI 알림과의 관계
    ai_alerts = relationship("AIAlert", back_populates="guidance_model")
    
class GuidanceModelLang(Base):
    """ai 언어 모델 다국어 테이블"""
    __tablename__ = "tbl_guidance_model_product_lang"
    
    # 기본 키
    guidance_model_product_lang_seq = Column(Integer, primary_key=True, autoincrement=True)
    
    # 외래 키 
    guidance_model_product_seq = Column(Integer, ForeignKey('tbl_guidance_model_product.guidance_model_product_seq'), nullable=False)
    
    # 다국어 정보
    guidance_model_name = Column(String(250), nullable=True)   # 모델명
    ai_detection_guide = Column(LONGTEXT, nullable=True)   # AI 탐지 안내문 (다국어)
    lang_tag = Column(String(10), nullable=False)   # 언어 태그
    
    # 타임스탬프
    reg_dt = Column(DateTime, nullable=True, default=func.current_timestamp())
    
    # 관계 정의
    guidance_model = relationship("GuidanceModel", back_populates="languages")