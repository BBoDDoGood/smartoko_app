from pydantic import BaseModel, Field
from typing import Optional

class SignUpRequest(BaseModel):
    """회원가입 요청"""
    username: str = Field(description="로그인 ID (이메일 형식)")
    password: str = Field(description="비밀번호")
    fullname: Optional[str] = Field(None, description="이름")
    email: Optional[str] = Field(None, description="이메일")
    phone: Optional[str] = Field(None, description="전화번호")
    
    
class SignUpResponse(BaseModel):
    """회원가입 응답"""
    success: bool = Field(description="성공 여부")
    message: str = Field(description="응답 메시지")
    user_seq: Optional[int] = Field(None, description="생성된 사용자 번호")

class LoginRequest(BaseModel):
    """로그인 요청"""
    username: str = Field(description="사용자명")
    password: str = Field(description="비밀번호")
    
class UserInfo(BaseModel):
    """사용자 기본 정보"""
    user_seq: int = Field(description="사용자 고유 번호")
    username: str = Field(description="사용자명")
    fullname: Optional[str] = Field(None, description="이름")
    email: Optional[str] = Field(None, description="이메일 연락처")
    phone: Optional[str] = Field(None, description="전화번호")

    # 보안 및 상태
    enabled: str = Field(description="활성화 상태 (0: 비활성, 1: 활성)")
    status: str = Field(description="사용자 상태 (A/B/C/D/F)")
    status_msg: Optional[str] = Field(None, description="상태 메시지")
    password_wrong_cnt: int = Field(default=0, description="비밀번호 틀림 횟수")

    # 제한 설정
    group_limit: int = Field(default=5, description="그룹 생성 제한")
    device_limit: int = Field(default=5, description="디바이스 등록 제한")

    # 알림 설정
    alarm_yn: Optional[str] = Field(None, description="알림 on/off (Y/N)")
    alarm_line_yn: Optional[str] = Field(None, description="LINE 알림 (Y/N)")
    alarm_whatsapp_yn: Optional[str] = Field(None, description="WhatsApp 알림 (Y/N)")

    # AI 설정
    ai_status: Optional[str] = Field(None, description="AI 상태")
    ai_toggle_yn: Optional[str] = Field(None, description="AI 기능 토글 (Y/N)")

    # 타임스탬프
    last_access_dt: Optional[str] = Field(None, description="마지막 접속일시")
    reg_dt: Optional[str] = Field(None, description="가입일시")

    class Config:
        from_attributes = True
        
class LoginResponse(BaseModel):
    """로그인 응답"""
    success: bool = Field(description="성공 여부")
    message: str = Field(description="응답 메시지 (에러 코드)")
    user: Optional[UserInfo] = Field(None, description="사용자 정보")
    access_token: Optional[str] = Field(None, description="JWT 토큰")
    token_type: str = Field(default="Bearer", description="토큰 타입")
    expires_in: Optional[int] = Field(None, description="토큰 만료 시간 (초)")
    error_data: Optional[dict] = Field(None, description="에러 관련 추가 데이터 (예: password_wrong_count)")
    

    

