import logging
from math import exp
from pstats import Stats
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from fastapi import HTTPException, status

from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.detection_repository import DetectionRepository
from app.schemas.dashboard import (
    DashboardOverview,
    HourlyChartData,
    DeviceStatus,
    DeviceModelSubscription,
    RecentRiskDetection,
    RecentAlert,
    DashboardCompleteData
)
from backend.app.routers import dashboard

class DashboardService:
    """대시보드 비즈니스 로직 서비스
    - 사용자별 대시보드 통계 데이터
    - 시간대별 탐지 차트 데이터 생성
    - 디바이스 상태 및 최근 탐지 정보 조회
    - 다국어 지원 및 권한 기반 데이터 필터링
    """
    
    def __init__(self, dashboard_repo: DashboardRepository, detection_repo: DetectionRepository):
        self.dashboard_repo = dashboard_repo
        self.detection_repo = detection_repo
        self.logger = logging.getLogger(__name__)
        
    async def get_comprehensive_dashboard_data(self, user_seq: int, user_language: str = 'en-US', target_date: Optional[date] = None) -> DashboardCompleteData:
        """사용자 대시보드 전체 데이터 조회"""
        try:
            if target_date is None:
                target_date = date.today()
                
            self.logger.info(f"대시보드 전체 데이터 조회 시작 [user_seq={user_seq}, date={target_date}]")
            
            # 대시보드 개요 통계 조회
            dashboard_overview_data = await self._get_dashboard_overview(user_seq, target_date)
            
            # 시간대별 차트 데이터 조회
            hourly_chart_data = await self._get_hourly_chart(user_seq, target_date)

            # 등록된 디바이스별 활성화된 모델 상품명 조회
            device_model_subscriptions = await self._get_device_model_subscriptions(user_seq)

            # 최근 위험 탐지 목록 조회
            recent_risk_detections = await self._get_recent_risk_detections(user_seq, user_language)

            # 최근 알림 목록 조회
            recent_alerts = await self._get_recent_alerts(user_seq)
            
            # 통합 응답 데이터 생성
            complete_dashboard_data = DashboardCompleteData(
                overview=dashboard_overview_data,
                hourly_chart=hourly_chart_data,
                device_model_subscriptions=device_model_subscriptions,
                recent_detections=recent_risk_detections,
                recent_alerts=recent_alerts,
                last_updated=datetime.now(),
                user_language=user_language
            )
            
            self.logger.info(f"대시보드 데이터 조회 완료 [user_seq={user_seq}]: 탐지 {dashboard_overview_data.today_total_detections}건")
            return complete_dashboard_data
        
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"대시보드 데이터 조회 오류 [user_seq={user_seq}]: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="대시보드 데이터를 불러오는 중 오류가 발생했습니다.")
        
    async def get_dashboard_overview(self, user_seq: int, target_date: Optional[date] = None) -> DashboardOverview:
        """대시보드 개요 통계 조회"""
        try:
            dashboard_overview = await self._get_dashboard_overview(user_seq, target_date or date.today())
            self.logger.info(f"대시보드 개요 조회 완료 [user_seq={user_seq}]")
            return dashboard_overview
        
        except Exception as e:
            self.logger.error(f"대시보드 개요 조회 오류 [user_seq={user_seq}]: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="대시보드 개요 데이터를 불러올 수 없습니다.")
        
    async def get_hourly_detection_chart(self, user_seq: int, target_date: Optional[date] = None) -> List[HourlyChartData]:
        """시간대별 탐지 차트 데이터 조회"""
        try:
            hourly_char_data = await self._get_hourly_chart(user_seq, target_date or date.today())
            self.logger.info(f"디바이스별 분포 차트 데이터 조회 완료 [user_seq={user_seq}]")
            return hourly_char_data
        
        except Exception as e:
            self.logger.error(f"시간대별 차트 데이터 조회 오류 [user_seq={user_seq}]: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="차트 데이터를 불러올 수 없습니다.")
        
    async def get_device_distribution_chart(self, user_seq: int, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """디바이스별 탐지 분포 차트 데이터 조회"""
        try:
            distribution_data = await self.detection_repo.get_device_distribution_chart(user_seq, target_date or date.today())
            self.logger.info(f"디바이스별 분포 차트 데이터 조회 완료 [user_seq={user_seq}]")
            return distribution_data
        
        except Exception as e:
            self.logger.error(f"디바이스별 분포 차트 데이터 조회 오류 [user_seq={user_seq}]: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="디바이스 분포 차트 데이터를 불러올 수 없습니다.")
        
    # 헬퍼 메서드
    async def _get_dashboard_overview(self, user_seq: int, target_date: date) -> DashboardOverview:
        """대시보드 개요 조회"""
        try:
            summary_stats = await self.dashboard_repo.get_today_dashboard_summary(user_seq, target_date)
            
            risk_classification = self._classify_risk_levels_for_frontend(summary_stats)
            
            dashboard_overview = DashboardOverview(
                today_total_detections=summary_stats['total_detections_today'],
                devices_detected_today=summary_stats['devices_detected_today'],
                total_registered_devices=summary_stats['total_registered_devices'],
                risk_level_critical_count=risk_classification['critical'],
                risk_level_high_count=risk_classification['high'],
                risk_level_medium_count=risk_classification['medium'],
                security_safe_count=risk_classification['safe'],
                general_detection_count=risk_classification['normal'],
                last_updated=datetime.now()
            )
            
            return dashboard_overview
        
        except Exception as e:
            self.logger.error(f"대시보드 개요 데이터 조회 실패 [user_seq={user_seq}]: {str(e)}")
            raise
        
    async def _get_hourly_chart(self, user_seq: int, target_date: date) -> List[HourlyChartData]:
        """시간대별 차트 데이터 조회"""
        try:
            hourly_data = await self.dashboard_repo.get_hourly_detection_chart_data(user_seq, target_date)

            # 24시간 전체 데이터 생성 (데이터가 없는 시간은 0으로 채움)
            hourly_chart_list = []
            for hour in range(24):
                hour_data = next((data for data in hourly_data if data['hour'] == hour), None)

                hourly_chart_list.append(HourlyChartData(
                    hour=hour,
                    hour_display=f"{hour:02d}:00",
                    detection_count=hour_data['detection_count'] if hour_data else 0
                ))

            return hourly_chart_list

        except Exception as e:
            self.logger.error(f"시간대별 차트 데이터 조회 실패 [user_seq={user_seq}]: {str(e)}")
            raise

    async def _get_device_model_subscriptions(self, user_seq: int) -> List[DeviceModelSubscription]:
        """등록된 디바이스별 활성화된 모델 상품명 조회"""
        try:
            device_model_data = await self.dashboard_repo.get_device_model_subscriptions(user_seq)

            device_subscriptions = []
            for device_data in device_model_data:
                device_subscriptions.append(DeviceModelSubscription(
                    device_seq=device_data['device_seq'],
                    device_label=device_data['device_label'],
                    device_type=device_data['device_type'],
                    activated_model_products=device_data['activated_model_products'],
                    today_detection_count=device_data['today_detection_count'],
                    last_detection_time=device_data['last_detection_time']
                ))

            return device_subscriptions

        except Exception as e:
            self.logger.error(f"디바이스 모델 구독 조회 실패 [user_seq={user_seq}]: {str(e)}")
            raise

    async def _get_recent_alerts(self, user_seq: int) -> List[RecentAlert]:
        """최근 알림 목록 조회"""
        try:
            alert_data = await self.dashboard_repo.get_recent_alert_notifications(user_seq, limit=5)

            recent_alerts = []
            for alert in alert_data:
                recent_alerts.append(RecentAlert(
                    alert_seq=alert['alert_seq'],
                    device_label=alert['device_label'],
                    alert_type=alert['alert_type'],
                    alert_message=alert['alert_message'],
                    alert_time=alert['alert_time'],
                    is_read=alert['is_read'],
                    related_detection_seq=alert['related_detection_seq']
                ))

            return recent_alerts

        except Exception as e:
            self.logger.error(f"최근 알림 조회 실패 [user_seq={user_seq}]: {str(e)}")
            raise

    async def _get_recent_risk_detections(self, user_seq: int, user_language: str = 'en-US') -> List[RecentRiskDetection]:
        """최근 위험 탐지 목록 조회"""
        try:
            risk_detections_data = await self.detection_repo.get_recent_detections_with_full_info(user_seq, limit=10)

            recent_detections = []
            for detection in risk_detections_data:
                recent_detections.append(RecentRiskDetection(
                    detection_seq=detection['detection_seq'],
                    device_label=detection['device_label'],
                    detection_class=detection['detection_class'],
                    detection_label=detection['detection_label'],
                    danger_level=detection['danger_level'],
                    detection_confidence=detection['detection_confidence'],
                    thumbnail_image_path=detection['thumbnail_image_path'],
                    detection_time=detection['detection_time'],
                    ai_detection_guide=detection.get('ai_detection_guide'),
                    location_info=detection.get('location_info'),
                    bounding_box_info=detection.get('bounding_box_info')
                ))

            return recent_detections

        except Exception as e:
            self.logger.error(f"최근 위험 탐지 조회 실패 [user_seq={user_seq}]: {str(e)}")
            raise

    def _classify_risk_levels_for_frontend(self, summary_stats: Dict[str, Any]) -> Dict[str, int]:
        """위험 수준 분류 (프론트엔드용)"""
        return {
            'critical': summary_stats.get('risk_detections_count', 0),  # critical+high+medium
            'high': 0,
            'medium': 0,
            'safe': summary_stats.get('safe_detections_count', 0),    # low+safe
            'normal': summary_stats.get('normal_detections_count', 0)  # normal
        }