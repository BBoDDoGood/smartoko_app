from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo

router = APIRouter(prefix='/auth', tags=["인증"])

# 의존성 주입 함수들
async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """UserRepository 의존성 주입 함수"""
    return UserRepository(db)

async def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    """AuthService 의존성 주입 함수"""
    return AuthService(user_repo)

@router.post("/login/app", response_model=LoginResponse)
async def login_app(request: Request, login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """모바일 앱 로그인 api"""
    try:
        # 사용자 인증 (아이디/비밀번호 확인)
        user = await auth_service.authenticate_user(login_data.username, login_data.password)
        
        # jwt 토큰 및 세션 생성, 로그인 로그 저장
        client_ip = request.client.host if request.client else "127.0.0.1"
        auth_data = await auth_service.create_app_login(user, client_ip)
        
        # UserInfo -> 스키마로 사용자 정보 변환
        user_info = UserInfo(
            user_seq=user.user_seq,
            username=user.username,
            fullname=user.fullname,
            enabled=user.enabled
        )
        
        # 성공 응답 반환
        return LoginResponse(
            success=True,
            message="로그인 성공",
            user=user_info,
            access_token=auth_data["access_token"],
            token_type=auth_data.get("token_type", "bearer"),
            expires_in=auth_data.get("expires_in")
        )
        
    except Exception as e:
        # 로그인 실패
        print(f"로그인 실패: {str(e)}")
        return LoginResponse(
            success=False,
            message="아이디 또는 비밀번호가 틀렸습니다.",
            user=None,
            access_token=None
        )