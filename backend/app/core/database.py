from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLAlchemy Base 클래스
Base = declarative_base()

# 비동기 데이터베이스 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 개발환경에서는 SQL 쿼리 로그 출력
    pool_pre_ping=True,   # 연결 상태 체크
    pool_recycle=3600,    # 1시간마다 연결 재생성
)

# 비동기 세션 팩토리
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 데이터베이스 세션 의존성 함수
async def get_db() -> AsyncSession:
    """
    FastAPI 의존성 주입용 데이터베이스 세션 생성 함수
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# 데이터베이스 연결 테스트
async def test_db_connection():
    """데이터베이스 연결을 테스트합니다"""
    try:
        async with async_session() as session:
            result = await session.execute("SELECT 1")
            print("✅ 데이터베이스 연결 성공!")
            return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False