from sqlalchemy import Column, Integer, String, DateTime, Text, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """사용자 테이블"""
    __tablename__ = "tbl_user"
    
    # 기본 사용자 정보
    user_seq = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(256), nullable=False)  # SHA512
    fullname = Column(String(128), nullable=True)
    email = Column(String(128), nullable=True)
    phone = Column(String(16), nullable=True)

    # 상태 관리
    enabled = Column(CHAR(1), nullable=False, default='0')  # 활성화 여부(0:비활성화 / 1:활성화)
    password_wrong_cnt = Column(Integer, nullable=False, default=0)  # DB에서 NOT NULL
    status = Column(CHAR(1), nullable=False, default='B')  # B 기본값
    status_msg = Column(Text, nullable=True)

    # 제한 설정
    group_limit = Column(Integer, default=5)
    device_limit = Column(Integer, default=5)

    # 알림 설정
    alarm_yn = Column(CHAR(1), default='N')
    alarm_line_yn = Column(CHAR(1), default='N')
    alarm_line_to = Column(String(128), nullable=True)
    alarm_whatsapp_yn = Column(CHAR(1), default='N')

    # AI 설정
    ai_status = Column(CHAR(1), default='C')
    ai_toggle_yn = Column(CHAR(1), default='N')

    # 타임스탬프
    reg_dt = Column(DateTime, nullable=True)
    lastup_dt = Column(DateTime, nullable=True)
    last_access_dt = Column(DateTime, nullable=True)

    # 관계 정의
    subscriptions = relationship("ModelProductSubscription", back_populates="user")
    user_roles = relationship("UserRole", back_populates="user")
    
class LoginLog(Base):
    """로그인 로그 테이블"""
    __tablename__ = "tbl_logs_login"

    logs_seq = Column(Integer, primary_key=True, autoincrement=True)
    user_seq = Column(Integer, nullable=True)
    ip_addr = Column(String(39), nullable=True)
    country_code = Column(CHAR(2), default='99')
    device_type = Column(CHAR(3), nullable=True)
    reg_dt = Column(DateTime, nullable=True)

class SpringSession(Base):
    """Spring Session 테이블"""
    __tablename__ = "SPRING_SESSION"

    PRIMARY_ID = Column(CHAR(36), primary_key=True)
    SESSION_ID = Column(CHAR(36), unique=True, nullable=False, index=True)
    CREATION_TIME = Column(Integer, nullable=False)
    LAST_ACCESS_TIME = Column(Integer, nullable=False)
    MAX_INACTIVE_INTERVAL = Column(Integer, nullable=False)
    EXPIRY_TIME = Column(Integer, nullable=False)
    PRINCIPAL_NAME = Column(String(100), nullable=True)

class SpringSessionAttributes(Base):
    """Spring Session 속성 테이블 - 세션 데이터 저장"""
    __tablename__ = "SPRING_SESSION_ATTRIBUTES"

    SESSION_PRIMARY_ID = Column(CHAR(36), primary_key=True)
    ATTRIBUTE_NAME = Column(String(200), primary_key=True)
    ATTRIBUTE_BYTES = Column(Text, nullable=False)  # blob -> Text로 JSON 저장

class UserRole(Base):
    """사용자 권한 테이블 - tbl_user_roles"""
    __tablename__ = "tbl_user_roles"

    user_roles_seq = Column(Integer, primary_key=True, autoincrement=True)
    roles_seq = Column(Integer, nullable=False)  # 권한 레벨 (10=일반, 11, 13 = 관리자?)
    user_seq = Column(Integer, ForeignKey("tbl_user.user_seq"), nullable=False)
    reg_dt = Column(DateTime, nullable=True)

    # 관계 정의
    user = relationship("User", back_populates="user_roles")