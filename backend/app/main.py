from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, dashboard

# 환경별 설정으로 FastAPI 앱 생성
app = FastAPI(
    title="SmartOkO API",
    description="SmartOkO AI 모니터링 시스템 API", 
    version=settings.api_version,
    debug=settings.debug,
    docs_url=f"{settings.api_prefix}/docs" if settings.debug else None,  # 프로덕션에서는 문서 비활성화
    redoc_url=f"{settings.api_prefix}/redoc" if settings.debug else None,
)

# CORS 설정 (환경별로 다른 도메인 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)

@app.get("/")
async def root():
    """기본 엔드포인트 - 서버 상태 확인"""
    return {
        "message": "SmartOkO API 서버가 실행중입니다!",
        "environment": settings.environment,
        "version": settings.api_version,
        "debug": settings.debug
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트 - 서버 상태 모니터링용"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }