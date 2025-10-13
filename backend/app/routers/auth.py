from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import requests

from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo, SignUpRequest, SignUpResponse

router = APIRouter(prefix='/auth', tags=["인증"])

# 의존성 주입 함수들
async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """UserRepository 의존성 주입 함수"""
    return UserRepository(db)

async def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    """AuthService 의존성 주입 함수"""
    return AuthService(user_repo)

@router.post("/signup", response_model=SignUpResponse)
async def signup(signup_data: SignUpRequest, auth_service: AuthService = Depends(get_auth_service)):
    """회원가입api"""
    try:
        # 회원가입 처리 (username 중복 체크, 이메일 형식 검증 포함)
        new_user = await auth_service.register_user(
            username=signup_data.username,
            password=signup_data.password,
            fullname=signup_data.fullname,
            email=signup_data.email,
            phone=signup_data.phone
        )
        
        return SignUpResponse(success=True, message="회원가입이 완료되었습니다.", user_seq=new_user.user_seq)
    
    except HTTPException as e:
        # username 중복, 이메일 형식 오류 등
        return SignUpResponse(success=False, message=e.detail, user_seq=None)
    
    except Exception as e:
        print(f"회원가입 오류: {str(e)}")
        return SignUpResponse(success=False, message="회원가입 처리 중 오류가 발생했습니다.", user_seq=None)
    
    

@router.post("/login", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """로그인 - 웹 API 연동 방식

    웹 시스템의 로그인 API를 호출하여 인증을 처리합니다.
    환경별로 다른 API 서버를 사용합니다:
    - 개발: https://dev.smartoko.com/api
    - 스테이징: https://beta.smartoko.com/api
    - 프로덕션: https://beta.smartoko.com/api
    """
    try:
        # 웹 API 엔드포인트 생성 (환경별로 자동 설정됨)
        web_api_url = f"{settings.web_api_base_url}{settings.web_api_login_endpoint}"

        print(f"[웹 API 로그인] {settings.environment} 환경 - {web_api_url}")

        # 웹 API 로그인 시도
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        web_response = requests.post(
            web_api_url,
            json={"username": login_data.username, "password": login_data.password},
            headers=headers,
            timeout=10
        )

        web_data = web_response.json()

        # 웹 API 로그인 실패
        if not web_data.get("success"):
            print(f"웹 API 로그인 실패: {web_data.get('message')}")
            return LoginResponse(
                success=False,
                message=web_data.get("message", "아이디 또는 비밀번호가 틀렸습니다."),
                user=None,
                access_token=None
            )
        
        # 웹 API 로그인 성공 -> DB에서 사용자 정보 조회
        print(f"웹 API 로그인 성공! DB에서 사용자 조회 중: {login_data.username}")
        user = await auth_service.user_repo.find_by_username(login_data.username)
        print(f"DB 조회 결과: {user}")

        if not user:
            print(f"DB에 사용자 없음: {login_data.username}")
            return LoginResponse(
                success=False,
                message="사용자 정보를 찾을 수 없습니다.",
                user=None,
                access_token=None
            )
            
        # 로그인 로그 저장
        client_ip = request.client.host if request.client else "127.0.0.1"
        await auth_service.user_repo.save_login_log(
            user_seq=user.user_seq,
            ip_address=client_ip,
            device_type="APP"
        )
        
        # 사용자 정보 변환
        user_info = UserInfo(
            user_seq=user.user_seq,
            username=user.username,
            fullname=user.fullname,
            email=user.email,
            ai_toggle_yn=user.ai_toggle_yn,
            enabled=user.enabled
        )
        
        print(f"로그인 성공: {login_data.username}")
        
        # 웹토큰 + 사용자 정보 반환
        return LoginResponse(
            success=True,
            message="로그인 성공",
            user=user_info,
            access_token=web_data["data"]["access_token"],
            token_type=web_data["data"].get("token_type", "Bearer"),
            expires_in=web_data["data"].get("expires_in")
        )
        
    except requests.exceptions.RequestException as e:
        # 웹 api 연결 실패
        print(f"웹 api 연결 실패: {str(e)}")
        return LoginResponse(
            success=False,
            message="인증 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
            user=None,
            access_token=None
        )
    
    except Exception as e:
        # 기타 오류
        print(f"로그인 오류: {str(e)}")
        return LoginResponse(
            success=False,
            message="로그인 처리 중 오류가 발생했습니다.",
            user=None,
            access_token=None
        )
    