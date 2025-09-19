from sqlalchemy import Column, Integer, String, DateTime, CHAR
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func
from app.core.database import Base

class Group(Base):
    """그룹 테이블"""
    __tablename__ = "tbl_group"
    
    # 기본키
    group_seq = Column(Integer, primary_key=True, autoincrement=True)
    
    # 연결 관계
    user_seq = Column(Integer, nullable=False)
    
    # 그룹 정보
    p_group_seq = Column(Integer, nullable=True)
    group_icon = Column(String(128), nullable=True)
    group_name = Column(String(64), nullable=False)   #그룹명
    
    depth = Column(TINYINT(4), nullable=False, default=1)  #계층 (1~5)
    is_protected = Column(CHAR(1), nullable=False, default='N')  #삭제 보호 여부(Y 이면 삭제불가)
    
    reg_dt = Column(DateTime, nullable=False)

    # 관계 정의
    user = relationship("User", primaryjoin="Group.user_seq == User.user_seq", foreign_keys=[user_seq])
    parent_group = relationship("Group", remote_side=[group_seq], primaryjoin="Group.p_group_seq == Group.group_seq",
    foreign_keys=[p_group_seq])