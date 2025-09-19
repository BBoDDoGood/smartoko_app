"""JWT 토큰 + SHA 세션 동시 지원 인증 의존성 주입 모듈"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository

# HTTPBearer 토큰 스키마 생성 (JWT용)
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Header(None, alias="X-Session-Token"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """JWT 토큰 또는 SHA 세션을 검증하여 현재 사용자 정보 반환
    - JWT Bearer 토큰: Authorization: Bearer <jwt_token>
    - 세션 토큰: X-Session-Token: <session_token>
    - 쿠키 세션: session_token 쿠키
    """

    # 인증 실패 에러 준비
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다. JWT 토큰 또는 세션이 필요합니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_repository = UserRepository(db)

    # JWT 토큰 인증 시도
    if credentials and credentials.credentials:
        try:
            token = credentials.credentials
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])

            # user_seq 추출
            user_seq_str: str = payload.get("sub")
            if user_seq_str is not None:
                user_seq = int(user_seq_str)
                user = await user_repository.get_user_with_basic_info(user_seq)

                if user is not None:
                    return user

        except (JWTError, ValueError) as e:
            print(f"JWT 토큰 인증 실패: {str(e)}")
            # JWT 실패 시 세션 방식으로 fallback
            pass

    # 세션 토큰 인증 시도
    if session_token:
        try:
            user = await _verify_session_token(session_token, user_repository)
            if user:
                return user
        except Exception as e:
            print(f"세션 토큰 헤더 인증 실패: {str(e)}")
            pass

    # 세션 토큰 인증 시도
    session_token_cookie = request.cookies.get("session_token")
    if session_token_cookie:
        try:
            user = await _verify_session_token(session_token_cookie, user_repository)
            if user:
                return user
        except Exception as e:
            print(f"세션 토큰 쿠키 인증 실패: {str(e)}")
            pass

    # 모든 인증 방식 실패
    raise credentials_exception

async def store_session_token(session_token: str, user_seq: int, session_id: str, db: AsyncSession) -> None:
    """DB 세션 토큰 저장 - Spring Session 테이블"""
    import uuid
    import json
    from datetime import datetime
    from app.models.user import SpringSession, SpringSessionAttributes

    try:
        # 1시간 후 만료
        now_ms = int(datetime.now().timestamp() * 1000)
        expires_ms = now_ms + (60 * 60 * 1000)  # 1시간

        # UUID 생성
        primary_id = str(uuid.uuid4())

        # 세션 기본 정보 저장
        spring_session = SpringSession(
            PRIMARY_ID=primary_id,
            SESSION_ID=session_id,  # 원본 세션 ID
            CREATION_TIME=now_ms,
            LAST_ACCESS_TIME=now_ms,
            MAX_INACTIVE_INTERVAL=3600,  # 1시간
            EXPIRY_TIME=expires_ms,
            PRINCIPAL_NAME=str(user_seq)  # 사용자 식별용
        )

        # 세션 속성 저장 (user_seq와 session_token)
        session_attrs = [
            SpringSessionAttributes(
                SESSION_PRIMARY_ID=primary_id,
                ATTRIBUTE_NAME="user_seq",
                ATTRIBUTE_BYTES=json.dumps(user_seq)
            ),
            SpringSessionAttributes(
                SESSION_PRIMARY_ID=primary_id,
                ATTRIBUTE_NAME="session_token",
                ATTRIBUTE_BYTES=json.dumps(session_token)
            )
        ]

        # DB에 저장
        db.add(spring_session)
        for attr in session_attrs:
            db.add(attr)

        await db.commit()
        print(f"세션 저장 성공: {session_token[:16]}... -> user_seq: {user_seq}")

    except Exception as e:
        await db.rollback()
        print(f"세션 저장 실패: {str(e)}")

async def _verify_session_token(session_token: str, user_repository: UserRepository) -> Optional[User]:
    """실운영급 DB 기반 세션 토큰 검증 - Spring Session 테이블 활용"""
    import json
    from datetime import datetime
    from app.models.user import SpringSession, SpringSessionAttributes
    from sqlalchemy import select, and_

    try:
        # 토큰 형식 검증
        if not (len(session_token) == 64 and all(c in '0123456789abcdef' for c in session_token.lower())):
            return None

        # 세션 조회
        query = select(
            SpringSession.PRIMARY_ID,
            SpringSession.EXPIRY_TIME,
            SpringSession.PRINCIPAL_NAME
        ).select_from(
            SpringSession.join(
                SpringSessionAttributes,
                SpringSession.PRIMARY_ID == SpringSessionAttributes.SESSION_PRIMARY_ID
            )
        ).where(
            and_(
                SpringSessionAttributes.ATTRIBUTE_NAME == "session_token",
                SpringSessionAttributes.ATTRIBUTE_BYTES == json.dumps(session_token)
            )
        )

        result = await user_repository.db.execute(query)
        session_row = result.fetchone()

        if not session_row:
            print(f"세션 토큰 없음: {session_token[:16]}...")
            return None

        # 만료 시간 확인
        current_ms = int(datetime.now().timestamp() * 1000)
        if current_ms > session_row.EXPIRY_TIME:
            print(f"세션 토큰 만료: {session_token[:16]}...")
            # 만료된 세션 제거
            await _cleanup_expired_session(session_row.PRIMARY_ID, user_repository.db)
            return None

        # 사용자 정보 조회
        user_seq = int(session_row.PRINCIPAL_NAME)
        user = await user_repository.get_user_with_basic_info(user_seq)

        if user:
            print(f"세션 토큰 인증 성공: {session_token[:16]}... -> user_seq: {user_seq}")
            # 마지막 접근 시간 업데이트
            await _update_session_access_time(session_row.PRIMARY_ID, user_repository.db)
        else:
            print(f"세션 토큰 사용자 없음: {session_token[:16]}... -> user_seq: {user_seq}")

        return user

    except Exception as e:
        print(f"세션 토큰 검증 오류: {str(e)}")
        return None

async def _cleanup_expired_session(primary_id: str, db: AsyncSession) -> None:
    """만료된 세션 정리"""
    from app.models.user import SpringSession, SpringSessionAttributes
    from sqlalchemy import delete

    try:
        # 속성 먼저 삭제
        await db.execute(
            delete(SpringSessionAttributes).where(
                SpringSessionAttributes.SESSION_PRIMARY_ID == primary_id
            )
        )
        # 세션 삭제
        await db.execute(
            delete(SpringSession).where(SpringSession.PRIMARY_ID == primary_id)
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"만료 세션 정리 실패: {str(e)}")

async def _update_session_access_time(primary_id: str, db: AsyncSession) -> None:
    """세션 마지막 접근 시간 업데이트"""
    from app.models.user import SpringSession
    from sqlalchemy import update
    from datetime import datetime

    try:
        current_ms = int(datetime.now().timestamp() * 1000)
        await db.execute(
            update(SpringSession)
            .where(SpringSession.PRIMARY_ID == primary_id)
            .values(LAST_ACCESS_TIME=current_ms)
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"세션 접근 시간 업데이트 실패: {str(e)}")