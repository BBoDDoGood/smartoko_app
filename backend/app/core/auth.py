import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password_sha256(password: str) -> str:
    """sha-256으로 비밀번호 해싱"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """다중 인증 방식 지원: SHA-256, bcrypt 비밀번호 검증"""
    # bcrypt 해시인지 확인 -> bcrypt는 $2b$ 또는 $2a$로 시작
    if hashed_password.startswith(('$2b$', '$2a$', '$2y$')):
        return pwd_context.verify(plain_password, hashed_password)
    
    # SHA-256 해시 검증 -> 64자 길이의 hex 문자열
    elif len(hashed_password) == 64 and all(c in '0123456789abcdef' for c in hashed_password.lower()):
        return hash_password_sha256(plain_password) == hashed_password
    
    # 기타 해시 방식
    else:
        return hash_password_sha256(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """jwt 토큰 검증 및 데이터 추출"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def generate_session_id() -> str:
    return secrets.token_urlsafe(32)