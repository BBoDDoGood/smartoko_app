from fastapi import HTTPException
import hashlib
from datetime import datetime
import re

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.auth import create_access_token, generate_session_id, hash_password

class AuthService:
    """인증 서비스"""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def register_user(self, username: str, password: str, fullname: str = None, email: str = None, phone: str = None) -> User:
        """회원가입 처리 - 앱 전용
        - username: 사용자 로그인 ID (이메일 형식)
        - fullname: 사용자 이름
        - email: 사용자 이메일
        - phone: 사용자 전화번호
        - password: 평문 비밀번호 (bcrypt 해싱 처리)
        """
        # username 중복 확인
        existing_user = await self.user_repo.find_by_username(username)
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 사용 중인 로그인 ID입니다.")
        
        # username 이메일 형식 검증
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, username):
            raise HTTPException(status_code=400, detail="아이디는 이메일 형식이어야 합니다.")
        
        # 비밀번호 해싱(bcrypt)
        hashed_password = hash_password(password)
        
        # 사용자 생성(enabled='1' - 즉시 활성화)
        new_user = await self.user_repo.create_user(
            username=username,
            email=email,
            hashed_password=hashed_password,
            fullname=fullname,
            phone=phone
        )
        
        if not new_user:
            raise HTTPException(status_code=500, detail="회원가입 처리 중 오류가 발생했습니다.")
        
        return new_user
        
        
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
        