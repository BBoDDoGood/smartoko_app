from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """로그인 요청"""
    username: str = Field(description="사용자명")
    password: str = Field(description="비밀번호")
    
class UserInfo(BaseModel):
    """사용자 기본 정보"""
    user_seq: int = Field(description="사용자 고유 번호")
    username: str = Field(description="사용자명")
    fullname: Optional[str] = Field(None, description="이름")
    enabled: str = Field(description="활성화 상태 (0: 비활성, 1: 활성)")
    
    class Config:
        from_attributes = True
        
class LoginResponse(BaseModel):
    """로그인 응답"""
    success: bool = Field(description="성공 여부")
    message: str = Field(description="응답 메시지")
    user: Optional[UserInfo] = Field(None, description="사용자 정보")
    access_token: Optional[str] = Field(None, description="JWT 토큰")
    token_type: str = Field(default="Bearer", description="토큰 타입")
    expires_in: Optional[int] = Field(None, description="토큰 만료 시간 (초)")
    

