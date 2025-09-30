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

def hash_password_sha512(password: str) -> str:
    """sha-512로 비밀번호 해싱"""
    return hashlib.sha512(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """다중 인증 방식 지원: SHA-256, bcrypt, 레거시 형식 비밀번호 검증"""
    print(f"🔐 verify_password 호출: password='{plain_password}', stored_hash='{hashed_password[:50]}...'")

    # bcrypt 해시인지 확인 -> bcrypt는 $2b$ 또는 $2a$로 시작
    if hashed_password.startswith(('$2b$', '$2a$', '$2y$')):
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"🔐 bcrypt 검증 결과: {result}")
        return result

    # 레거시 형식: {SHA-256}{base64}hex 패턴 처리
    elif hashed_password.startswith('{SHA-256}'):
        import base64

        # {SHA-256}{base64}hex 형식에서 base64와 hex 부분 분리
        remaining = hashed_password[10:]  # {SHA-256} 제거
        if '}' in remaining:
            parts = remaining.split('}')
            base64_part = parts[0]
            hex_part = parts[1] if len(parts) > 1 else ""

            plain_hash_256 = hash_password_sha256(plain_password)
            plain_hash_512 = hash_password_sha512(plain_password)

            # 1. Base64 부분 디코딩해서 비교 (SHA-256, SHA-512 둘 다)
            try:
                decoded_bytes = base64.b64decode(base64_part)
                decoded_hex = decoded_bytes.hex()
                if plain_hash_256 == decoded_hex or plain_hash_512 == decoded_hex:
                    return True
            except Exception:
                pass

            # 2. 마지막 hex 부분과 비교 (SHA-256: 64자, SHA-512: 128자)
            if len(hex_part) == 64 and all(c in '0123456789abcdef' for c in hex_part.lower()):
                if plain_hash_256 == hex_part:
                    return True
            elif len(hex_part) == 128 and all(c in '0123456789abcdef' for c in hex_part.lower()):
                if plain_hash_512 == hex_part:
                    return True

        # 레거시 형식이지만 parsing 실패시 전체 비교
        return hash_password_sha256(plain_password) == hashed_password

    # 표준 SHA-256 해시 검증 -> 64자 길이의 hex 문자열
    elif len(hashed_password) == 64 and all(c in '0123456789abcdef' for c in hashed_password.lower()):
        calculated_hash = hash_password_sha256(plain_password)
        result = calculated_hash == hashed_password
        print(f"🔐 SHA-256 검증: calculated='{calculated_hash}', stored='{hashed_password}', result={result}")
        return result

    # 표준 SHA-512 해시 검증 -> 128자 길이의 hex 문자열
    elif len(hashed_password) == 128 and all(c in '0123456789abcdef' for c in hashed_password.lower()):
        calculated_hash = hash_password_sha512(plain_password)
        result = calculated_hash == hashed_password
        print(f"🔐 SHA-512 검증: calculated='{calculated_hash[:50]}...', stored='{hashed_password[:50]}...', result={result}")
        return result

    # 기타 해시 방식 - 마지막 시도 (SHA-256, SHA-512 둘 다 시도)
    else:
        sha256_hash = hash_password_sha256(plain_password)
        sha512_hash = hash_password_sha512(plain_password)
        result = (sha256_hash == hashed_password or sha512_hash == hashed_password)
        print(f"🔐 기타 해시 검증: sha256='{sha256_hash[:30]}...', sha512='{sha512_hash[:30]}...', result={result}")
        return result

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
    """36자 UUID 세션 ID 생성 (데이터베이스 CHAR(36) 컬럼에 맞춤)"""
    import uuid
    return str(uuid.uuid4())