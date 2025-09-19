from typing import List, Dict, Optional, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.base_repository import BaseRepository
from app.models.detection_result import DetectionResult
from app.models.device import Device
from app.models.group import Group
from app.models.detection_mapping import ModelDetectionMapping
from app.models.model_product import ModelProduct, ModelProductLang
from app.models.guidance_model import GuidanceModel, GuidanceModelLang
from app.models.alert import Alert
from app.models.subscription import ModelProductSubscription

class DetectionRepository(BaseRepository):
    """탐지 결과 관련 레포지토리"""

    # 다국어 "개발중" 메시지
    DEVELOPMENT_MESSAGES = {
        "ko-KR": "개발 중입니다",
        "en-US": "Under Development",
        "zh-CN": "开发中",
        "ja-JP": "開発中です",
        "th-TH": "กำลังพัฒนา",
        "fil-PH": "Sa pag-develop pa"
    }
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        
    async def get_today_stats(self, user_seq: int) -> Dict[str, Any]:
        """오늘의 탐지 통계 조회 - 메인 페이지 대시 보드용
        - 오늘 하루 총 탐지 건수 계산
        - 오늘 위험도별 분포
        - 활성화 디바이스 수
        """
        try:
            today = date.today()
            
            # 오늘의 위험도별 통계 쿼리 (삼중 보안 필터링: 디바이스 + 탐지결과 + 구독)
            stats_query = select(
                func.count(DetectionResult.detection_seq).label('total_detections'),
                func.count(func.distinct(DetectionResult.device_seq)).label('devices_active'),
                ModelDetectionMapping.danger_level,
                func.count(DetectionResult.detection_seq).label('level_count')
            ).select_from(
                DetectionResult
                .join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelDetectionMapping, and_(
                    DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                    DetectionResult.detection_label == ModelDetectionMapping.detection_label
                ))
                .join(ModelProductSubscription, and_(
                    ModelProductSubscription.user_seq == user_seq,                    # 구독 소유자 확인
                    ModelProductSubscription.model_product_seq == DetectionResult.model_product_seq,  # 모델 상품 연결
                    ModelProductSubscription.subscription_status == 'A'              # 활성 구독만
                ))
            ).where(
                and_(
                    Device.user_seq == user_seq,                                      # 디바이스 소유자 확인
                    DetectionResult.user_seq == user_seq,                            # 탐지 결과 소유자 확인
                    func.date(DetectionResult.detected_at) == today                   # 오늘 데이터만
                )
            ).group_by(ModelDetectionMapping.danger_level)
            
            result = await self.db.execute(stats_query)
            stats_data = result.fetchall()
            
            # 전체 디바이스 수 조회 - 사용자별 필터링
            total_devices_query = select(func.count(Device.device_seq)).where(Device.user_seq == user_seq)
            total_device_result = await self.db.execute(total_devices_query)
            total_devices = total_device_result.scalar() or 0
            
            # 통계 데이터 정리
            total_detections = 0
            devices_active = 0
            risk_distribution = {
                'critical': 0,  # 위험
                'high': 0,     # 경고
                'medium': 0,   # 주의
                'safe': 0   # 정상 => low + safe + normal 합계
            }
            
            for row in stats_data:
                if devices_active == 0:
                    devices_active = row.devices_active
                    
                total_detections += row.level_count
                
                # 위험도별 그룹핑 처리
                if row.danger_level == 'critical':
                    risk_distribution['critical'] = row.level_count
                elif row.danger_level == 'high':
                    risk_distribution['high'] = row.level_count
                elif row.danger_level == 'medium':
                    risk_distribution['medium'] = row.level_count
                elif row.danger_level in ['low', 'safe', 'normal']:    # low, safe, normal 모두 safe로 통합
                    risk_distribution['safe'] += row.level_count
                    
            result_stats = {
                'total_detections': total_detections,
                'devices_active': devices_active,
                'risk_distribution': risk_distribution,
                'total_devices': total_devices
            }
            
            self.logger.info(f"오늘 통게 조회 완료 [user_seq={user_seq}]: 총 {total_detections}건, (위험:{risk_distribution['critical']}, 경고:{risk_distribution['high']}, 주의:{risk_distribution['medium']}, 정상:{risk_distribution['safe']})")
            return result_stats
        
        except SQLAlchemyError as e:
            self.logger.error(f"오늘 통계 조회 오류 [user_seq={user_seq}]: {str(e)}")
            return {
                'total_detections': 0,
                'devices_active': 0,
                'risk_distribution': {'critical': 0, 'high': 0, 'medium': 0, 'safe': 0},
                'total_devices': 0
            }
            
    async def get_recent_detections_with_full_info(self, user_seq: int, language: str = 'en-US', limit: int = 10) -> List[Dict[str, Any]]:
        """최근 탐지 목록 조회"""
        try:
            # 7개 테이블 join 쿼리 (Alert + Subscription 테이블 추가)
            query = select(
                # 탐지 정보
                DetectionResult.detection_seq,
                DetectionResult.detection_class,  # ✅ 새로 추가된 컬럼
                DetectionResult.detection_label,
                DetectionResult.thumbnail_url,
                DetectionResult.detected_at,
                DetectionResult.confidence,

                # 디바이스 정보
                Device.device_label,
                Device.device_seq,

                # 그룹 정보
                Group.group_name,

                # 위험도
                ModelDetectionMapping.danger_level,

                # 상품명 (다국어)
                ModelProductLang.product_name,

                # AI 안내문 (실제 알림 기록)
                Alert.ai_detection_guide.label('alert_guide'),

                # AI 안내문 템플릿 (다국어)
                GuidanceModelLang.ai_detection_guide.label('template_guide')
            ).select_from(
                DetectionResult
                .join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelDetectionMapping, and_(
                    DetectionResult.model_product_seq == ModelDetectionMapping.model_product_seq,
                    DetectionResult.detection_label == ModelDetectionMapping.detection_label
                ))
                .join(ModelProductSubscription, and_(
                    ModelProductSubscription.user_seq == user_seq,                    # 구독 소유자 확인
                    ModelProductSubscription.model_product_seq == DetectionResult.model_product_seq,  # 모델 상품 연결
                    ModelProductSubscription.subscription_status == 'A'              # 활성 구독만
                ))
                .outerjoin(Group, Device.group_seq == Group.group_seq)
                .outerjoin(ModelProductLang, and_(
                    DetectionResult.model_product_seq == ModelProductLang.model_product_seq,
                    ModelProductLang.lang_tag == language
                ))
                .outerjoin(GuidanceModel,
                    GuidanceModel.model_product_seq == DetectionResult.model_product_seq
                )
                .outerjoin(GuidanceModelLang, and_(
                    GuidanceModelLang.guidance_model_product_seq == GuidanceModel.guidance_model_product_seq,
                    GuidanceModelLang.lang_tag == language
                ))
                .outerjoin(Alert, and_(
                    Alert.detection_seq == DetectionResult.detection_seq,
                    Alert.lang_tag == language
                ))
            ).where(
                and_(
                    Device.user_seq == user_seq,                                      # 디바이스 소유자 확인
                    DetectionResult.user_seq == user_seq                             # 탐지 결과 소유자 확인
                )
            ).order_by(desc(DetectionResult.detected_at)).limit(limit)
            
            result = await self.db.execute(query)
            raw_data = result.fetchall()
            
            # 데이터 가공
            detections = []
            for row in raw_data:
                location_info = self._get_location_info(row.group_name, row.device_label)
                product_name = row.product_name or self._get_default_product_message(language)
                danger_level_display = self._get_danger_level_display(row.danger_level)

                # AI 안내문 처리 - 실제 알림 → 템플릿 → "개발중"
                ai_guide = (
                    row.alert_guide or                           # 1순위: 실제 알림 (tbl_ai_alerts)
                    row.template_guide or                        # 2순위: AI 안내 템플릿 (tbl_guidance_model_product_lang)
                    self.DEVELOPMENT_MESSAGES.get(language, "Under Development")  # 3순위: 개발중 메시지
                )

                detection_info = {
                    'detection_seq': row.detection_seq,
                    'thumbnail_url': row.thumbnail_url,
                    'detection_class': row.detection_class,      # ✅ 새 컬럼 추가
                    'detection_label': row.detection_label,
                    'device_label': row.device_label,
                    'group_name': row.group_name,
                    'location_info': location_info,
                    'product_name': product_name,
                    'danger_level': row.danger_level,
                    'danger_level_display': danger_level_display,
                    'detected_at': row.detected_at,
                    'confidence': float(row.confidence) if row.confidence else 0.0,
                    'ai_detection_guide': ai_guide
                }

                detections.append(detection_info)
                
            self.logger.info(f"최근 탐지 목록 조회 완료 [user_seq={user_seq}]: {len(detections)}건")
            return detections
        
        except SQLAlchemyError as e:
            self.logger.error(f"최근 탐지 목록 조회 오류 [user_seq={user_seq}]: {str(e)}")
            return []
        
    async def get_hourly_chart_data(self, user_seq: int, target_date: date) -> List[Dict[str, Any]]:
        """시간대별 탐지 차트 데이터 조회 (차트 모달용)"""
        try:
            user_devices = await self._get_user_device_list(user_seq)
            if not user_devices:
                self.logger.warning(f"시간대별 차트 데이터 없음 - 디바이스 없음 [user_seq={user_seq}]")
                return self._get_empty_hourly_data_list()

            hourly_result = await self.db.execute(
                select(
                    func.hour(DetectionResult.detected_at).label('hour'),
                    func.count(DetectionResult.detection_seq).label('count')
                )
                .select_from(DetectionResult)
                .join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelProductSubscription, and_(
                    ModelProductSubscription.user_seq == user_seq,                    # 구독 소유자 확인
                    ModelProductSubscription.model_product_seq == DetectionResult.model_product_seq,  # 모델 상품 연결
                    ModelProductSubscription.subscription_status == 'A'              # 활성 구독만
                ))
                .where(
                    and_(
                        Device.user_seq == user_seq,                                  # 디바이스 소유자 확인
                        DetectionResult.user_seq == user_seq,                        # 탐지 결과 소유자 확인
                        func.date(DetectionResult.detected_at) == target_date         # 대상 날짜만
                    )
                )
                .group_by(func.hour(DetectionResult.detected_at))
                .order_by(func.hour(DetectionResult.detected_at))
            )

            hourly_data = self._get_empty_hourly_data()

            for hour, count in hourly_result.fetchall():
                hourly_data[hour]['count'] = count

            self.logger.info(f"시간대별 차트 데이터 조회 완료 [user_seq={user_seq}, date={target_date}]")
            return list(hourly_data.values())

        except SQLAlchemyError as e:
            self.logger.error(f"시간대별 차트 데이터 조회 오류 [user_seq={user_seq}, date={target_date}]: {str(e)}")
            return self._get_empty_hourly_data_list()

    def _get_empty_hourly_data(self) -> Dict[int, Dict[str, Any]]:
        """0시~23시 빈 데이터 구조 생성"""
        return {
            hour: {
                'hour': hour,
                'hour_display': f"{hour:02d}:00",
                'count': 0
            } for hour in range(24)
        }

    def _get_empty_hourly_data_list(self) -> List[Dict[str, Any]]:
        """빈 시간대별 데이터를 리스트로 반환"""
        return list(self._get_empty_hourly_data().values())

    async def get_device_distribution_chart(self, user_seq: int, target_date: date) -> List[Dict[str, Any]]:
        """디바이스별 탐지 분포 차트 데이터 조회 (차트 모달용)"""
        try:
            user_devices = await self._get_user_device_list(user_seq)
            if not user_devices:
                self.logger.warning(f"디바이스별 차트 데이터 없음 - 디바이스 없음 [user_seq={user_seq}]")
                return []

            distribution_result = await self.db.execute(
                select(
                    Device.device_label,
                    Group.group_name,
                    Device.device_seq,
                    func.count(DetectionResult.detection_seq).label('count')
                )
                .select_from(DetectionResult)
                .join(Device, DetectionResult.device_seq == Device.device_seq)
                .join(ModelProductSubscription, and_(
                    ModelProductSubscription.user_seq == user_seq,                    # 구독 소유자 확인
                    ModelProductSubscription.model_product_seq == DetectionResult.model_product_seq,  # 모델 상품 연결
                    ModelProductSubscription.subscription_status == 'A'              # 활성 구독만
                ))
                .outerjoin(Group, Device.group_seq == Group.group_seq)
                .where(
                    and_(
                        Device.user_seq == user_seq,                                  # 디바이스 소유자 확인
                        DetectionResult.user_seq == user_seq,                        # 탐지 결과 소유자 확인
                        func.date(DetectionResult.detected_at) == target_date         # 대상 날짜만
                    )
                )
                .group_by(Device.device_seq, Device.device_label, Group.group_name)
                .order_by(func.count(DetectionResult.detection_seq).desc())
            )

            results = distribution_result.fetchall()
            total_count = sum(row.count for row in results)

            if total_count == 0:
                self.logger.info(f"디바이스별 차트 데이터 없음 - 탐지 없음 [user_seq={user_seq}, date={target_date}]")
                return []

            distribution_data = []
            for row in results:
                percentage = round((row.count / total_count) * 100, 1)

                distribution_data.append({
                    'device_seq': row.device_seq,
                    'device_label': row.device_label or f"디바이스_{row.device_seq}",
                    'group_name': row.group_name or "기본 그룹",
                    'count': row.count,
                    'percentage': percentage
                })

            self.logger.info(f"디바이스별 차트 데이터 조회 완료 [user_seq={user_seq}, date={target_date}]: {len(distribution_data)}개 디바이스")
            return distribution_data

        except SQLAlchemyError as e:
            self.logger.error(f"디바이스별 차트 데이터 조회 오류 [user_seq={user_seq}, date={target_date}]: {str(e)}")
            return []