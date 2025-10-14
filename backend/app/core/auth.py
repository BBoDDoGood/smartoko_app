import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# bcrypt 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ 비밀번호 검증 bcrypt 해싱 검증
    - 임시 => 앱에서 가입한 사용자만 로그인 가능
    """
    try:
        # 긴 비밀번호를 SHA-256으로 먼저 해싱
        sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        
        # bcrypt 해시 검증 ({bcrypt} prefix 있는 경우)
        if hashed_password.startswith('{bcrypt}'):
            bcrypt_hash = hashed_password.replace('{bcrypt}', '')
            return pwd_context.verify(sha256_hash, bcrypt_hash)
        # bcrypt 해시 검증 (prefix 없는 경우)
        elif hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            return pwd_context.verify(sha256_hash, hashed_password)
        else:
            print(f"지원하지 않는 해시 형식: {hashed_password[:20]}")
            return False
    except Exception as e:
        print(f"비밀번호 검증 오류: {e}")
        return False

def hash_password(plain_password: str) -> str:
    """비밀번호 해싱
    bcrypt 해시 생성 후 {bcrypt} prefix 추가
    """
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()

    bcrypt_hash = pwd_context.hash(sha256_hash)
    return f"{{bcrypt}}{bcrypt_hash}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성
    - data: 토큰에 포함할 데이터
    - expires_delta: 토큰 만료 시간
    """
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
    # 만료 시간 추가
    to_encode.update({"exp": expire})
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증 및 데이터 추출
    - token: 검증할 JWT 토큰
    """
    try:
        # JWT 토큰 디코딩 및 검증
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        # 토큰 만료, 서명 오류
        return None

def generate_session_id() -> str:
    """세션 ID 생성 (24자리 URL-safe 문자열)"""
    return secrets.token_urlsafe(24)