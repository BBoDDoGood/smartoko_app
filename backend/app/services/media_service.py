import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from app.repositories.media_repository import MediaRepository
from app.repositories.user_repository import UserRepository
from app.core.file_storage_manager import ProductionFileStorageManager
from app.schemas.media_schemas import (MediaListQuery, MediaListResult, DetectionMedia, UploadRequest, UploadResponse,
                                       DeleteRequest, DeleteResult, MediaStats, ErrorResponse)
from app.core.config import settings


class MediaService:
    """미디어 비즈니스 로직 서비스
    - 파일 업로드 및 미디어 처리 (이미지, 썸네일, 비디오 클립)
    - 권한 기반 미디어 관리(사용자 권한 체크)
    - 환경별 파일 저장소 관리 -> 개발, 스테이징, 프로덕션
    - 미디어 삭제
    - 미디어 통계 및 대시보드 데이터
    """

    def __init__(self, media_repo: MediaRepository, user_repo: UserRepository):
        self.media_repo = media_repo
        self.user_repo = user_repo
        self.file_manager = ProductionFileStorageManager()
        self.logger = logging.getLogger(__name__)

        self._setup_audit_logging()

    def _setup_audit_logging(self):
        """환경별 감사 로그 디렉토리 설정"""
        try:
            if settings.environment == 'development':
                self.audit_log_dir = Path(
                    __file__).parent.parent.parent / 'logs' / 'audit'
            elif settings.environment == 'staging':
                self.audit_log_dir = Path("/var/log/smartoko-staging/audit")
            else:
                self.audit_log_dir = Path("/var/log/smartoko/audit")

            # 디렉토리 생성
            self.audit_log_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"감사 로그 디렉토리 설정: {self.audit_log_dir}")
        except Exception as e:
            self.logger.error(f"감사 로그 디렉토리 설정 실패: {str(e)}")
            # 폴백
            self.audit_log_dir = Path("/tmp/smartoko-audit")
            self.audit_log_dir.mkdir(parents=True, exist_ok=True)

    async def upload_media_file(self, user_id: int, upload_request: UploadRequest, file_content: bytes, filename: str) -> UploadResponse:
        """미디어 파일 업로드 및 처리"""
        start_time = datetime.now()

        try:
            # 사용자 권한 체크
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                self.logger.warning(f"미디어 업로드 실패 - 사용자 없음: {user_id}")
                return UploadResponse(success=False, message="Insufficient permissions for file upload", error_code="INSUFFICIENT_PERMISSIONS")

            # 파일 검증 및 저장
            self.logger.info(
                f"미디어 업로드 시작 [user_id: {user_id}, filename: {filename}]")

            # 파일 스토리지 매니저를 통한 파일 처리
            storage_result = await self.file_manager.save_detection_media(
                file_content=file_content,
                original_filename=filename,
                device_name=upload_request.device_name,
                detection_time=upload_request.detection_time,
                file_type=upload_request.file_type
            )

            if not storage_result["success"]:
                self.logger.error(f"파일 저장 실패: {storage_result['error']}")
                return UploadResponse(
                    success=False,
                    message="File storage error occurred",
                    error_code="FILE_STORAGE_ERROR",
                    error_details=storage_result
                )
            # 데이터베이스 업데이트
            if upload_request.detection_id:
                # 기존 탐지 결과 업데이트
                update_success = await self.media_repo.update_detection_media_urls(
                    detection_id=upload_request.detection_id,
                    image_url=storage_result.get("image_url"),
                    thumbnail_url=storage_result.get("thumbnail_url"),
                    video_url=storage_result.get("video_url")
                )

                if not update_success:
                    self.logger.error(
                        f"DB업데이트 실패 [detection_id={upload_request.detection_id}]")
                    return UploadResponse(
                        success=False, message="Database update failed", error_code="DATABASE_UPDATE_ERROR")

            # 성공 응답 생성
            detection_media = await self.media_repo.get_detection_media_by_id(
                detection_id=upload_request.detection_id or storage_result["detection_id"]
            )

            processing_time = (
                datetime.now() - start_time).total_seconds() * 1000

            # 감사 로그 기록
            await self._log_media_action(
                user_id=user_id,
                action="upload",
                target_id=upload_request.detection_id,
                details={
                    "filename": filename,
                    "file_type": upload_request.file_type.value,
                    "device_name": upload_request.device_name,
                    "processing_time": processing_time
                }
            )

            self.logger.info(
                f"미디어 업로드 완료 [user_id={user_id}, processing_time={processing_time:.1f}ms]")

            return UploadResponse(
                success=True,
                message="File upload completed successfully",
                detection_media=detection_media,
                processing_time_ms=processing_time
            )
        except Exception as e:
            processing_time = (
                datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"미디어 업로드 오류 [user_id={user_id}: {str(e)}]")

            return UploadResponse(
                success=False,
                message="An error occurred during file upload",
                error_code="INTERNAL_SERVER_ERROR",
                error_details={"error_message": str(e)},
                processing_time=processing_time
            )

    async def get_media_list(self, user_id: int, query: MediaListQuery, lang_tag: str = "en_US") -> MediaListResult:
        """미디어 목록 조회 - 페이징 및 필터링"""
        try:
            # 권한 체크
            permissions = await self.user_repo.get_user_permissions(user_id)
            if "read" not in permissions:
                self.logger.warning(f"미디어 조회 권한 없음 [user_id={user_id}]")
                raise PermissionError(
                    "Insufficient permissions for media access")

            self.logger.info(
                f"미디어 목록 조회 [user_id={user_id}, page={query.page}, size={query.page_size}]")

            # 레파지토리를 통한 데이터 조회
            media_result = await self.media_repo.get_media_list_paginated(query, lang_tag)

            # 감사 로그 기록
            await self._log_media_action(
                user_id=user_id,
                action="list_view",
                details={
                    "page": query.page,
                    "page_size": query.page_size,
                    "filters": {
                        "device_name": query.device_name,
                        "media_type": query.media_type.value if query.media_type else None,
                        "date_range": f"{query.date_from} ~ {query.date_to}" if query.date_from else None
                    },
                    "total_count": media_result["total_count"]
                }
            )

            self.logger.info(
                f"미디어 목록 조회 완료 [user_id={user_id}, count={media_result['total_count']}]")
            return media_result

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"미디어 목록 조회 오류 [user_id={user_id}: {str(e)}]")
            raise

    async def get_media_detail(self, user_id: int, detection_id: int, lang_tag: str = "en_US") -> Optional[Dict[str, Any]]:
        """ 미디어 상세 정보 조회"""
        try:
            # 권한 체크
            permissions = await self.user_repo.get_user_permissions(user_id)
            if "read" not in permissions:
                self.logger.warning(f"미디어 상세 조회 권한 없음 [user_id={user_id}]")
                return None

            self.logger.info(
                f"미디어 상세 조회 [user_id={user_id}, detection_id={detection_id}]")

            media_detail = await self.media_repo.get_detection_media_by_id(detection_id, lang_tag)

            if media_detail:
                # 감사 로그 기록
                await self._log_media_action(
                    user_id=user_id,
                    action="detail_view",
                    target_id=detection_id,
                    details={"detection_id": detection_id}
                )

                self.logger.info(
                    f"미디어 상세 조회 완료 [user_id={user_id}], detection_id={detection_id}")
            else:
                self.logger.warning(
                    f"미디어 상세 정보 없음 [detection_id={detection_id}]")

            return media_detail

        except Exception as e:
            self.logger.error(
                f"미디어 상세 조회 오류 [user_id={user_id}, detection_id={detection_id}: {str(e)}]")
            raise Exception(
                f"An error occurred while retrieving media detail: {str(e)}")

    async def delete_media(self, user_id: int, delete_request: DeleteRequest) -> DeleteResult:
        """ 미디어 삭제 - 권한 체크 및 파일 격리 처리"""
        try:
            # 관리자 권한 체크
            can_delete = await self.user_repo.can_delete_media(user_id)
            if not can_delete:
                self.logger.warning(f"미디어 삭제 권한 없음 [user_id={user_id}]")
                return DeleteResult(success=False, message="Insufficient permissions for media deletion", error_code="INSUFFICIENT_PERMISSIONS")

            detection_id = delete_request.detection_id
            self.logger.info(
                f"미디어 삭제 요청 [user_id={user_id}, detection_id={detection_id}]")

            # 삭제 전 미디어 정보 조회
            media_info = await self.media_repo.get_detection_media_by_id(detection_id)
            if not media_info:
                return DeleteResult(success=False, message="Media not found for deletion", error_code="MEDIA_NOT_FOUND")

            quarantine_result = await self._move_files_to_quarantine(media_info, user_id)

            # 데이터베이스에서 레코드 삭제
            db_delete_success = await self.media_repo.delete_detection_media(detection_id)

            if db_delete_success:
                # 감사 로그 기록
                await self._log_media_action(
                    user_id=user_id,
                    action="delete",
                    target_id=detection_id,
                    details={
                        "detection_id": detection_id,
                        "device_name": media_info.get("device_name"),
                        "quarantine_path": quarantine_result.get("quarantine_path"),
                        "file_moved": quarantine_result.get("file_count", 0)
                    }
                )

                self.logger.info(
                    f"미디어 삭제 완료 [user_id={user_id}, detection_id={detection_id}]")

                return DeleteResult(
                    success=True,
                    message="Media deleted successfully",
                    deleted_detection_id=detection_id,
                    deleted_file_count=quarantine_result.get("file_count", 0)
                )
            else:
                return DeleteResult(
                    success=False,
                    message="Failed to delete media from database",
                    error_code="DATABASE_DELETE_ERROR"
                )

        except Exception as e:
            self.logger.error(
                f"미디어 삭제 오류 [user_id={user_id}, detection_id={delete_request.detection_id}: {str(e)}]")

            return DeleteResult(
                success=False,
                message="An error occurred during media deletion",
                error_code="INTERNAL_SERVER_ERROR",
                error_details={"error_message": str(e)}
            )

    async def get_media_statistics(self, user_id: int, lang_tag: str = "en_US") -> MediaStats:
        """ 미디어 통계 정보 조회"""
        try:
            # 권한 체크
            permissions = await self.user_repo.get_user_permissions(user_id)
            if "read" not in permissions:
                self.logger.warning(f"미디어 통계 조회 권한 없음 [user_id={user_id}]")
                raise PermissionError(
                    "Insufficient permissions for statistics access")

            self.logger.info(f"미디어 통계 조회 [user_id={user_id}]")

            stats = await self.media_repo.get_media_stats(lang_tag)

            await self._log_media_action(
                user_id=user_id,
                action="stats_view",
                details={
                    "total_detection": stats["total_detection"],
                    "total_files": stats["total_files"]
                }
            )

            self.logger.info(
                f"미디어 통계 조회 완료 [user_id={user_id}, total_detection={stats['total_detection']}]")
            return stats

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"미디어 통계 조회 오류 [user_id={user_id}]: {str(e)}")
            raise Exception(
                f"An error occurred while retrieving media statistics: {str(e)}")

    async def get_device_media_history(self, user_id: int, device_name: str,
                                    start_date: datetime, end_date: datetime,
                                    lang_tag: str = "en-US") -> List[Dict[str, Any]]:
        """특정 디바이스의 미디어 이력 조회"""
        try:
            # 권한 체크
            permissions = await self.user_repo.get_user_permissions(user_id)
            if "read" not in permissions:
                self.logger.warning(f"디바이스 이력 조회 권한 없음 [user_id={user_id}]")
                raise PermissionError(
                    "Insufficient permissions for device history access")

            self.logger.info(
                f"디바이스 미디어 이력 조회 [user_id={user_id}, device={device_name}]")

            media_history = await self.media_repo.get_media_by_device_and_date(
                device_name=device_name,
                start_date=start_date,
                end_date=end_date,
                lang_tag=lang_tag
            )

            # 감사 로그 기록
            await self._log_media_action(
                user_id=user_id,
                action="DEVICE_HISTORY_VIEW",
                details={
                    "device_name": device_name,
                    "date_range": f"{start_date.date()} ~ {end_date.date()}",
                    "records_count": len(media_history)
                }
            )

            self.logger.info(
                f"디바이스 미디어 이력 조회 완료 [user_id={user_id}, count={len(media_history)}]")
            return media_history

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(
                f"디바이스 미디어 이력 조회 오류 [user_id={user_id}]: {str(e)}")
            raise Exception(
                f"An error occurred while retrieving device media history: {str(e)}")
            
    # 내부 헬퍼 메서드들
    async def _move_files_to_quarantine(self, media_info: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """ 파일들을 격리 디렉토리로 이동"""
        try:
            quarantine_base = Path(settings.upload_base_directory) / "quarantine" / datetime.now().strftime("%Y%m%d")
            quarantine_base.mkdir(parents=True, exist_ok=True)
            
            moved_files = 0
            file_paths = []
            
            # 각 미디어 파일 처리
            for media_type in ["original_image", "thumbnail","video_clip"]:
                if media_type in media_info and media_info[media_type]["url"]:
                    file_url = media_info[media_type]["url"]
                    if file_url.startswith("/uploads/"):
                        source_path = Path(settings.upload_base_directory) / file_url[9:]   # /uploads/ 제거
                        
                        if source_path.exists():
                            quarantine_path = quarantine_base / f"user_{user_id}" / source_path.name
                            quarantine_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # 파일 이동
                            source_path.rename(quarantine_path)
                            moved_files += 1
                            file_paths.append(str(quarantine_path))
                            
                            self.logger.info(f"파일 격리 디렉토리로 이동: {source_path} -> {quarantine_path}")
                            
            return {
                "success": True,
                "file_count": moved_files,
                "quarantine_path": str(quarantine_base / f"user_{user_id}"),
                "file_paths": file_paths
            }
            
        except Exception as e:
            self.logger.error(f"격리 이동 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_count": 0
            }
            
    async def _log_media_action(self, user_id: int, action: str, target_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """미디어 과련 로그 기록"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "action": action,
                "target_id": target_id,
                "details": details or {},
                "environment": settings.environment
            }
            
            # 일별 로그 파일에 기록
            log_file = self.audit_log_dir / f"media_audit_{datetime.now().strftime('%Y%m%d')}.log"
            
            with open(log_file, "a", encoding="utf-8") as f:
                import json
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        except Exception as e:
            self.logger.error(f"로그 기록 오류: {str(e)}")