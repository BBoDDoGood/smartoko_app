import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    환경별 설정을 관리하는 클래스
    .env 파일에서 자동으로 값을 읽어옴
    """
    
    # 기본 환경 설정
    environment: str = Field(default="development", description="현재 실행 환경")
    debug: bool = Field(default=True, description="디버그 모드")
    
    # 서버 설정
    host: str = Field(default="127.0.0.1", description="서버 호스트")
    port: int = Field(default=8000, description="서버 포트")
    
    # 데이터베이스 설정
    db_host: str = Field(..., description="DB 호스트")
    db_port: int = Field(default=3306, description="DB 포트")
    db_user: str = Field(..., description="DB 사용자명")
    db_password: str = Field(..., description="DB 비밀번호")
    db_name: str = Field(..., description="DB 이름")
    
    # JWT 보안 설정
    jwt_secret_key: str = Field(..., description="JWT 암호화 키")
    jwt_access_token_expire_minutes: int = Field(default=30, description="JWT 토큰 만료시간(분)")
    
    # API 설정
    api_version: str = Field(default="v1", description="API 버전")
    api_prefix: str = Field(default="/api", description="API 접두사")
    
    # 로그 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
    
    # CORS 설정
    cors_origins: List[str] = Field(default=["*"], description="허용된 CORS 도메인 목록")

    # 웹 API 연동 설정 (Spring 서버)
    web_api_base_url: str = Field(default="https://web.smartoko.com", description="웹 서버 API 기본 URL")
    web_api_enabled: bool = Field(default=True, description="웹 API 연동 활성화 여부")
    web_api_login_endpoint: str = Field(default="/api/auth/login", description="웹 로그인 API 엔드포인트") 
    
    #파일 저장소 설정 ->환경별 분리
    upload_base_directory: str = Field(default="uploads", description="업로드 파일 기본 디렉토리")
    static_files_url_prefix: str = Field(default="/uploads", description="파일 서빙 url 접두사")
    
    #파일 크기 제한
    max_image_file_size_mb: int = Field(default=10, description="최대 이미지 파일 크기")
    max_video_file_size_mb: int = Field(default=50, description="최대 동영상 클립 파일 크기")
    
    # 동영상 클립 설정
    video_clip_before_detection_seconds: int = Field(default=3, description="탐지 전 포함 시간 (초)")
    video_clip_after_detection_seconds: int = Field(default=7, description="탐지 후 포함 시간 (초)")
    video_clip_output_quality: str = Field(default="720p", description="클립 출력 품질")
    
    # 썸네일 설정
    thumbnail_width_pixels: int = Field(default=320, description="썸네일 가로 크기")
    thumbnail_height_pixels: int = Field(default=240, description="썸네일 세로 크기")
    thumbnail_jpeg_quality: int = Field(default=85, description="썸네일 JPEG 품질 (1-100)")
    
    # 데이터베이스 URL 생성
    @property
    def database_url(self) -> str:
        """MySQL 연결 URL을 생성합니다"""
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        # 환경변수 파일명 설정
        case_sensitive = False
        
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """
            환경에 따라 다른 .env 파일을 로드합니다
            """
            environment = os.getenv("ENVIRONMENT", "development")
            env_file = f".env.{environment}"
            
            # .env 파일이 존재하는지 확인
            if os.path.exists(env_file):
                return (
                    init_settings,
                    env_settings,
                    file_secret_settings,
                )
            else:
                # 기본 .env 파일 사용
                return (init_settings, env_settings, file_secret_settings)

def get_settings() -> Settings:
    """
    환경 설정을 가져오는 함수
    환경변수 ENVIRONMENT에 따라 다른 설정 파일을 로드
    
    사용법:
    - 개발환경: ENVIRONMENT=development
    - 스테이징환경: ENVIRONMENT=staging  
    - 프로덕션환경: ENVIRONMENT=production
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    # 환경별로 다른 .env 파일 로드
    env_file = f".env.{environment}"
    
    if os.path.exists(env_file):
        print(f"📋 환경설정 로드중: {env_file}")
        return Settings(_env_file=env_file)
    else:
        print(f"⚠️  {env_file} 파일을 찾을 수 없습니다. 기본 설정을 사용합니다.")
        return Settings()

# 전역 설정 객체
settings = get_settings()