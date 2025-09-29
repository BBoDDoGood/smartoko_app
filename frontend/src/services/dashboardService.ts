import { API_CONFIG } from '../config/api';
import { authService } from './authService';
import type { DashboardResponse, DashboardError } from '../types/dashboard';

/**
 * Dashboard API 서비스
 * 백엔드 /api/v1/dashboard/* 엔드포인트와 연동
 */
class DashboardService {
    private readonly baseUrl = `${API_CONFIG.API_BASE_URL}/api/v1/dashboard`;

    /**
     * 대시보드 헬스체크
     * 서버 상태 확인용
     */
    async checkHealth(): Promise<{ status: string; message: string }> {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || '헬스체크 실패');
            }

            console.log('✅ DashboardService: 헬스체크 성공');
            return data;
        } catch (error) {
            console.error('❌ DashboardService: 헬스체크 실패', error);
            throw new Error('대시보드 서버 연결에 실패했습니다.');
        }
    }

    /**
     * 대시보드 전체 데이터 조회
     * - 오늘의 통계 (총 탐지 횟수, 활성 디바이스 수, 위험도별 분포)
     * - 최근 탐지 목록 (최근 10개)
     * - 최근 알림 목록 (최근 10개)
     */
    async getDashboardOverview(userLanguage: string = 'ko-KR'): Promise<DashboardResponse> {
        try {
            // 인증 헤더 가져오기
            const authHeaders = await authService.getAuthHeaders();
            
            if (!authHeaders['Authorization']) {
                throw new Error('인증 토큰이 없습니다. 다시 로그인해주세요.');
            }

            // API 호출
            const response = await fetch(`${this.baseUrl}/overview?user_ui_language=${userLanguage}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...authHeaders,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                // 401 Unauthorized - 토큰 만료 또는 인증 실패
                if (response.status === 401) {
                    throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
                }
                
                // 500 Internal Server Error - 서버 오류
                if (response.status === 500) {
                    throw new Error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
                }

                // 기타 오류
                throw new Error(data.detail || '대시보드 데이터를 불러올 수 없습니다.');
            }

            console.log('✅ DashboardService: 대시보드 데이터 조회 성공', {
                totalDetections: data.today_stats.total_detections,
                recentDetections: data.recent_detections.length,
                recentAlerts: data.recent_alerts.length,
                language: userLanguage
            });

            return data;
        } catch (error) {
            console.error('❌ DashboardService: 대시보드 조회 실패', error);
            
            // 네트워크 연결 오류
            if (error instanceof TypeError && error.message.includes('network')) {
                throw new Error('네트워크 연결을 확인해주세요.');
            }
            
            // 기존 오류 메시지 전달
            if (error instanceof Error) {
                throw error;
            }
            
            // 예상치 못한 오류
            throw new Error('예상치 못한 오류가 발생했습니다. 다시 시도해주세요.');
        }
    }

    /**
     * 대시보드 데이터 새로고침 (풀투리프레시용)
     * 동일한 getDashboardOverview를 호출하지만 캐시 무시
     */
    async refreshDashboard(userLanguage: string = 'ko-KR'): Promise<DashboardResponse> {
        console.log('🔄 DashboardService: 대시보드 새로고침 시작');
        return this.getDashboardOverview(userLanguage);
    }

    /**
     * 탐지 상세 정보 조회 (향후 구현 예정)
     * @param detectionSeq 탐지 결과 시퀀스
     */
    async getDetectionDetail(detectionSeq: number): Promise<any> {
        // TODO: 백엔드에 탐지 상세 API가 추가되면 구현
        throw new Error('탐지 상세 조회 기능은 준비 중입니다.');
    }

    /**
     * 알림 읽음 처리 (향후 구현 예정)
     * @param alertSeq 알림 시퀀스
     */
    async markAlertAsRead(alertSeq: number): Promise<void> {
        // TODO: 백엔드에 알림 읽음 처리 API가 추가되면 구현
        throw new Error('알림 읽음 처리 기능은 준비 중입니다.');
    }
}

// 싱글톤 인스턴스 생성
export const dashboardService = new DashboardService();
export default dashboardService;