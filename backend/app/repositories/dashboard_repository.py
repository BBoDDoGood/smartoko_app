from typing import List, Dict, Optional, Any
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, distinct
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.base_repository import BaseRepository
from app.models.detection_result import DetectionResult
from app.models.device import Device
from app.models.group import Group
from app.models.detection_mapping import ModelDetectionMapping
from app.models.subscription import ModelProductSubscription


class DashboardRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_today_dashboard_summary(self, user_seq: int, target_date: Optional[date] = None) -> Dict[str, Any]:
        """오늘 대시보드 요약 통계
            - total_detections_today: 오늘 전체 탐지 건수
            - devices_detected_today: 오늘 탐지가 발생한 디바이스 수
            - total_registered_devices: 사용자 전체 등록 디바이스 수
            - risk_detections_count: 위험 탐지 (critical + high + medium)
            - safe_detections_count: 안전 탐지 (low + safe)
            - normal_detections_count: 일반 객체 탐지 (normal)
        """
        try:
            if target_date is None:
                target_date = date.today()

            # 기본 탐지 통계 조회
            basic_detection_stats = await self._get_basic_detection_stats(user_seq, target_date)

            # 디바이스 등록 통계 조회
            device_registration_stats = await self._get_device_registration_stats(user_seq)

            # 위험도별 탐지 건수 조회
            risk_breakdown_counts = await self._get_risk_breakdown_counts(user_seq, target_date)

            return {
                'total_detections_today': basic_detection_stats.get('total_count', 0),
                'devices_detected_today': basic_detection_stats.get('detected_device_count', 0),
                'total_registered_devices': device_registration_stats.get('registered_count', 0),
                'risk_detections_count': risk_breakdown_counts[0],      # critical + high + medium
                'safe_detections_count': risk_breakdown_counts[1],      # low + safe
                'normal_detections_count': risk_breakdown_counts[2],    # normal
                'target_date': target_date.isoformat()
            }

        except SQLAlchemyError as e:
            self.logger.error(f"Dashboard summary query failed for user {user_seq}: {str(e)}")
            raise

    async def _get_basic_detection_stats(self, user_seq: int, target_date: date) -> Dict[str, int]:
        """기본 탐지 통계 조회 (사용자가 활성화한 모델 상품만)"""
        query = select(
            func.count(DetectionResult.detection_seq).label('total_count'),
            func.count(distinct(DetectionResult.device_seq)).label('detected_device_count')
        ).select_from(
            DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
            .join(ModelDetectionMapping, and_(
                DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                DetectionResult.detection_label == ModelDetectionMapping.detection_label
            ))
            .join(ModelProductSubscription,
                  and_(
                      ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                      ModelProductSubscription.user_seq == user_seq
                  ))
        ).where(
            and_(
                Device.user_seq == user_seq,
                DetectionResult.user_seq == user_seq,
                func.date(DetectionResult.detected_at) == target_date,
                ModelProductSubscription.subscription_status == 'A'  # 활성화된 구독만
            )
        )

        result = await self.db.execute(query)
        row = result.fetchone()

        return {
            'total_count': row.total_count if row.total_count else 0,
            'detected_device_count': row.detected_device_count if row.detected_device_count else 0
        }

    async def _get_device_registration_stats(self, user_seq: int) -> Dict[str, int]:
        """디바이스 등록 통계 조회"""
        query = select(
            func.count(Device.device_seq).label('registered_count')
        ).where(
            Device.user_seq == user_seq
        )

        result = await self.db.execute(query)
        row = result.fetchone()

        return {
            'registered_count': row.registered_count if row.registered_count else 0
        }

    async def _get_risk_breakdown_counts(self, user_seq: int, target_date: date) -> tuple[int, int, int]:
        """위험도별 탐지 건수 조회 (사용자가 활성화한 모델 상품만)
        - risk_count: 위험 탐지 건수
        - safe_count: 안전 탐지 건수
        - normal_count: 일반 객체 탐지 건수
        """
        # critical + high + medium = 위험
        risk_query = select(
            func.count(DetectionResult.detection_seq)
        ).select_from(
            DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
            .join(ModelDetectionMapping, and_(
                DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                DetectionResult.detection_label == ModelDetectionMapping.detection_label
            ))
            .join(ModelProductSubscription,
                  and_(
                      ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                      ModelProductSubscription.user_seq == user_seq
                  ))
        ).where(
            and_(
                Device.user_seq == user_seq,
                DetectionResult.user_seq == user_seq,
                func.date(DetectionResult.detected_at) == target_date,
                ModelDetectionMapping.danger_level.in_(['critical', 'high', 'medium']),
                ModelProductSubscription.subscription_status == 'A'  # 활성화된 구독만
            )
        )

        # low + safe = 안전
        safe_query = select(
            func.count(DetectionResult.detection_seq)
        ).select_from(
            DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
            .join(ModelDetectionMapping, and_(
                DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                DetectionResult.detection_label == ModelDetectionMapping.detection_label
            ))
            .join(ModelProductSubscription,
                  and_(
                      ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                      ModelProductSubscription.user_seq == user_seq
                  ))
        ).where(
            and_(
                Device.user_seq == user_seq,
                DetectionResult.user_seq == user_seq,
                func.date(DetectionResult.detected_at) == target_date,
                ModelDetectionMapping.danger_level.in_(['low', 'safe']),
                ModelProductSubscription.subscription_status == 'A'
            )
        )

        # normal = 일반 객체
        normal_query = select(
            func.count(DetectionResult.detection_seq)
        ).select_from(
            DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
            .join(ModelDetectionMapping, and_(
                DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                DetectionResult.detection_label == ModelDetectionMapping.detection_label
            ))
            .join(ModelProductSubscription,
                  and_(
                      ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                      ModelProductSubscription.user_seq == user_seq
                  ))
        ).where(
            and_(
                Device.user_seq == user_seq,
                DetectionResult.user_seq == user_seq,
                func.date(DetectionResult.detected_at) == target_date,
                ModelDetectionMapping.danger_level == 'normal',
                ModelProductSubscription.subscription_status == 'A'
            )
        )

        risk_result = await self.db.execute(risk_query)
        safe_result = await self.db.execute(safe_query)
        normal_result = await self.db.execute(normal_query)

        risk_count = risk_result.scalar() or 0
        safe_count = safe_result.scalar() or 0
        normal_count = normal_result.scalar() or 0

        return (risk_count, safe_count, normal_count)

    async def get_hourly_detection_chart_data(self, user_seq: int, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """시간대별 탐지 차트 데이터 조회"""
        try:
            if target_date is None:
                target_date = date.today()

            query = select(
                func.hour(DetectionResult.detected_at).label('hour'),
                func.count(DetectionResult.detection_seq).label('detection_count'),
                func.sum(
                    func.case(
                        (ModelDetectionMapping.danger_level.in_(['critical', 'high', 'medium']), 1),
                        else_=0
                    )
                ).label('risk_count'),
                func.sum(
                    func.case(
                        (ModelDetectionMapping.danger_level.in_(['low', 'safe']), 1),
                        else_=0
                    )
                ).label('safe_count'),
                func.sum(
                    func.case(
                        (ModelDetectionMapping.danger_level == 'normal', 1),
                        else_=0
                    )
                ).label('normal_count')
            ).select_from(
                DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelDetectionMapping, and_(
                    DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                    DetectionResult.detection_label == ModelDetectionMapping.detection_label
                ))
                .join(ModelProductSubscription,
                      and_(
                          ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                          ModelProductSubscription.user_seq == user_seq
                      ))
            ).where(
                and_(
                    Device.user_seq == user_seq,
                    DetectionResult.user_seq == user_seq,
                    func.date(DetectionResult.detected_at) == target_date,
                    ModelProductSubscription.subscription_status == 'A'
                )
            ).group_by(
                func.hour(DetectionResult.detected_at)
            ).order_by(
                func.hour(DetectionResult.detected_at)
            )

            result = await self.db.execute(query)
            chart_data = []

            for row in result:
                chart_data.append({
                    'hour': row.hour,
                    'detection_count': row.detection_count or 0,
                    'risk_count': row.risk_count or 0,
                    'safe_count': row.safe_count or 0,
                    'normal_count': row.normal_count or 0
                })

            return chart_data

        except SQLAlchemyError as e:
            self.logger.error(f"Hourly chart data query failed for user {user_seq}: {str(e)}")
            raise

    async def get_user_device_status_list(self, user_seq: int) -> List[Dict[str, Any]]:
        """사용자 디바이스 상태 목록 조회"""
        try:
            # 오늘 날짜 설정
            today = date.today()

            # 기본 디바이스 정보와 그룹 정보 조회
            device_query = select(
                Device.device_seq,
                Device.device_label,
                Device.device_type,
                Device.group_seq,
                Group.group_name,
                Device.reg_dt
            ).select_from(
                Device.outerjoin(Group, Device.group_seq == Group.group_seq)
            ).where(
                Device.user_seq == user_seq
            ).order_by(
                Device.device_label
            )

            device_result = await self.db.execute(device_query)
            devices = device_result.fetchall()

            device_status_list = []

            for device in devices:
                # 각 디바이스별 오늘 탐지 건수 조회
                today_detection_query = select(
                    func.count(DetectionResult.detection_seq).label('today_count'),
                    func.max(DetectionResult.detected_at).label('last_detection_time')
                ).where(
                    and_(
                        DetectionResult.device_seq == device.device_seq,
                        DetectionResult.user_seq == user_seq,
                        func.date(DetectionResult.detected_at) == today
                    )
                )

                detection_result = await self.db.execute(today_detection_query)
                detection_stats = detection_result.fetchone()

                device_status_list.append({
                    'device_seq': device.device_seq,
                    'device_label': device.device_label or f"디바이스 {device.device_seq}",
                    'device_type': device.device_type,
                    'group_name': device.group_name or "미분류",
                    'status': 'registered',
                    'last_detection_time': detection_stats.last_detection_time.isoformat() if detection_stats.last_detection_time else None,
                    'today_detection_count': detection_stats.today_count or 0,
                    'registration_date': device.reg_dt.isoformat() if device.reg_dt else None
                })

            return device_status_list

        except SQLAlchemyError as e:
            self.logger.error(f"Device status list query failed for user {user_seq}: {str(e)}")
            raise

    async def get_recent_critical_alert_list(self, user_seq: int, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 위험 알림 목록 조회"""
        try:
            query = select(
                DetectionResult.detection_seq,
                DetectionResult.confidence,
                DetectionResult.detected_at,
                DetectionResult.detection_class,
                DetectionResult.thumbnail_url,
                Device.device_label,
                Group.group_name,
                ModelDetectionMapping.detection_label.label('detection_name'),
                ModelDetectionMapping.danger_level.label('risk_level')
            ).select_from(
                DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelDetectionMapping, and_(
                    DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                    DetectionResult.detection_label == ModelDetectionMapping.detection_label
                ))
                .join(ModelProductSubscription,
                      and_(
                          ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                          ModelProductSubscription.user_seq == user_seq
                      ))
                .outerjoin(Group, Device.group_seq == Group.group_seq)
            ).where(
                and_(
                    Device.user_seq == user_seq,
                    DetectionResult.user_seq == user_seq,
                    ModelDetectionMapping.danger_level.in_(['critical', 'high', 'medium']),
                    ModelProductSubscription.subscription_status == 'A'
                )
            ).order_by(
                desc(DetectionResult.detected_at)
            ).limit(limit)

            result = await self.db.execute(query)
            alert_list = []

            for row in result:
                alert_list.append({
                    'detection_seq': row.detection_seq,
                    'device_label': row.device_label or f"디바이스 {row.detection_seq}",
                    'detection_class': row.detection_class,
                    'detection_name': row.detection_name,
                    'risk_level': row.risk_level,
                    'confidence': float(row.confidence) if row.confidence else 0.0,
                    'detection_time': row.detected_at.isoformat() if row.detected_at else None,
                    'thumbnail_url': row.thumbnail_url,
                    'group_name': row.group_name or "미분류"
                })

            return alert_list

        except SQLAlchemyError as e:
            self.logger.error(f"Recent critical alerts query failed for user {user_seq}: {str(e)}")
            raise

    async def get_recent_general_detection_list(self, user_seq: int, limit: int = 20) -> List[Dict[str, Any]]:
        """최근 일반 탐지 목록 조회 (썸네일 포함)"""
        try:
            query = select(
                DetectionResult.detection_seq,
                DetectionResult.confidence,
                DetectionResult.detected_at,
                DetectionResult.detection_class,
                DetectionResult.thumbnail_url,
                Device.device_label,
                Group.group_name,
                ModelDetectionMapping.detection_label.label('detection_name'),
                ModelDetectionMapping.danger_level.label('risk_level')
            ).select_from(
                DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelDetectionMapping, and_(
                    DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                    DetectionResult.detection_label == ModelDetectionMapping.detection_label
                ))
                .join(ModelProductSubscription,
                      and_(
                          ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                          ModelProductSubscription.user_seq == user_seq
                      ))
                .outerjoin(Group, Device.group_seq == Group.group_seq)
            ).where(
                and_(
                    Device.user_seq == user_seq,
                    DetectionResult.user_seq == user_seq,
                    ModelProductSubscription.subscription_status == 'A'
                )
            ).order_by(
                desc(DetectionResult.detected_at)
            ).limit(limit)

            result = await self.db.execute(query)
            detection_list = []

            for row in result:
                detection_list.append({
                    'detection_seq': row.detection_seq,
                    'device_label': row.device_label or f"디바이스 {row.detection_seq}",
                    'detection_class': row.detection_class,
                    'detection_name': row.detection_name,
                    'risk_level': row.risk_level,
                    'confidence': float(row.confidence) if row.confidence else 0.0,
                    'detection_time': row.detected_at.isoformat() if row.detected_at else None,
                    'thumbnail_url': row.thumbnail_url,
                    'group_name': row.group_name or "미분류"
                })

            return detection_list

        except SQLAlchemyError as e:
            self.logger.error(f"Recent detections query failed for user {user_seq}: {str(e)}")
            raise

    async def get_user_active_model_subscriptions(self, user_seq: int) -> List[Dict[str, Any]]:
        """사용자가 활성화한 모델 상품 구독 목록 조회"""
        try:
            from app.models.model_product import ModelProduct

            # 오늘 날짜 설정
            today = date.today()

            # 활성화된 구독과 오늘 탐지 건수 조회
            query = select(
                ModelProductSubscription.subscription_seq,
                ModelProductSubscription.model_product_seq,
                ModelProduct.product_name.label('model_product_name'),
                ModelProductSubscription.subscription_status,
                ModelProductSubscription.subscribed_dt,
                ModelProductSubscription.expires_dt,
                func.count(DetectionResult.detection_seq).label('detection_count_today')
            ).select_from(
                ModelProductSubscription.join(ModelProduct, ModelProductSubscription.model_product_seq == ModelProduct.model_product_seq)
                .outerjoin(
                    ModelDetectionMapping,
                    ModelProductSubscription.model_product_seq == ModelDetectionMapping.model_product_seq
                )
                .outerjoin(
                    DetectionResult,
                    and_(
                        DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                        DetectionResult.detection_label == ModelDetectionMapping.detection_label,
                        func.date(DetectionResult.detected_at) == today
                    )
                )
                .outerjoin(Device, DetectionResult.device_seq == Device.device_seq)
            ).where(
                and_(
                    ModelProductSubscription.user_seq == user_seq,
                    ModelProductSubscription.subscription_status == 'A',
                    func.coalesce(Device.user_seq, user_seq) == user_seq
                )
            ).group_by(
                ModelProductSubscription.subscription_seq,
                ModelProductSubscription.model_product_seq,
                ModelProduct.product_name,
                ModelProductSubscription.subscription_status,
                ModelProductSubscription.subscribed_dt,
                ModelProductSubscription.expires_dt
            ).order_by(
                ModelProductSubscription.subscribed_dt.desc()
            )

            result = await self.db.execute(query)
            subscription_list = []

            for row in result:
                subscription_list.append({
                    'subscription_seq': row.subscription_seq,
                    'model_product_seq': row.model_product_seq,
                    'model_product_name': row.model_product_name or f"모델 상품 {row.model_product_seq}",
                    'subscription_status': row.subscription_status,
                    'subscribed_date': row.subscribed_dt.isoformat() if row.subscribed_dt else None,
                    'expires_date': row.expires_dt.isoformat() if row.expires_dt else None,
                    'detection_count_today': row.detection_count_today or 0
                })

            return subscription_list

        except SQLAlchemyError as e:
            self.logger.error(f"Active model subscriptions query failed for user {user_seq}: {str(e)}")
            raise

    async def get_device_model_subscriptions(self, user_seq: int) -> List[Dict[str, Any]]:
        """등록된 디바이스별 활성화된 모델 상품명 조회"""
        try:
            from app.models.model_product import ModelProduct

            # 오늘 날짜 설정
            today = date.today()

            # 디바이스별 활성화된 모델 상품 목록 조회
            query = select(
                Device.device_seq,
                Device.device_label,
                Device.device_type,
                func.group_concat(ModelProduct.product_name.distinct()).label('activated_models'),
                func.count(distinct(DetectionResult.detection_seq)).label('today_detection_count'),
                func.max(DetectionResult.detected_at).label('last_detection_time')
            ).select_from(
                Device.join(
                    ModelProductSubscription,
                    ModelProductSubscription.user_seq == Device.user_seq
                )
                .join(ModelProduct, ModelProductSubscription.model_product_seq == ModelProduct.model_product_seq)
                .outerjoin(
                    ModelDetectionMapping,
                    ModelProductSubscription.model_product_seq == ModelDetectionMapping.model_product_seq
                )
                .outerjoin(
                    DetectionResult,
                    and_(
                        DetectionResult.device_seq == Device.device_seq,
                        DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                        DetectionResult.detection_label == ModelDetectionMapping.detection_label,
                        func.date(DetectionResult.detected_at) == today
                    )
                )
            ).where(
                and_(
                    Device.user_seq == user_seq,
                    ModelProductSubscription.subscription_status == 'A'
                )
            ).group_by(
                Device.device_seq,
                Device.device_label,
                Device.device_type
            ).order_by(
                Device.device_label
            )

            result = await self.db.execute(query)
            device_model_list = []

            for row in result:
                activated_models = row.activated_models.split(',') if row.activated_models else []

                device_model_list.append({
                    'device_seq': row.device_seq,
                    'device_label': row.device_label or f"디바이스 {row.device_seq}",
                    'device_type': row.device_type,
                    'activated_model_products': activated_models,
                    'today_detection_count': row.today_detection_count or 0,
                    'last_detection_time': row.last_detection_time.isoformat() if row.last_detection_time else None
                })

            return device_model_list

        except SQLAlchemyError as e:
            self.logger.error(f"Device model subscriptions query failed for user {user_seq}: {str(e)}")
            raise

    async def get_recent_alert_notifications(self, user_seq: int, limit: int = 5) -> List[Dict[str, Any]]:
        """최근 알림 목록 조회 (탐지 결과 기반 위험 알림)"""
        try:
            # AI 알림 테이블이 없으므로 위험 탐지 결과를 알림으로 변환
            query = select(
                DetectionResult.detection_seq.label('alert_seq'),
                Device.device_seq,
                Device.device_label,
                DetectionResult.detection_class,
                DetectionResult.detection_label,
                ModelDetectionMapping.danger_level.label('alert_type'),
                DetectionResult.detected_at.label('alert_time'),
                DetectionResult.detection_seq.label('related_detection_seq')
            ).select_from(
                DetectionResult.join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelDetectionMapping, and_(
                    DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                    DetectionResult.detection_label == ModelDetectionMapping.detection_label
                ))
                .join(ModelProductSubscription,
                      and_(
                          ModelDetectionMapping.model_product_seq == ModelProductSubscription.model_product_seq,
                          ModelProductSubscription.user_seq == user_seq
                      ))
            ).where(
                and_(
                    Device.user_seq == user_seq,
                    DetectionResult.user_seq == user_seq,
                    ModelDetectionMapping.danger_level.in_(['critical', 'high']),
                    ModelProductSubscription.subscription_status == 'A'
                )
            ).order_by(
                desc(DetectionResult.detected_at)
            ).limit(limit)

            result = await self.db.execute(query)
            alert_list = []

            for row in result:
                # 알림 메시지 생성
                alert_message = f"{row.detection_class} 분류에서 {row.detection_label} 탐지됨"

                alert_list.append({
                    'alert_seq': row.alert_seq,
                    'device_label': row.device_label or f"디바이스 {row.device_seq}",
                    'alert_type': row.alert_type,
                    'alert_message': alert_message,
                    'alert_time': row.alert_time.isoformat() if row.alert_time else None,
                    'is_read': False,  # 기본값으로 미읽음 처리
                    'related_detection_seq': row.related_detection_seq
                })

            return alert_list

        except SQLAlchemyError as e:
            self.logger.error(f"Recent alert notifications query failed for user {user_seq}: {str(e)}")
            raise