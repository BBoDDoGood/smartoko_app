from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
import math

from app.repositories.base_repository import BaseRepository
from app.models.detection_result import DetectionResult
from app.models.device import Device
from app.models.model_product import ModelProduct, ModelProductLang
from app.schemas.media_schemas import (DetectionMedia, MediaFile, MediaType, MediaListQuery, MediaListResult, MediaStats)

class MediaRepository(BaseRepository):
    """미디어 관련 데이터 접근 레이어
    - 3개 미디어 파일 -> 이미지, 썸네일, 동영상
    - 다국어 지원 (기본: 영어 / 지원: 한국어, 중국어, 일본어, 태국어, 필리핀어)
    - 페이징, 필터링, 통계 기능 제공
    """
    async def get_detection_media_by_id(self, detection_id: int, lang_tag: str = "en-US") -> Optional[Dict[str, Any]]:
        """탐지 결과 미디어 정보 조회
        - detection_id: 탐지 결과 id
        - lang_tag: 언어 태그
        """
        try:
            query = (select(DetectionResult, Device.device_label, ModelProductLang.product_name)
                     .join(Device, DetectionResult.device_seq == Device.device_seq)
                     .join(ModelProduct, DetectionResult.model_product_seq == ModelProduct.model_product_seq)
                     .join(ModelProduct, DetectionResult.model_product_seq == ModelProduct.model_product_seq)
                     .join(ModelProductLang, and_(
                         ModelProduct.model_product_seq == ModelProductLang.model_product_seq,
                         ModelProductLang.lang_tag == lang_tag))
                     .where(DetectionResult.detection_seq == detection_id))
            
            result = await self.session.execute(query)
            row = result.first()
            
            if not row:
                return None
            
            detection_result, device_label, product_name = row
            
            return {
                "detection_id": detection_result.detection_seq,
                "detection_time": detection_result.detected_at,
                "device_name": device_label or "Unknown Device",
                "model_name": product_name or "Unknown Model",
                "original_image": {
                    "url": detection_result.image_url,
                    "type": "image",
                    "size_bytes": 0,
                    "created_at": detection_result.reg_dt
                },
                "thumbnail": {
                    "url": detection_result.thumbnail_url,
                    "type": "thumbnail",
                    "size_bytes": 0,
                    "created_at": detection_result.reg_dt
                },
                "video_clip": {
                    "url": detection_result.video_url,
                    "type": "video_clip",
                    "size_bytes": 0,
                    "created_at": detection_result.reg_dt
                }
            }
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"미디어 조회 중 데이터 베이스 오류 발생: {str(e)}")
        except Exception as e:
            raise Exception(f"미디어 조회 중 오류 발생: {str(e)}")
        
    async def get_media_list_paginated(self, query: MediaListQuery, lang_tag: str = "en-US") -> MediaListResult:
        """페이징 처리된 미디어 목록 조회"""
        try:
            base_query = (select(DetectionResult, Device.device_label, ModelProductLang.product_name)
                          .select_from(DetectionResult)
                          .join(Device, DetectionResult.device_seq == Device.device_seq)
                          .join(ModelProduct, DetectionResult.model_product_seq == ModelProduct.model_product_seq)
                          .join(ModelProductLang, and_(
                              ModelProduct.model_product_seq == ModelProductLang.model_product_seq,
                              ModelProductLang.lang_tag == lang_tag)))
            
            # 필터링 조건 추가
            conditions = []
            
            if query.device_name:
                conditions.append(Device.device_label.like(f"%{query.device_name}%"))
                
            if query.media_type:
                if query.media_type == MediaType.IMAGE:
                    conditions.append(DetectionResult.image_url.isnot(None))
                elif query.media_type == MediaType.THUMBNAIL:
                    conditions.append(DetectionResult.thumbnail_url.isnot(None))
                elif query.media_type == MediaType.VIDEO_CLIP:
                    conditions.append(DetectionResult.video_url.isnot(None))
                    
            if query.date_from:
                conditions.append(DetectionResult.detected_at >= query.date_from)
            if query.date_to:
                end_date = query.date_to.replace(hour=23, minute=59, second=59)
                conditions.append(DetectionResult.detected_at <= end_date)
                
            if conditions:
                base_query = base_query.where(and_(*conditions))
                
            # 전체 개수 계산
            count_query = select(func.count()).select_from(base_query.subquery())
            total_count_result = await self.session.execute(count_query)
            total_count = total_count_result.scalar() or 0
            
            # 정렬 적용
            sort_column = DetectionResult.reg_dt
            if query.sort_by == "device_name":
                sort_column = Device.device_label
            elif query.sort_by == "created_at":
                sort_column = DetectionResult.reg_dt
                
            if query.sort_order == "asc":
                base_query = base_query.order_by(asc(sort_column))
            else:
                base_query = base_query.order_by(desc(sort_column))
                
            # 페이징 적용
            offset = (query.page - 1) * query.page_size
            paginated_query = base_query.offset(offset).limit(query.page_size)
            
            result = await self.session.execute(paginated_query)
            rows = result.all()
            
            # 결과 변환
            items = []
            for detection_result, device_label, product_name in rows:
                detection_media = {
                    "detection_id": detection_result.detection_seq,
                    "detection_time": detection_result.detected_at,
                    "device_name": device_label or "Unknown Device",
                    "model_name": product_name or "Unknown Model",
                    "original_image": {
                        "url": detection_result.image_url,
                        "type": "image",
                        "size_bytes": 0,
                        "created_at": detection_result.reg_dt
                    },
                    "thumbnail": {
                        "url": detection_result.thumbnail_url,
                        "type": "thumbnail",
                        "size_bytes": 0,
                        "created_at": detection_result.reg_dt
                    },
                    "video_clip": {
                        "url": detection_result.video_url,
                        "type": "video_clip",
                        "size_bytes": 0,
                        "created_at": detection_result.reg_dt
                    }
                }
                items.append(detection_media)
                
            # 페이징 메타 데이터 계산
            total_pages = math.ceil(total_count / query.page_size) if total_count > 0 else 1
            has_next = query.page < total_pages
            has_previous = query.page > 1
            
            return {
                "total_count": total_count,
                "page": query.page,
                "page_size": query.page_size,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous,
                "items": items
            }
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"미디어 목록 조회 중 데이터 베이스 오류 발생: {str(e)}")
        except Exception as e:
            raise Exception(f"미디어 목록 조회 중 오류 발생: {str(e)}")
        
    async def get_media_stats(self, lang_tag: str = "en-US") -> Dict[str, Any]:
        """미디어 통계 정보 조회
        - 전체 탐지 수, 파일 수, 디바이스별 통계
        """
        try:
            # 전체 탐지 수
            total_detections_query = select(func.count(DetectionResult.detection_seq))
            total_detections_result = await self.session.execute(total_detections_query)
            total_detections = total_detections_result.scalar() or 0
            
            # 각 탐지마다 3개 파일 -> 이미지, 썸네일, 동영상
            total_files = total_detections * 3
            
            # 타입별 개수
            image_count_query = select(func.count()).where(DetectionResult.image_url.isnot(None))
            thumbnail_count_query = select(func.count()).where(DetectionResult.thumbnail_url.isnot(None))
            video_count_query = select(func.count()).where(DetectionResult.video_url.isnot(None))
            
            image_count_result = await self.session.execute(image_count_query)
            thumbnail_count_result = await self.session.execute(thumbnail_count_query)
            video_count_result = await self.session.execute(video_count_query)
            
            image_count = image_count_result.scalar() or 0
            thumbnail_count = thumbnail_count_result.scalar() or 0
            video_clip_count = video_count_result.scalar() or 0
            
            # 디바이스별 통계
            device_stats_query = (select(Device.device_label, func.count(DetectionResult.detection_seq).label("detection_count"))
                                  .select_from(DetectionResult)
                                  .join(Device, DetectionResult.device_seq == Device.device_seq)
                                  .group_by(Device.device_label))
            
            device_stats_result = await self.session.execute(device_stats_query)
            device_stats_rows = device_stats_result.all()
            
            device_stats = {}
            for device_label, count in device_stats_rows:
                device_stats[device_label or "Unknown Device"] = count
                
            # 최근 탐지 시간
            latest_detection_query = select(func.max(DetectionResult.detected_at))
            latest_detection_result = await self.session.execute(latest_detection_query)
            latest_detection = latest_detection_result.scalar()
            
            return {
                "total_detections": total_detections,
                "total_files": total_files,
                "image_count": image_count,
                "thumbnail_count": thumbnail_count,
                "video_clip_count": video_clip_count,
                "total_size_mb": 0.0,
                "device_stats": device_stats,
                "latest_detection": latest_detection,
                "generated_at": datetime.now()
            }
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"미디어 통게 조회 중 데이터 베이스 오류 발생: {str(e)}")
        except Exception as e:
            raise Exception(f"미디어 통계 조회 중 오류 발생: {str(e)}")
        
    async def update_detection_media_urls(self, detection_id: int, 
                                          image_url: Optional[str] = None,
                                          thumbnail_url: Optional[str] = None,
                                          video_url: Optional[str] = None) -> bool:
        """탐지 결과 미디어 url 업데이트
        - detection_id: 탐지 결과 id
        - image_url: 이미지 url
        - thumbnail_url: 썸네일 url
        - video_url: 동영상 url
        """
        try:
            query = select(DetectionResult).where(DetectionResult.detection_seq == detection_id)
            result = await self.session.execute(query)
            detection_result = result.scalar_one_or_none()
            
            if not detection_result:
                return False
            
            update = False
            if image_url is not None:
                detection_result.image_url = image_url
                update = True
            
            if thumbnail_url is not None:
                detection_result.thumbnail_url = thumbnail_url
                update = True
                
            if video_url is not None:
                detection_result.video_url = video_url
                update = True
                
            if update:
                await self.session.commit()
                return True
            
            return False
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"미디어 url 업데이트 중 데이터 베이스 오류 발생: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"미디어 url 업데이트 중 오류 발생: {str(e)}")
        
    async def delete_detection_media(self, detection_id: int) -> bool:
        """탐지 결과 삭제 - 데이터 베이스 레코드만 삭제 (파일은 file_storage_manager에서 처리)"""
        try:
            query = select(DetectionResult).where(DetectionResult.detection_seq == detection_id)
            result = await self.session.execute(query)
            detection_result = result.scalar_one_or_none()
            
            if not detection_result:
                return False
            
            await self.session.delete(detection_result)
            await self.session.commit()
            
            return True
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"미디어 삭제 중 데이터베이스 오류 발생: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"미디어 삭제 중 오류 발생: {str(e)}")
        
    async def get_media_by_device_and_date(self, device_name: str,start_date: datetime, end_date: datetime, lang_tag: str = "en-US") -> List[Dict[str, Any]]:
        """특정 디바이스의 날짜 범위별 미디어 조회
        - 디바이스별 일일 / 주간 / 월간 리포트
        - 대시보드 차트 데이터
        - 특정 기간 탐지 이력 분석
        """
        try:
            query = (select(DetectionResult, Device.device_label, ModelProductLang.product_name)
                     .select_from(DetectionResult)
                     .join(Device, DetectionResult.device_seq ==Device.device_seq)
                     .join(ModelProduct, DetectionResult.model_product_seq == ModelProduct.model_product_seq)
                     .join(ModelProductLang, and_(
                         ModelProduct.model_product_seq == ModelProductLang.model_product_seq,
                         ModelProductLang.lang_tag == lang_tag))
                     .where(and_(
                         Device.device_label.ilike(f"%{device_name}%"),
                         DetectionResult.detected_at >= start_date,
                         DetectionResult.detected_at <= end_date
                         ))
                     .order_by(desc(DetectionResult.detected_at))
                     )
            
            result = await self.session.execute(query)
            rows = result.all()
            
            media_list = []
            for detection_result, device_label, product_name in rows:
                media_data = {
                    "detection_id": detection_result.detection_seq,
                    "detection_time": detection_result.detected_at,
                    "device_name": device_label or "Unknown Device",
                    "model_name": product_name or "Unknown Model",
                    "confidence": float(detection_result.confidence),
                    "detection_label": detection_result.detection_label,
                    "original_image": {
                        "url": detection_result.image_url,
                        "type": "image",
                        "created_at": detection_result.reg_dt
                    },
                    "thumbnail": {
                        "url": detection_result.thumbnail_url,
                        "type": "thumbnail",
                        "created_at": detection_result.reg_dt
                    },
                    "video_clip": {
                        "url": detection_result.video_url,
                        "type": "video_clip",
                        "created_at": detection_result.reg_dt
                    }
                }
                media_list.append(media_data)
                
            return media_list
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"디바이스별 미디어 조회 중 데이터베이스 오류 발생: {str(e)}")
        except Exception as e:
            raise Exception(f"디바이스별 미디어 조회 중 오류 발생: {str(e)}")
        