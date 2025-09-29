// Dashboard API 응답 타입 정의 (백엔드 schemas/dashboard.py와 일치)

// 오늘의 통계 데이터
export interface TodayStats {
    total_detections: number;
    devices_active: number;
    risk_distribution: Record<string, number>; // 위험도별 분포 (critical, high, medium, low 등)
}

// 최근 탐지 결과 데이터
export interface RecentDetection {
    detection_seq: number;
    thumbnail_url: string | null;
    danger_level: string;
    detection_class: string;
    device_label: string;
    detection_at: string; // ISO datetime 문자열
    confidence: number; // 0.0 ~ 1.0
}

// 최근 AI 알림 데이터
export interface RecentAlert {
    alert_seq: number;
    detection_seq: number;
    alert_type: string;
    ai_detection_guide: string;
    language_code: string;
    user_model_name: string | null;
    is_read: boolean;
    reg_dt: string; // ISO datetime 문자열
    read_dt: string | null; // ISO datetime 문자열 또는 null
}

// 대시보드 전체 응답 데이터
export interface DashboardResponse {
    today_stats: TodayStats;
    recent_detections: RecentDetection[];
    recent_alerts: RecentAlert[];
}

// 위험도 레벨 enum (백엔드와 일치)
export enum DangerLevel {
    CRITICAL = 'critical',
    HIGH = 'high',
    MEDIUM = 'medium',
    LOW = 'low',
    SAFE = 'safe',
    NORMAL = 'normal'
}

// 위험도별 색상 매핑
export const DANGER_LEVEL_COLORS: Record<string, string> = {
    [DangerLevel.CRITICAL]: '#FF0000', // 빨강
    [DangerLevel.HIGH]: '#FF4500',     // 주황빨강
    [DangerLevel.MEDIUM]: '#FFA500',   // 주황
    [DangerLevel.LOW]: '#FFFF00',      // 노랑
    [DangerLevel.SAFE]: '#00FF00',     // 초록
    [DangerLevel.NORMAL]: '#808080'    // 회색
};

// API 에러 응답 타입
export interface DashboardError {
    detail: string;
    status_code: number;
}

// 대시보드 로딩 상태 관리
export interface DashboardState {
    data: DashboardResponse | null;
    isLoading: boolean;
    error: string | null;
    lastUpdated: string | null;
}