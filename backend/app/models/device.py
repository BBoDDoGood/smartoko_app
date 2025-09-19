from sqlalchemy import Column, Integer, String, DateTime, Text, CHAR, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Device(Base):
    """디바이스 테이블"""
    __tablename__ = "tbl_device"
    
    # 기본 키
    device_seq = Column(Integer, primary_key=True, autoincrement=True)

    # 연결 관계
    user_seq = Column(Integer, ForeignKey('tbl_user.user_seq'), nullable=False)
    group_seq = Column(Integer, ForeignKey('tbl_group.group_seq'), nullable=True)  # 그룹 참조
    product_seq = Column(Integer, nullable=True)  # 제품 참조
    
    # 디바이스 정보
    device_label = Column(String(128), nullable=True)   #사용자가 확인할 수 있는 장비명
    device_type = Column(CHAR(1), nullable=True)    #장비 타입(A:RTSP / B:bodycam / C:RTMP)
    device_id = Column(String(64), nullable=True)   #장비ID (Bodycam 장비에서 사용)
    
    # 스트리밍 URL
    stream_id = Column(String(64), nullable=True)   #Media server와 연결하여 사용할 strem id (RTSP,RTMP 장비에서 사용)
    rtsp_url = Column(String(64), nullable=True)   #RTSP URL (RTSP,RTMP 장비에서 사용)
    
    # 타임스탬프
    reg_dt = Column(DateTime, nullable=True)

    # 관계 정의
    user = relationship("User")
    group = relationship("Group")
    
 