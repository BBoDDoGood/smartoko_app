from re import M
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.auth import create_access_token, generate_session_id
import hashlib
from datetime import datetime

class AuthService:
    """인증 서비스"""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def authenticate_user(self, username: str, password: str) -> User:
        """사용자 인증 및 검증"""
        
        # 사용자 인증 (비밀번호 검증 + 계정 상태 확인 포함)
        user = await self.user_repo.verify_user_credentials(username, password)
        
        if not user:
            raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸거나 계정이 비활성화 되었습니다.")
        return user
    
    async def create_app_login(self, user: User, ip_address: str = "127.0.0.1") -> dict:
        """앱 로그인 처리 및 jwt + 세션 토큰 생성
        - user: 인증된 사용자 객체
        - ip_address: 클라이언트 ip 주소 (GeoIP 국가 코드 추출용)
        """
        # jwt 액세스 토큰 생성 - 앱 로그인 시 사용
        access_token = create_access_token(
            data={
                "sub": str(user.user_seq),
                "username": user.username
            }
        )

        # sha256 세션 id 생성 - 웹 호환용
        session_id = generate_session_id()
        session_data = f"{user.user_seq}{session_id}{datetime.now()}"
        session_token = hashlib.sha256(session_data.encode()).hexdigest()

        # 세션 토큰을 실운영급 DB 기반 저장소에 저장
        from app.dependencies.auth import store_session_token
        await store_session_token(session_token, user.user_seq, session_id, self.user_repo.db)

        #로그인 로그 저장 ( ip -> 국가 코드 자동 변환 포함)
        await self.user_repo.save_login_log(
            user_seq=user.user_seq,
            ip_address=ip_address,
            device_type="APP"
        )

        # 클라이언트에게 반환할 로그인 응답 데이터
        return {
            "access_token": access_token,
            "session_token": session_token,
            "session_id": session_id,
            "token_type": "bearer",
            "expires_in": 3600
        }
        