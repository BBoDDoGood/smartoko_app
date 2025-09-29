import { Dimensions, PixelRatio, Platform } from 'react-native';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// 기준 디자인 크기
const BASE_WIDTH = 375;
const BASE_HEIGHT = 812;

// 화면 너비 기준 백분율 계산
export const wp = (percentage: number): number => {
    const value = (percentage * SCREEN_WIDTH) / 100;
    return Math.round(PixelRatio.roundToNearestPixel(value));
};

// 화면 높이 기준 백분율 계산
export const hp = (percentage: number): number => {
    const value = (percentage * SCREEN_HEIGHT) / 100;
    return Math.round(PixelRatio.roundToNearestPixel(value))
};

// 폰트 크기 계산
export const fs = (size: number): number => {
    // 화면 크게에 비례한 스케일 계산
    const scale = Math.min(SCREEN_WIDTH / BASE_WIDTH, 1.3);
    const newSize = size * scale;

    // 플랫폼별 최소 폰트 크기 보장
    const minSize = Platform.OS === 'ios' ? 12 : 14;

    // 테블릿에서는 더 큰 폰트 사용
    const maxMultiplier = isTablet() ? 1.4 : 1.2;
    const maxSize = size * maxMultiplier;

    // 최소값, 최대값 사이에서 게산된 크기 반환
    return Math.max(minSize, Math.min(maxSize, Math.round(PixelRatio.roundToNearestPixel(newSize))));
};

// 반응형 간격/ 여백 계산
export const sp = (size: number): number => {
    // 화면 크기 비율 중 더 작은 값 사용
    const scale = Math.min(SCREEN_WIDTH / BASE_WIDTH, SCREEN_HEIGHT / BASE_HEIGHT);
    const newSize = size * scale;
    return Math.round(PixelRatio.roundToNearestPixel(newSize));
};

// 반응형 아이콘 크기 계산
export const iconSize = (size: number): number => {
    if (isTablet()) return Math.round(size * 1.3);
    if (isSmallDevice()) return Math.round(size * 0.9);
    return size;
}

// 터치 영역 최적화
export const touchableSize = (minSize: number = 44): number => {
    return Math.max(minSize, sp(minSize));
};

// 현재 기기가 태블릿인지 확인 -> 테블릿이면 true, 폰이면 false
export const isTablet = (): boolean => {
    // 화면 비율과 크기로 태블릿 판단
    const ratio = SCREEN_HEIGHT / SCREEN_WIDTH;
    const isLargeScreen = SCREEN_WIDTH >= 768;
    const isTabletRatio = Platform.OS === 'ios' ? ratio < 1.6 : ratio < 1.8;

    return isLargeScreen && isTabletRatio;
};

// 현재 기기가 작은 화면인지 확인 -> 작은 폰이면 true
export const isSmallDevice = (): boolean => {
    return SCREEN_WIDTH < 350;
};

// 현재 기기가 큰 화면인지 확인
export const isLargeDevice = (): boolean => {
    return SCREEN_WIDTH > 400 && !isTablet();
};

// 현재 화면 정보 - 디버깅용
export const screenInfo = {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
    isTablet: isTablet(),
    isSmallDevice: isSmallDevice(),
    isLargeDevice: isLargeDevice(),
    pixelRatio: PixelRatio.get(),
    fontScale: PixelRatio.getFontScale(),
    platform: Platform.OS,
}
// 개발 환경일 때만 화면 정보 로그 출력
if (__DEV__) {
    console.log('📱 반응형 화면 정보:', screenInfo);
}


