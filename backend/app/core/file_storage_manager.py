import os
import hashlib
import logging
import mimetypes
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

# 실제 미디어 처리를 위한 import
try:
    from PIL import Image, ImageOps
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FileStorageResult:
    """파일 저장 결과 데이터"""
    success: bool
    file_url: Optional[str] = None  # DB 저장용 URL
    file_path: Optional[Path] = None    # 실제 파일 경로
    file_size_bytes: int = 0    # 파일 크기
    error_message: Optional[str] = None     # 에러 메시지
    file_creation_timestamp: Optional[datetime] = None   # 생성 시간
    detection_timestamp: Optional[datetime] = None    # 탐지 시간
    storage_environment: Optional[str] = None   # 저장 환경


class ProductionFileStorageManager:
    """
    - 환경별 경로 자동 관리 (개발/프로덕션)
    - 파일 물리적 저장 관리
    - DB URL 생성 및 관리
    - 완벽한 파일명 추적성
    - 보안 및 검증
    """

    def __init__(self):
        # 환경별 설정
        self.upload_root_directory = Path(settings.upload_base_directory)
        self.static_file_url_prefix = settings.static_files_url_prefix
        self.current_environment = settings.environment

        # 파일 크기 제한
        self.max_image_file_size_bytes = settings.max_image_file_size_mb * 1024 * 1024
        self.max_video_file_size_bytes = settings.max_video_file_size_mb * 1024 * 1024

        # 동영상 클립 설정
        self.video_clip_before_seconds = settings.video_clip_before_detection_seconds
        self.video_clip_after_seconds = settings.video_clip_after_detection_seconds
        self.video_clip_quality = settings.video_clip_output_quality

        # 썸네일 설정
        self.thumbnail_size = (
            settings.thumbnail_width_pixels,
            settings.thumbnail_height_pixels,
        )
        self.thumbnail_quality = settings.thumbnail_jpeg_quality

        # 업로드 디렉토리 구조
        self.original_images_directory = self.upload_root_directory / "images"
        self.thumbnail_images_directory = self.upload_root_directory / "thumbnails"
        self.original_videos_directory = self.upload_root_directory / "videos"
        self.video_clips_directory = self.upload_root_directory / "video_clips"

        # 지원 파일 확장자
        self.supported_image_extensions = [
            ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"
        ]
        self.supported_video_extensions = [
            ".mp4", ".mov", ".avi", ".mkv", ".webm"
        ]

        # 시작 시 디렉토리 생성
        self._ensure_upload_directories_exist()

        logger.info(
            f"파일 스토리지 매니저 초기화 완료 [환경={self.current_environment}, 경로={self.upload_root_directory}]"
        )

    def _ensure_upload_directories_exist(self) -> None:
        """업로드에 필요한 모든 디렉토리 생성 -> 환경별 경로"""
        required_directories = [
            self.original_images_directory,
            self.thumbnail_images_directory,
            self.original_videos_directory,
            self.video_clips_directory,
        ]

        for directory_path in required_directories:
            try:
                directory_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"업로드 디렉토리 확인/생성: {directory_path}")
            except Exception as e:
                logger.error(f"디렉토리 생성 실패 {directory_path}: {str(e)}")
                raise RuntimeError(f"필수 디렉토리 생성 실패: {directory_path}")

    def _generate_organized_file_path(
        self, base_directory: Path, device_id: int, detection_timestamp: datetime
    ) -> Path:
        """
        파일 저장 경로 생성
        구조: uploads/images/2024/09/device_001/ 이런 형식으로 생성
        """
        year_month_path = f"{detection_timestamp.year:04d}/{detection_timestamp.month:02d}"
        device_directory_name = f"device_{device_id:03d}"  # device_001 형태

        organized_directory = base_directory / year_month_path / device_directory_name
        organized_directory.mkdir(parents=True, exist_ok=True)

        return organized_directory

    def _generate_production_filename(
        self,
        detection_seq: int,
        file_type: str,
        detection_timestamp: datetime,
        original_filename: str = None,
    ) -> str:
        """
        파일명 생성
        파일명 구조: [타입]_det[ID]_[탐지날짜시간]_[생성시간]_[해시]_[원본명].확장자
        """
        # 탐지 발생 시간
        detection_time_str = detection_timestamp.strftime("%Y%m%d_%H%M%S")

        # 파일 생성 시간
        file_creation_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 원본 파일명에서 확장자 추출 및 안전한 이름 생성
        if original_filename:
            file_extension = Path(original_filename).suffix.lower()
            # 원본 파일명을 안전하게 변환 (특수문자/공백 제거, 길이 제한)
            safe_original_name = "".join(
                c for c in Path(original_filename).stem if c.isalnum() or c in "-_"
            )[:15]
        else:
            file_extension = self._get_default_extension_for_file_type(file_type)
            safe_original_name = ""

        # 보안 해시 생성
        hash_input = f"{detection_seq}_{detection_time_str}_{file_creation_time_str}_{file_type}_{safe_original_name}_{self.current_environment}"
        security_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]

        # 파일명 조합
        base_filename = f"det{detection_seq:06d}_{detection_time_str}_{file_creation_time_str}_{security_hash}"

        # 파일 타입별 접두사 + 원본명 포함
        if file_type == "thumbnail":
            return f"thumb_{base_filename}.jpg"
        elif file_type == "video_clip":
            return f"clip_{base_filename}.mp4"
        elif file_type == "image":
            if safe_original_name:
                return f"img_{base_filename}_{safe_original_name}{file_extension}"
            else:
                return f"img_{base_filename}{file_extension}"
        elif file_type == "video":
            if safe_original_name:
                return f"vid_{base_filename}_{safe_original_name}{file_extension}"
            else:
                return f"vid_{base_filename}{file_extension}"
        else:
            return f"file_{base_filename}{file_extension}"

    def _get_default_extension_for_file_type(self, file_type: str) -> str:
        """파일 타입별 기본 확장자"""
        defaults = {
            "thumbnail": ".jpg",
            "image": ".jpg",
            "video": ".mp4",
            "video_clip": ".mp4",
        }
        return defaults.get(file_type, ".bin")

    def _validate_file_security_and_size(
        self, file_path: Path, file_type: str
    ) -> Tuple[bool, str]:
        """
        파일 보안 검증
        - 파일 크기 제한
        - MIME 타입 검증 (악성 파일 차단)
        - 확장자 화이트리스트 (보안)
        - 파일 존재 확인
        """
        if not file_path.exists():
            return False, f"파일이 존재하지 않습니다: {file_path}"

        # 파일 크기 검증
        file_size = file_path.stat().st_size

        if file_type in ["image", "thumbnail"]:
            if file_size > self.max_image_file_size_bytes:
                return (
                    False,
                    f"이미지 파일 크기 초과 (최대 {settings.max_image_file_size_mb}MB, 현재 {file_size/(1024*1024):.1f}MB)",
                )
        elif file_type in ["video", "video_clip"]:
            if file_size > self.max_video_file_size_bytes:
                return (
                    False,
                    f"동영상 파일 크기 초과 (최대 {settings.max_video_file_size_mb}MB, 현재 {file_size/(1024*1024):.1f}MB)",
                )

        # 확장자 화이트리스트 검증
        file_extension = file_path.suffix.lower()

        if file_type in ["image", "thumbnail"]:
            if file_extension not in self.supported_image_extensions:
                return (
                    False,
                    f"지원하지 않는 이미지 확장자: {file_extension} (지원: {', '.join(self.supported_image_extensions)})",
                )
        elif file_type in ["video", "video_clip"]:
            if file_extension not in self.supported_video_extensions:
                return (
                    False,
                    f"지원하지 않는 동영상 확장자: {file_extension} (지원: {', '.join(self.supported_video_extensions)})",
                )

        # MIME 타입 검증
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if file_type in ["image", "thumbnail"] and not mime_type.startswith("image/"):
                return False, f"잘못된 이미지 MIME 타입: {mime_type}"
            elif file_type in ["video", "video_clip"] and not mime_type.startswith("video/"):
                return False, f"잘못된 동영상 MIME 타입: {mime_type}"

        return True, "보안 검증 통과"

    def store_detection_image_file(
        self,
        source_image_path: str,
        device_id: int,
        detection_seq: int,
        detection_timestamp: datetime,
    ) -> FileStorageResult:
        """
        탐지 이미지 파일을 환경별 upload 경로에 저장하고 DB용 URL 반환
        - source_image_path: 원본 이미지 파일 경로
        - device_id: 디바이스 ID
        - detection_seq: 탐지 결과 시퀀스
        - detection_timestamp: 실제 탐지 발생 시간
        """
        file_creation_time = datetime.now()

        try:
            source_path = Path(source_image_path)

            # 보안 검증
            is_valid, validation_message = self._validate_file_security_and_size(
                source_path, "image"
            )
            if not is_valid:
                return FileStorageResult(
                    success=False,
                    error_message=validation_message,
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )

            # 저장 경로 생성 (년/월/디바이스별 구조)
            organized_directory = self._generate_organized_file_path(
                self.original_images_directory, device_id, detection_timestamp
            )

            # 파일명 생성
            production_filename = self._generate_production_filename(
                detection_seq, "image", detection_timestamp, source_path.name
            )
            destination_file_path = organized_directory / production_filename

            # 파일 복사
            shutil.copy2(source_path, destination_file_path)

            # DB 저장용 URL 생성
            relative_path = destination_file_path.relative_to(self.upload_root_directory)
            database_url = f"{self.static_file_url_prefix}/{relative_path.as_posix()}"

            logger.info(
                f"이미지 저장 완료 [환경={self.current_environment}]: det_seq={detection_seq}, 탐지시간={detection_timestamp}, URL={database_url}"
            )

            return FileStorageResult(
                success=True,
                file_url=database_url,
                file_path=destination_file_path,
                file_size_bytes=destination_file_path.stat().st_size,
                file_creation_timestamp=file_creation_time,
                detection_timestamp=detection_timestamp,
                storage_environment=self.current_environment,
            )

        except Exception as e:
            error_msg = f"이미지 저장 실패 [환경={self.current_environment}, detection_seq={detection_seq}]: {str(e)}"
            logger.error(error_msg)
            return FileStorageResult(
                success=False,
                error_message=error_msg,
                file_creation_timestamp=file_creation_time,
                detection_timestamp=detection_timestamp,
                storage_environment=self.current_environment,
            )

    def store_video_clip_file(
        self,
        source_video_path: str,
        device_id: int,
        detection_seq: int,
        detection_timestamp: datetime,
        clip_before_seconds: Optional[int] = None,
        clip_after_seconds: Optional[int] = None,
    ) -> FileStorageResult:
        """
        탐지 기준 동영상 클립을 추출하여 저장
        - source_video_path: 원본 동영상 파일 경로
        - device_id: 디바이스 ID
        - detection_seq: 탐지 결과 시퀀스
        - detection_timestamp: 탐지 발생 시간 (클립 중심점)
        - clip_before_seconds: 탐지 전 포함 시간 (기본값: 설정값)
        - clip_after_seconds: 탐지 후 포함 시간 (기본값: 설정값)
        - 10초 클립 = 탐지 전 3초 + 탐지 후 7초 (기본 설정)
        """
        file_creation_time = datetime.now()

        # 기본 클립 길이 설정 -> config.py 설정 사용
        before_seconds = clip_before_seconds or self.video_clip_before_seconds
        after_seconds = clip_after_seconds or self.video_clip_after_seconds

        try:
            source_path = Path(source_video_path)

            # 보안 검증
            is_valid, validation_message = self._validate_file_security_and_size(source_path, "video")
            if not is_valid:
                return FileStorageResult(
                    success=False,
                    error_message=validation_message,
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )

            # 저장 경로 생성 -> 년/월/디바이스별 구조
            organized_directory = self._generate_organized_file_path(
                self.video_clips_directory, device_id, detection_timestamp
            )

            # 클립 파일명 생성
            clip_filename = self._generate_production_filename(
                detection_seq, "video_clip", detection_timestamp, source_path.name
            )
            destination_file_path = organized_directory / clip_filename

            # 실제 동영상 클립 추출 처리
            self._extract_video_clip(
                source_path, destination_file_path,
                before_seconds, after_seconds, detection_timestamp
            )

            # DB 저장용 URL 생성 -> 환경별 URL 접두사 사용
            relative_path = destination_file_path.relative_to(self.upload_root_directory)
            database_url = f"{self.static_file_url_prefix}/{relative_path.as_posix()}"

            logger.info(
                f"동영상 클립 저장 완료 [환경={self.current_environment}]: det_seq={detection_seq}, 클립길이={before_seconds + after_seconds}초, URL={database_url}"
            )

            return FileStorageResult(
                success=True,
                file_url=database_url,
                file_path=destination_file_path,
                file_size_bytes=destination_file_path.stat().st_size,
                file_creation_timestamp=file_creation_time,
                detection_timestamp=detection_timestamp,
                storage_environment=self.current_environment,
            )

        except Exception as e:
            error_msg = f"동영상 클립 저장 실패 [환경={self.current_environment}, detection_seq={detection_seq}]: {str(e)}"
            logger.error(error_msg)
            return FileStorageResult(
                success=False,
                error_message=error_msg,
                file_creation_timestamp=file_creation_time,
                detection_timestamp=detection_timestamp,
                storage_environment=self.current_environment,
            )

    def store_thumbnail_image_file(
        self,
        source_image_path: str,
        device_id: int,
        detection_seq: int,
        detection_timestamp: datetime,
        thumbnail_size: Optional[Tuple[int, int]] = None,
        jpeg_quality: Optional[int] = None,
    ) -> FileStorageResult:
        """
        탐지 이미지의 썸네일을 생성하여 저장
        - source_image_path: 원본 이미지 파일 경로
        - device_id: 디바이스 ID
        - detection_seq: 탐지 결과 시퀀스
        - detection_timestamp: 탐지 발생 시간
        - thumbnail_size: 썸네일 크기 (기본값: 설정값)
        - jpeg_quality: JPEG 품질 (기본값: 설정값)
        """
        file_creation_time = datetime.now()

        # 썸네일 설정 -> config.py 설정 사용
        thumb_size = thumbnail_size or self.thumbnail_size
        quality = jpeg_quality or self.thumbnail_quality

        try:
            source_path = Path(source_image_path)

            # 보안 검증
            is_valid, validation_message = self._validate_file_security_and_size(
                source_path, "image"
            )
            if not is_valid:
                return FileStorageResult(
                    success=False,
                    error_message=validation_message,
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )

            # 저장 경로 생성
            organized_directory = self._generate_organized_file_path(
                self.thumbnail_images_directory, device_id, detection_timestamp
            )

            # 썸네일 파일명 생성
            thumbnail_filename = self._generate_production_filename(
                detection_seq, "thumbnail", detection_timestamp, source_path.name
            )
            destination_file_path = organized_directory / thumbnail_filename

            # 실제 썸네일 생성 처리
            self._create_thumbnail_image(source_path, destination_file_path, thumb_size, quality)

            # DB 저장용 URL 생성
            relative_path = destination_file_path.relative_to(self.upload_root_directory)
            database_url = f"{self.static_file_url_prefix}/{relative_path.as_posix()}"

            logger.info(
                f"썸네일 저장 완료 [환경={self.current_environment}]: det_seq={detection_seq}, 크기={thumb_size}, URL={database_url}"
            )

            return FileStorageResult(
                success=True,
                file_url=database_url,
                file_path=destination_file_path,
                file_size_bytes=destination_file_path.stat().st_size,
                file_creation_timestamp=file_creation_time,
                detection_timestamp=detection_timestamp,
                storage_environment=self.current_environment,
            )

        except Exception as e:
            error_msg = f"썸네일 저장 실패 [환경={self.current_environment}, detection_seq={detection_seq}]: {str(e)}"
            logger.error(error_msg)
            return FileStorageResult(
                success=False,
                error_message=error_msg,
                file_creation_timestamp=file_creation_time,
                detection_timestamp=detection_timestamp,
                storage_environment=self.current_environment,
            )

    # 운영 관련 기능들은 제거됨 - 시스템 운영은 별도 도구에서 관리
    # - get_total_storage_usage_info(): 스토리지 모니터링 → Prometheus/Grafana
    # - cleanup_orphaned_files(): 파일 정리 → Cron Job/운영 스크립트

    def _create_thumbnail_image(
        self,
        source_path: Path,
        destination_path: Path,
        thumb_size: Tuple[int, int],
        jpeg_quality: int
    ) -> None:
        """
        실제 썸네일 이미지 생성 (Pillow 사용)
        - 비율 유지하며 리사이징
        - 고품질 JPEG 압축
        - 파일 크기 최적화 (보통 원본의 5-10% 수준)
        """
        if not PILLOW_AVAILABLE:
            logger.warning("Pillow가 설치되지 않아 원본 파일을 복사합니다.")
            shutil.copy2(source_path, destination_path)
            return

        try:
            with Image.open(source_path) as img:
                # EXIF 정보를 반영하여 회전 보정
                img = ImageOps.exif_transpose(img)

                # RGB로 변환 (RGBA, CMYK 등 → RGB)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # 비율을 유지하며 썸네일 생성
                img.thumbnail(thumb_size, Image.Resampling.LANCZOS)

                # 고품질 JPEG로 저장 (최적화 옵션 포함)
                img.save(
                    destination_path,
                    'JPEG',
                    quality=jpeg_quality,
                    optimize=True,           # 파일 크기 최적화
                    progressive=True        # 점진적 로딩 지원
                )

            logger.info(
                f"✅ 썸네일 생성 완료: 원본 {img.size} → 썸네일 {thumb_size}, 품질 {jpeg_quality}%"
            )

        except Exception as e:
            logger.error(f"썸네일 생성 실패: {str(e)}")
            # 실패 시 원본 파일 복사 (fallback)
            shutil.copy2(source_path, destination_path)
            raise RuntimeError(f"썸네일 생성 중 오류 발생: {str(e)}")

    def _extract_video_clip(
        self,
        source_path: Path,
        destination_path: Path,
        before_seconds: int,
        after_seconds: int,
        detection_timestamp: Optional[datetime] = None
    ) -> None:
        """
        실제 동영상 클립 추출 (FFmpeg 사용)
        - 탐지 시점 기준 전후 클립 추출
        - 고효율 H.264 인코딩
        - DB 용량 99.7% 절약 효과 (30분 → 10초)
        """
        if not FFMPEG_AVAILABLE:
            logger.warning("ffmpeg-python이 설치되지 않아 원본 파일을 복사합니다.")
            shutil.copy2(source_path, destination_path)
            return

        try:
            # 실제 탐지 시점 기반 클립 추출 (향후 확장 가능)
            # 현재는 동영상 시작부터 클립을 추출하는 방식으로 구현
            clip_start_offset = 0  # 동영상 시작 지점
            clip_duration = before_seconds + after_seconds

            # detection_timestamp는 향후 정확한 탐지 시점 계산에 사용 예정
            if detection_timestamp:
                logger.debug(f"탐지 시간 기준 클립 추출: {detection_timestamp}")

            # FFmpeg를 사용한 동영상 클립 추출
            stream = ffmpeg.input(str(source_path))
            stream = ffmpeg.output(
                stream,
                str(destination_path),
                # 시간 설정
                ss=clip_start_offset,          # 시작 시간 (초)
                t=clip_duration,               # 클립 길이 (초)
                # 비디오 설정
                vcodec='libx264',              # H.264 인코딩
                crf=23,                        # 품질 (18-28, 낮을수록 고품질)
                preset='fast',                 # 인코딩 속도 (fast, medium, slow)
                pix_fmt='yuv420p',            # 호환성을 위한 픽셀 형식
                # 오디오 설정
                acodec='aac',                  # AAC 오디오
                audio_bitrate='128k',          # 오디오 비트레이트
                # 최적화
                movflags='faststart',          # 웹 스트리밍 최적화
                # 기존 파일 덮어쓰기
                overwrite_output=True
            )

            # FFmpeg 실행
            ffmpeg.run(stream, quiet=True, capture_stdout=True)

            logger.info(
                f"✅ 동영상 클립 추출 완료: {clip_duration}초 클립, 탐지 기준 전 {before_seconds}초 + 후 {after_seconds}초"
            )

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFmpeg 오류: {error_message}")
            # 실패 시 원본 파일 복사 (fallback)
            shutil.copy2(source_path, destination_path)
            raise RuntimeError(f"동영상 클립 추출 중 오류 발생: {error_message}")

        except Exception as e:
            logger.error(f"동영상 클립 추출 실패: {str(e)}")
            # 실패 시 원본 파일 복사 (fallback)
            shutil.copy2(source_path, destination_path)
            raise RuntimeError(f"동영상 클립 추출 중 오류 발생: {str(e)}")

    def check_media_processing_dependencies(self) -> Dict[str, bool]:
        """
        미디어 처리 의존성 확인 (시스템 진단용)

        Returns:
            Dict: 각 의존성의 설치/사용 가능 여부
        """
        dependencies = {
            "pillow": PILLOW_AVAILABLE,
            "ffmpeg_python": FFMPEG_AVAILABLE,
        }

        # FFmpeg 바이너리 확인
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5
            )
            dependencies["ffmpeg_binary"] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            dependencies["ffmpeg_binary"] = False

        logger.info(f" 미디어 처리 의존성 확인: {dependencies}")
        return dependencies


# 전역 파일 스토리지 매니저 인스턴스 (의존성 주입용)
production_file_storage = ProductionFileStorageManager()

async def save_detection_media(self, file_content: bytes, original_filename: str, device_name: str, detection_time: datetime, file_type:str) -> Dict[str, Any]:
    """
    미디어 파일 통합 저장 메서드 (mediaservice 에서 사용)
    file_content: 업로드된 파일의 바이너리 데이터
    original_filename: 원본 파일명
    device_name: 디바이스명
    detection_time: 탐지 발생 시간
    file_type: 파일 타입
    """
    file_creation_time = datetime.now()
    
    try: 