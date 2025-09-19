from sqlalchemy import Column, Integer, String, DateTime, CHAR, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.core.database import Base

class ModelProduct(Base):
    """모델 제품 테이블 - AI 모델 제품의 기본 정보"""
    __tablename__ = "tbl_model_product"
    
    # 기본 키
    model_product_seq = Column(Integer, primary_key=True, autoincrement=True)
    model_seq = Column(Integer, nullable=False)  # 모델 연결
    
    # 제품 기본 정보
    product_name_depatecated = Column(String(256), nullable=False)  # 상품명
    product_desc_depatecated = Column(String(512), nullable=True)   # 상품 설명
    product_code = Column(String(32), nullable=True)               # 제품 코드
    price = Column(DECIMAL(12,2), nullable=False, default=0.00)    # 가격
    
    # 구독 및 상태 정보
    subscription_type = Column(CHAR(1), nullable=False, default='F')  # 구독 타입(F:무료/M:월간/Y:연간/O:일회성)
    icon_type = Column(CHAR(1), nullable=True)                     # 아이콘 타입 (A:bootstrap icon/B:font-awesome)
    icon_class = Column(String(32), nullable=True)         
    icon_color = Column(String(16), nullable=True)
    icon_bgcolor = Column(String(16), nullable=True)
    usage_limit = Column(Integer, nullable=True)                   # 사용량 제한
    published_yn = Column(CHAR(1), nullable=False, default='N')    # 게시 여부(Y:게시/N:미게시)
    status = Column(CHAR(1), nullable=False, default='A')          # 상태(A:활성/B:비활성/C:삭제)
    published_dt = Column(DateTime, nullable=True)                 # 게시일
    
    # 요금 정보
    cost_per_second = Column(DECIMAL(10,4), nullable=True, default=0.0001)  # 초당 비용
    billing_type = Column(CHAR(1), nullable=False, default='S')             # 과금 타입
    min_charge_amount = Column(DECIMAL(10,2), nullable=True, default=0.01)  # 최소 과금액
    detection_cycle = Column(String(16), nullable=True)                     # 탐지 주기
    
    # JSON 및 탐지 데이터
    detection_color = Column(String(16), nullable=True)
    detection_name = Column(String(32), nullable=True)  #AI 서버에서 사용하는 감지 모델명 (상품별 설정)
    detection_label = Column(String(32), nullable=True) #AI 탐지시 보여줄 라벨명  (fire,helmet ..)
    is_featured = Column(CHAR(1), nullable=False, default='N')
    
    # 타임스탬프
    reg_dt = Column(DateTime, nullable=True)                       # 등록일시
    lastup_dt = Column(DateTime, nullable=True)                    # 최종 수정일시

    # 관계 정의
    detection_mappings = relationship("ModelDetectionMapping", back_populates="model_product")
    detection_results = relationship("DetectionResult", back_populates="model_product")
    subscriptions = relationship("ModelProductSubscription", back_populates="model_product")

class ModelProductLang(Base):
    """모델 제품 다국어 테이블"""
    __tablename__ = "tbl_model_product_lang"
    
    # 기본 키  
    model_product_lang_seq = Column(Integer, primary_key=True, autoincrement=True)
    model_product_seq = Column(Integer, nullable=False)            # 모델 상품 일련번호 (tbl_model_product.model_product_seq 참조)
    
    # 다국어 정보
    product_name = Column(String(256), nullable=False)             # 상품명(다국어)
    product_desc = Column(String(512), nullable=True)              # 상품 설명(다국어)
    product_contents = Column(LONGTEXT, nullable=True)             # 상품 상세 내용(다국어)
    lang_tag = Column(String(10), nullable=False, default='en-US') # 언어 태그 (en-US, ko-KR, ja-JP, zh-CN, th-TH, fil-PH 등)
    
    # 타임스탬프
    reg_dt = Column(DateTime, nullable=False, default=func.current_timestamp())
    lastup_dt = Column(DateTime, nullable=False, default=func.current_timestamp())