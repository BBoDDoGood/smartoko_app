from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.services.dashboard_service import DashboardService
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.detection_repository import DetectionRepository

from app.schemas.dashboard import (
    DashboardCompleteData,
    DashboardOverview,
    DeviceModelSubscription,
    RecentRiskDetection,
    RecentAlert,
    HourlyChartData,
    DashboardResponse
)

# 라우터 인스턴스 생성
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# 헬스 체크 응답 스키마
class DashboardHealthResponse(BaseModel):
    """대시보드 서비스 상태 응답 모델"""
    status: str # healthy or error
    message: str    # 상태 설명 메시지
    
# 헬스 체크 api
@router.get("/health", response_model=DashboardHealthResponse)
async def dashboard_health(db: AsyncSession = Depends(get_db)):
    """대시보드 서비스 헬스 체크"""
    try:
        # 대시보드 레파지토리 초기화 테스트
        dashboard_repo = DashboardRepository(db)
        detection_repo = DetectionRepository(db)
        dashboard_service = DashboardService(dashboard_repo, detection_repo)
        
        return DashboardHealthResponse(status="healthy", message="대시보드 서비스 정상적으로 작동 중")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 서비스 상태 확인 실패: {str(e)}")
    
# 메인 대시보드 api
@router.get("/complete", response_model=DashboardCompleteData)
async def get_complete_dashboard_data(
    target_date: Optional[str] = Query(None, description="조회 날짜 (YYYY-MM-DD)"),
    user_language: str = Query("en-US", description="사용자 언어 (ko, en, zh, ja, th, ph)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """메인 대시보드 데이터 조회
    - 오늘의 탐지 요약 통계
    - 등록된 디바이스별 활성화된 모델 상품명
    - 최근 위험 탐지 목록 10개
    - 최근 알림 목록 5개
    - 시간대별 탐지 차트 -> 24시간
    """
    try:
        # 날짜 파싱 처리
        parsed_date = None
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)")
            
        # 서비스 인스턴스 생성
        dashboard_repo = DashboardRepository(db)
        detection_repo = DetectionRepository(db)
        dashboard_service = DashboardService(dashboard_repo, detection_repo)
        
        # 통합 대시보드 데이터 조회
        complete_data = await dashboard_service.get_comprehensive_dashboard_data(
            user_seq=current_user.user_seq,
            user_language=user_language,
            target_date=parsed_date
        )
        return complete_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 조회 실패: {str(e)}")
    
# 개별 컴포넌트 api들
@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    target_date: Optional[str] = Query(None, description="조회 날짜 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """대시보드 개요 통계만 조회"""
    try:
        # 날짜 파싱
        parsed_date = None
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)")
            
        # 서비스 생성
        dashboard_repo = DashboardRepository(db)
        detection_repo = DetectionRepository(db)
        dashboard_service = DashboardService(dashboard_repo, detection_repo)
        
        # 대시보드 개요 조회
        overview_data = await dashboard_service.get_dashboard_overview(
            user_seq=current_user.user_seq,
            target_date=parsed_date
        )
        return overview_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 개요 데이터 조회 실패: {str(e)}")
    
@router.get("/device-subscriptions", response_model=List[DeviceModelSubscription])
async def get_device_model_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """등록된 디바이스별 활성화된 모델 상품명 조회"""
    try:
        dashboard_repo = DashboardRepository(db)
        
        device_subscriptions_data = await dashboard_repo.get_device_model_subscriptions(
            user_seq=current_user.user_seq
        )
        
        # 스키마 객체로 변환
        result = []
        for device_data in device_subscriptions_data:
            result.append(DeviceModelSubscription(
                device_seq=device_data['device_seq'],
                device_label=device_data['device_label'],
                device_type=device_data['device_type'],
                activated_model_products=device_data['activated_model_products'],
                today_detection_count=device_data['today_detection_count'],
                last_detection_time=device_data['last_detection_time']
            ))  
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디바이스 구독 조회 실패: {str(e)}")
    
@router.get("/recent-detections", response_model=List[RecentRiskDetection])
async def get_recent_risk_detections(
    limit: int = Query(10, ge=1, le=50, description="조회 건수 (1~50)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """최근 위험 탐지 목록 조회"""
    try:
        detection_repo = DetectionRepository(db)
        
        # 최근 위험 탐지 조회
        detections_data = await detection_repo.get_recent_detections_with_full_info(user_seq=current_user.user_seq, limit=limit)
        
        # 스키마 변환
        result = []
        for detection in detections_data:
            result.append(RecentRiskDetection(
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
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최근 탐지 조회 실패: {str(e)}")
    
@router.get("/recent-alerts", response_model=List[RecentAlert])
async def get_recent_alerts(limit: int = Query(5, ge=1, le=20, description="조회할 알림 수 (1~20개)"),
                            current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
    """최근 알림 목록 조회"""
    try:
        dashboard_repo = DashboardRepository(db)
        # 최근 알림 조회
        alerts_data = await dashboard_repo.get_recent_alert_notifications(
            user_seq=current_user.user_seq,
            limit=limit)
        
        # 스키마 변환
        result = []
        for alert in alerts_data:
            result.append(RecentAlert(
                alert_seq=alert['alert_seq'],
                device_label=alert['device_label'],
                alert_type=alert['alert_type'],
                alert_message=alert['alert_message'],
                alert_time=alert['alert_time'],
                is_read=alert['is_read'],
                related_detection_seq=alert['related_detection_seq']
            ))
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최근 알림 조회 실패: {str(e)}")
    
@router.get("/hourly-chart", response_model=List[HourlyChartData])
async def get_hourly_detection_chart(
    target_date: Optional[str] = Query(None, description="조회 날짜 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """시간대별 탐지 차트 데이터 조회 (24시간)"""
    try:
        # 날짜 파싱
        parsed_date = None
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)")
            
        # 서비스 생성
        dashboard_repo = DashboardRepository(db)
        detection_repo = DetectionRepository(db)
        dashboard_service = DashboardService(dashboard_repo, detection_repo)
        
        # 차트 데이터 조회
        chart_data = await dashboard_service.get_hourly_detection_chart(user_seq=current_user.user_seq, target_date=parsed_date)
        return chart_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 데이터 조회 실패: {str(e)}")
    
    
# 레커시 api
@router.get("/legacy-overview", response_model=DashboardResponse)
async def get_dashboard_overview_legacy(
    user_ui_language: str = Query("en-US", description="사용자 언어 (ko, en, zh, ja, th, ph)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """레거시 대시보드 api
    - 프론트엔드와 호환성을 위해
    """
    try:
        # 서비스 생성
        dashboard_repo = DashboardRepository(db)
        detection_repo = DetectionRepository(db)
        dashboard_service = DashboardService(dashboard_repo, detection_repo)
        
        # 대시보드 데이터 조회
        complete_data = await dashboard_service.get_comprehensive_dashboard_data(
            user_seq=current_user.user_seq,
            user_language=user_ui_language,
            target_date=None
        )
        # 레거시 형식으로 변환
        legacy_response = DashboardResponse(
            success=True,
            overview=complete_data.overview,
            hourly_chart=complete_data.hourly_chart,
            device_status=[],
            recent_risks=complete_data.recent_detections
        )
        return legacy_response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="대시보드 데이터 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")