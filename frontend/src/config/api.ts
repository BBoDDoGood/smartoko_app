// src/config/api.ts
// 실무 표준: 환경 변수 기반 API 설정

/**
 * 환경 변수에서 API 설정 가져오기
 * Expo는 EXPO_PUBLIC_ 접두사가 붙은 환경 변수를 자동으로 번들에 포함
 *
 * 사용 방법:
 * 1. 프로젝트 루트에 .env.development, .env.staging, .env.production 파일 생성
 * 2. EXPO_PUBLIC_API_BASE_URL 등의 환경 변수 설정
 * 3. npm run dev (개발), npm run staging (스테이징), npm run prod (프로덕션)
 */

// 환경 변수에서 설정 가져오기 (기본값 포함)
const getEnvVariable = (key: string, defaultValue: string): string => {
  const value = process.env[key];

  if (!value) {
    if (__DEV__) {
      console.warn(`⚠️ 환경 변수 ${key}가 설정되지 않았습니다. 기본값 사용: ${defaultValue}`);
    }
    return defaultValue;
  }

  return value;
};

// 현재 환경 감지
const APP_ENV = getEnvVariable('EXPO_PUBLIC_APP_ENV', 'development');

// API 기본 설정
export const API_CONFIG = {
  // 환경 정보
  ENV: APP_ENV,
  IS_DEV: APP_ENV === 'development',
  IS_STAGING: APP_ENV === 'staging',
  IS_PROD: APP_ENV === 'production',

  // API 설정
  API_BASE_URL: getEnvVariable('EXPO_PUBLIC_API_BASE_URL', 'https://dev.smartoko.com/api'),
  API_VERSION: getEnvVariable('EXPO_PUBLIC_API_VERSION', 'v1'),
  API_TIMEOUT: parseInt(getEnvVariable('EXPO_PUBLIC_API_TIMEOUT', '10000'), 10),

  // 앱 정보
  APP_NAME: getEnvVariable('EXPO_PUBLIC_APP_NAME', 'SmartOkO'),
  APP_VERSION: getEnvVariable('EXPO_PUBLIC_APP_VERSION', '1.0.0'),
};

// API 엔드포인트 정의
export const API_ENDPOINTS = {
  // 인증 관련
  LOGIN: `${API_CONFIG.API_BASE_URL}/auth/login`,
  SIGNUP: `${API_CONFIG.API_BASE_URL}/auth/signup`,
  LOGOUT: `${API_CONFIG.API_BASE_URL}/auth/logout`,

  // 사용자 관련
  USER_INFO: `${API_CONFIG.API_BASE_URL}/user/info`,
  USER_UPDATE: `${API_CONFIG.API_BASE_URL}/user/update`,

  // 대시보드 관련
  DASHBOARD_HEALTH: `${API_CONFIG.API_BASE_URL}/v1/dashboard/health`,
  DASHBOARD_OVERVIEW: `${API_CONFIG.API_BASE_URL}/v1/dashboard/overview`,

  // 로그 관련
  LOGS: `${API_CONFIG.API_BASE_URL}/logs`,
};

// 개발 환경에서만 설정 출력
if (__DEV__) {
  console.log('🔧 API 설정 로드 완료:', {
    환경: API_CONFIG.ENV,
    'API 주소': API_CONFIG.API_BASE_URL,
    '앱 이름': API_CONFIG.APP_NAME,
    '버전': API_CONFIG.APP_VERSION,
    타임아웃: `${API_CONFIG.API_TIMEOUT}ms`,
  });

  console.log('📡 API 엔드포인트:', API_ENDPOINTS);
}

// 타입 정의 (TypeScript 타입 안전성)
export type ApiEndpoint = keyof typeof API_ENDPOINTS;
export type ApiConfig = typeof API_CONFIG;
