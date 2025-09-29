import { Platform } from 'react-native';
import Constants from 'expo-constants';

/**
 * API 환경별 설정
 * 개발자마다 다른 환경에서 작업할 수 있도록 자동 설정
 */

// 개발 환경에서 사용할 기본 설정
const DEV_CONFIG = {
  // 로컬 개발 서버 (안드로이드 에뮬레이터용)
  API_BASE_URL: 'http://10.0.2.2:8000',  // 안드로이드 에뮬레이터에서 localhost 접근
  
  // iOS 시뮬레이터나 실제 기기 테스트용
  // API_BASE_URL: 'http://localhost:8000',  
};

// 스테이징 환경 설정
const STAGING_CONFIG = {
  API_BASE_URL: 'https://staging-api.smartoko.com',
};

// 프로덕션 환경 설정
const PRODUCTION_CONFIG = {
  API_BASE_URL: 'https://api.smartoko.com',
};

// 현재 환경 감지
const getEnvironment = () => {
  // 환경 변수 우선 확인 (EXPO_PUBLIC_ENV)
  const envFromVariable = process.env.EXPO_PUBLIC_ENV;
  if (envFromVariable) {
    return envFromVariable;
  }
  
  if (__DEV__) {
    return 'development';
  }
  
  // Expo build 시 환경 변수로 구분
  const buildVariant = Constants.expoConfig?.extra?.buildVariant;
  
  if (buildVariant === 'staging') {
    return 'staging';
  }
  
  return 'production';
};

// 환경별 설정 반환
const getConfig = () => {
  const environment = getEnvironment();
  
  switch (environment) {
    case 'development':
      return DEV_CONFIG;
    case 'staging':
      return STAGING_CONFIG;
    case 'production':
      return PRODUCTION_CONFIG;
    default:
      return DEV_CONFIG;
  }
};

export const API_CONFIG = getConfig();

// API 엔드포인트들
export const API_ENDPOINTS = {
  LOGIN: `${API_CONFIG.API_BASE_URL}/api/auth/login/app`,
  LOGOUT: `${API_CONFIG.API_BASE_URL}/api/auth/logout`,
  USER_INFO: `${API_CONFIG.API_BASE_URL}/api/user/info`,
  LOGS: `${API_CONFIG.API_BASE_URL}/api/logs`,
  
  // Dashboard API 엔드포인트
  DASHBOARD_HEALTH: `${API_CONFIG.API_BASE_URL}/api/v1/dashboard/health`,
  DASHBOARD_OVERVIEW: `${API_CONFIG.API_BASE_URL}/api/v1/dashboard/overview`,
};

// 개발자 카드 표시 (개발 환경에서만)
export const SHOW_DEV_CARD = __DEV__;

// 현재 설정 로깅 (개발 환경에서만)
if (__DEV__) {
  console.log('🔧 SmartOkO API 설정:', {
    environment: getEnvironment(),
    baseUrl: API_CONFIG.API_BASE_URL,
    expotHostUri: Constants.expoConfig?.hostUri,
    platform: Platform.OS,
  });
}