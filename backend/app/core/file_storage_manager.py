"""파일 스토리지 매니저
- 파일 물리적 저장 관리
- DB URL 생성 및 관리
- media 모듈 통합 (이미지/동영상 처리, 파일 검증)
"""
import os
import hashlib
import logging
import re
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

# Media 모듈 import
from app.core.media import ImageProcessor, VideoProcessor, FileValidator
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class FileStorageResult:
    """파일 저장 결과 데이터"""
    success: bool
    file_url: Optional[str] = None  # DB 저장용 URL
    file_path: Optional[Path] = None  # 실제 파일 경로
    file_size_bytes: Optional[int] = None  # 파일 크기 (바이트)
    error_message: Optional[str] = None  # 오류 메시지
    file_creation_timestamp: Optional[datetime] = None  # 파일 생성 시간
    detection_timestamp: Optional[datetime] = None  # 탐지 시간
    storage_environment: Optional[str] = None  # 저장 환경
    
class FileStorageManager:
    """파일 저장소 매니저
    - 환경별 경로 자동 관리
    - 파일 저장 및 URL 생성
    - 미디어 처리 통합
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

        # Media 프로세서 인스턴스
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.file_validator = FileValidator()

        # 시작 시 디렉토리 생성
        self._ensure_directories_exist()

        logger.info(
            f"파일 저장소 초기화 완료 [환경={self.current_environment}, 경로={self.upload_root_directory}]"
        )

    def _ensure_directories_exist(self) -> None:
        """업로드 디렉토리 생성"""
        required_directories = [
            self.original_images_directory,
            self.thumbnail_images_directory,
            self.original_videos_directory,
            self.video_clips_directory,
        ]

        for directory_path in required_directories:
            try:
                directory_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"디렉토리 확인: {directory_path}")
            except Exception as e:
                logger.error(f"디렉토리 생성 실패 {directory_path}: {str(e)}")
                raise RuntimeError(f"필수 디렉토리 생성 실패: {directory_path}")

    def _generate_file_path(
        self, base_directory: Path, device_id: int, detection_timestamp: datetime
    ) -> Path:
        """파일 저장 경로 생성"""
        year_month_path = f"{detection_timestamp.year:04d}/{detection_timestamp.month:02d}"
        device_directory_name = f"device_{device_id:03d}"

        organized_directory = base_directory / year_month_path / device_directory_name
        organized_directory.mkdir(parents=True, exist_ok=True)

        return organized_directory

    def _generate_filename(
        self,
        detection_seq: int,
        file_type: str,
        detection_timestamp: datetime,
        original_filename: str = None,
    ) -> str:
        """파일명 생성"""
        # 탐지 시간
        detection_time_str = detection_timestamp.strftime("%Y%m%d_%H%M%S")

        # 파일 생성 시간
        file_creation_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 원본 파일명 처리
        if original_filename:
            file_extension = Path(original_filename).suffix.lower()
            safe_original_name = "".join(
                c for c in Path(original_filename).stem if c.isalnum() or c in "-_"
            )[:15]
        else:
            file_extension = self._get_default_extension(file_type)
            safe_original_name = ""

        # 보안 해시
        hash_input = f"{detection_seq}_{detection_time_str}_{file_creation_time_str}_{file_type}_{safe_original_name}_{self.current_environment}"
        security_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]

        # 파일명 조합
        base_filename = f"det{detection_seq:06d}_{detection_time_str}_{file_creation_time_str}_{security_hash}"

        # 타입별 접두사
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

    def _get_default_extension(self, file_type: str) -> str:
        """파일 타입별 기본 확장자"""
        defaults = {
            "thumbnail": ".jpg",
            "image": ".jpg",
            "video": ".mp4",
            "video_clip": ".mp4",
        }
        return defaults.get(file_type, ".bin")

    def _validate_file(self, file_path: Path, file_type: str) -> Tuple[bool, str]:
        """파일 보안 검증 (FileValidator 사용)"""
        # FileValidator 종합 검증
        expected_type = 'image' if file_type in ['image', 'thumbnail'] else 'video'
        validation_result = self.file_validator.validate_file_comprehensive(
            file_path, expected_type=expected_type
        )

        if not validation_result['valid']:
            return False, validation_result['message']

        # 파일 크기 추가 검증
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

        return True, "검증 통과"

    def store_image(
        self,
        source_image_path: str,
        device_id: int,
        detection_seq: int,
        detection_timestamp: datetime,
    ) -> FileStorageResult:
        """이미지 파일 저장"""
        file_creation_time = datetime.now()

        try:
            source_path = Path(source_image_path)

            # 파일 검증
            is_valid, validation_message = self._validate_file(source_path, "image")
            if not is_valid:
                return FileStorageResult(
                    success=False,
                    error_message=validation_message,
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )

            # 저장 경로 생성
            organized_directory = self._generate_file_path(
                self.original_images_directory, device_id, detection_timestamp
            )

            # 파일명 생성
            filename = self._generate_filename(
                detection_seq, "image", detection_timestamp, source_path.name
            )
            destination_file_path = organized_directory / filename

            # 파일 복사
            shutil.copy2(source_path, destination_file_path)

            # DB 저장용 URL 생성
            relative_path = destination_file_path.relative_to(self.upload_root_directory)
            database_url = f"{self.static_file_url_prefix}/{relative_path.as_posix()}"

            logger.info(
                f"이미지 저장 완료 [환경={self.current_environment}]: det_seq={detection_seq}, URL={database_url}"
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
            
    def store_video_clip(
        self,
        source_video_path: str,
        device_id: int,
        detection_seq: int,
        detection_timestamp: datetime,
        clip_before_seconds: Optional[int] = None,
        clip_after_seconds: Optional[int] = None,
    ) -> FileStorageResult:
        """동영상 클립 저장 (VideoProcessor 사용)"""
        file_creation_time = datetime.now()
        
        # 기본 클립 길이 설정
        before_seconds = clip_before_seconds or self.video_clip_before_seconds
        after_seconds = clip_after_seconds or self.video_clip_after_seconds
        
        try:
            source_path = Path(source_video_path)
            
            # 파일 검증
            is_valid, validation_message = self._validate_file(source_path, "video")
            if not is_valid:
                return FileStorageResult(
                    success=False,
                    error_message=validation_message,
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )
                
            # 저장 경로 생성
            organized_directory = self._generate_file_path(
                self.video_clips_directory, device_id, detection_timestamp
            )
            
            # 클립 파일명 생성
            clip_filename = self._generate_filename(detection_seq, "video_clip", detection_timestamp, source_path.name)
            destination_file_path = organized_directory / clip_filename
            
            # VideoProcessor 사용해 클립 생성
            clip_result = self.video_processor.extract_detection_clip(
                source_path=source_path,
                destination_path=destination_file_path,
                detection_timestamp=detection_timestamp,
                before_seconds=before_seconds,
                after_seconds=after_seconds,
                quality_preset='fast'
            )
            
            if not clip_result.get('success'):
                return FileStorageResult(
                    success=False,
                    error_message=f"동영상 클립 추출 실패: {clip_result.get('error')}",
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )
            
            # DB 저장용 URL 생성
            relative_path = destination_file_path.relative_to(self.upload_root_directory)
            database_url = f"{self.static_file_url_prefix}/{relative_path.as_posix()}"
            
            logger.info(f"동영상 클립 완료 [환경={self.current_environment}]: det_seq={detection_seq}, URL={database_url}")
            
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
            
    def store_thumbnail(
        self,
        source_image_path: str,
        device_id: int,
        detection_seq: int,
        detection_timestamp: datetime,
        thumbnail_size: Optional[Tuple[int, int]] = None,
        jpeg_quality: Optional[int] = None,
    ) -> FileStorageResult:
        """썸네일 이미지 저장 (ImageProcessor 사용)"""
        file_creation_time = datetime.now()
        
        # 썸네일 설정
        thumb_size = thumbnail_size or self.thumbnail_size
        quality = jpeg_quality or self.thumbnail_quality
        
        try:
            source_path = Path(source_image_path)
            
            # 파일 검증
            is_valid, validation_message = self._validate_file(source_path, "image")
            if not is_valid:
                return FileStorageResult(
                    success=False,
                    error_message=validation_message,
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )
                
            # 저장 경로 생성
            organized_directory = self._generate_file_path(
                self.thumbnail_images_directory, device_id, detection_timestamp
            )
            
            # 썸네일 파일명 생성
            thumbnail_filename = self._generate_filename(detection_seq, "thumbnail", detection_timestamp, source_path.name)
            destination_file_path = organized_directory / thumbnail_filename
            
            # ImageProcessor 사용해 썸네일 생성
            thumbnail_result = self.image_processor.create_thumbnail(
                source_path=source_path,
                destination_path=destination_file_path,
                size=thumb_size,
                quality=quality,
                maintain_aspect_ratio=True
            )
            
            if not thumbnail_result.get('success'):
                return FileStorageResult(
                    success=False,
                    error_message=f"썸네일 생성 실패: {thumbnail_result.get('error')}",
                    file_creation_timestamp=file_creation_time,
                    detection_timestamp=detection_timestamp,
                    storage_environment=self.current_environment,
                )
                
            # DB 저장용 url 생성
            relative_path = destination_file_path.relative_to(self.upload_root_directory)
            database_url = f"{self.static_file_url_prefix}/{relative_path.as_posix()}"
            
            logger.info(f"썸네일 저장 완료 [환경={self.current_environment}]: det_seq={detection_seq}, URL={database_url}")
            
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
            
    async def save_detection_media(
        self,
        file_content: bytes,
        original_filename: str,
        device_name: str,
        detection_time: datetime,
        file_type: str
    ) -> Dict[str, Any]:
        """미디어 파일 통합 저장"""
        start_time = datetime.now()
        
        try:
            logger.info(f"미디어 파일 저장 시작: {original_filename} (타입: {file_type})")
            
            # 임시 파일 생성
            temp_dir = Path("/tmp/smartoko_upload")
            temp_dir.mkdir(exist_ok=True)
            
            safe_filename = "".join(c for c in original_filename if c.isalnum() or c in ".-_")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            temp_file_path = temp_dir / f"temp_{timestamp}_{safe_filename}"
            
            with open(temp_file_path, "wb") as f:
                f.write(file_content)
                
            logger.debug(f"임시 파일 생성: {temp_file_path}")
            
            # device_id 추출
            device_id = self._extract_device_id(device_name)
            
            # detection_seq 생성
            detection_seq = int(datetime.now().timestamp() * 1000000) % 999999
            
            # 파일 타입별 처리
            result_urls = {}
            processing_errors = []
            
            if file_type.lower() in ["image", "jpg", "jpeg", "png", "bmp", "webp", "tiff"]:
                # 원본 이미지 저장
                image_result = self.store_image(str(temp_file_path), device_id, detection_seq, detection_time)
                
                if image_result.success:
                    result_urls["image_url"] = image_result.file_url
                    logger.info(f"원본 이미지 저장 성공: {image_result.file_url}")
                    
                    # 썸네일 자동 생성
                    thumbnail_result = self.store_thumbnail(str(temp_file_path), device_id, detection_seq, detection_time)
                    
                    if thumbnail_result.success:
                        result_urls["thumbnail_url"] = thumbnail_result.file_url
                        logger.info(f"썸네일 생성 성공: {thumbnail_result.file_url}")
                    else:
                        processing_errors.append(f"썸네일 생성 실패: {thumbnail_result.error_message}")
                        
                else:
                    error_msg = f"이미지 저장 실패: {image_result.error_message}"
                    logger.error(error_msg)
                    return self._create_error_response(error_msg, file_type, original_filename, start_time)
                
            elif file_type.lower() in ["video", "mp4", "mov", "avi", "mkv", "webm", "video_clip"]:
                # 동영상 클립 저장
                video_result = self.store_video_clip( str(temp_file_path), device_id, detection_seq, detection_time)
                
                if video_result.success:
                    result_urls["video_url"] = video_result.file_url
                    logger.info(f"동영상 클립 저장 성공: {video_result.file_url}")
                else:
                    error_msg = f"동영상 저장 실패: {video_result.error_message}"
                    logger.error(error_msg)
                    return self._create_error_response(error_msg, file_type, original_filename, start_time)
            else:
                error_msg = f"지원하지 않는 파일 타입: {file_type}"
                logger.error(error_msg)
                return self._create_error_response(error_msg, file_type, original_filename, start_time)
            
            # 임시 파일 정리
            try:
                temp_file_path.unlink()
                logger.debug(f"임시 파일 삭제: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"임시 파일 삭제 실패: {cleanup_error}")
                
            # 성공 응답
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            success_response = {
                "success": True,
                "detection_id": detection_seq,
                "device_id": device_id,
                "device_name": device_name,
                "file_type": file_type,
                "original_filename": original_filename,
                "processing_time_ms": round(processing_time, 2),
                "generated_files": len(result_urls),
                "storage_environment": self.current_environment,
                **result_urls
            }
            
            if processing_errors:
                success_response["warnings"] = processing_errors

            logger.info(
                f"미디어 저장 완료 [device_id={device_id}, file_type={file_type}]: 생성된 파일 {len(result_urls)}개"
            )

            return success_response

        except Exception as e:
            try:
                if 'temp_file_path' in locals() and temp_file_path.exists():
                    temp_file_path.unlink()
            except Exception:
                pass

            error_msg = f"미디어 파일 저장 중 예외 발생: {str(e)}"
            logger.error(error_msg, exc_info=True)

            return self._create_error_response(error_msg, file_type, original_filename, start_time)
        
    def _extract_device_id(self, device_name: str) -> int:
        """디바이스명에서 ID 추출"""
        try:
            numbers = re.findall(r'\d+', device_name)
            
            if numbers:
                device_id = int(numbers[0])
                if 1 <= device_id <= 9999:
                    return device_id
                
            return 1
        
        except Exception:
            return 1
        
    def _create_error_response(
        self,
        error_message: str,
        file_type: str,
        original_filename: str,
        start_time: datetime,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """에러 응답 생성"""
        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        error_response = {
            "success": False,
            "error": error_message,
            "file_type": file_type,
            "original_filename": original_filename,
            "processing_time_ms": round(processing_time, 2),
            "storage_environment": self.current_environment,
            "timestamp": datetime.now().isoformat()
        }
        
        if extra_data:
            error_response.update(extra_data)
            
        return error_response
    
    def check_dependencies(self) -> Dict[str, bool]:
        """미디어 처리 의존성 확인"""
        dependencies = {
            "image_processor": True,
            "video_processor": True,
            "file_validator": True,
        }
        
        # FFmpeg 확인
        ffmpeg_status = self.video_processor.check_ffmpeg_availability()
        dependencies["ffmpeg_available"] = ffmpeg_status.get('available', False)
        if ffmpeg_status.get('available'):
            dependencies["ffmpeg_version"] = ffmpeg_status.get('version', 'unknown')

        logger.info(f"미디어 처리 의존성: {dependencies}")
        return dependencies


# 전역 인스턴스 (싱글톤 패턴)
file_storage = FileStorageManager()

                