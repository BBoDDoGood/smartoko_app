from sqlalchemy import Column, Integer, String, DateTime, CHAR, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ModelProductSubscription(Base):
    """모델 제품 구독 테이블"""
    __tablename__ = "tbl_model_product_subscription"
    
    # 기본 키
    subscription_seq = Column(Integer, primary_key=True, autoincrement=True)
    
    # 외래키들
    user_seq = Column(Integer, ForeignKey("tbl_user.user_seq"), nullable=False)
    model_product_seq = Column(Integer, ForeignKey("tbl_model_product.model_product_seq"), nullable=False)
    model_seq = Column(Integer, ForeignKey("tbl_model.model_seq"), nullable=True)
    
    # 구독 상태
    subscription_status = Column(CHAR(1), nullable=False, default='P') # 구독 상태(A:활성/E:만료/C:취소/P:결제대기)
    payment_status = Column(CHAR(1), nullable=False, default='P')   #결제 상태(S:성공/P:대기/F:실패/R:환불)
    
    # 결제 정보
    payment_method = Column(String(32), nullable=True)
    payment_amount = Column(DECIMAL(12, 2), nullable=True)
    usage_limit = Column(Integer, nullable=True)
    
    # 구독 기간
    subscribed_dt = Column(DateTime, nullable=False)
    expires_dt = Column(DateTime, nullable=True)
    cancelled_dt = Column(DateTime, nullable=True)
    
    # 취소/ 갱신 정보
    cancel_reason = Column(String(256), nullable=True)
    auto_renewal_yn = Column(CHAR(1), nullable=False, default='N')  # Y:자동갱신, N:수동갱신
    
    # 타임 스탬프
    reg_dt = Column(DateTime, nullable=False, default=func.current_timestamp())
    lastup_dt = Column(DateTime, nullable=True, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # 관계 정의
    user = relationship("User", back_populates="subscriptions")
    model_product = relationship("ModelProduct", back_populates="subscriptions")
    
    class Config:
        from_attributes = True
        
DeviceProductSubscription = ModelProductSubscription