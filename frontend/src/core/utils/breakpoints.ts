import { Dimensions } from "react-native";

const { width } = Dimensions.get('window');

// 실제 기기별 중단점 정의
export const Breakpoints = {
    xs: 0,  //
    sm: 376,
    md: 391,
    lg: 429,
    tablet: 768,
} as const;

// 화면 크기가 어떤 중단점에 해당하는지 판단
export const getCurrentBreakpoint = (): keyof typeof Breakpoints => {
    if (width >= Breakpoints.tablet) return 'tablet';
    if (width >= Breakpoints.lg) return 'lg';
    if (width >= Breakpoints.md) return 'md';
    if (width >= Breakpoints.sm) return 'sm';
    return 'xs';
};

// 화면 크기에 따라 적절한 값을 선택하는 함수
export const responsive = <T>(values: Partial<Record<keyof typeof Breakpoints, T>>): T => {
    const current = getCurrentBreakpoint();

    // 현재 크기부터 작은 크기 순서로 값을 찾기
    const order: (keyof typeof Breakpoints)[] = ['tablet', 'lg', 'md', 'sm', 'xs'];
    const currentIndex = order.indexOf(current);

    // 현재 중단점부터 작은 중단점 순서로 값 있는지 확인
    for (let i = currentIndex; i < order.length; i++) {
        const breakpoint = order[i];
        if (values[breakpoint] !== undefined) {
            return values[breakpoint] as T;
        }
    }

    // 아무 값도 못 찾으면 첫 번쨰로 정의된 값 반환
    return Object.values(values)[0] as T;
};

/// 현재 화면이 테블릿인지 확인하는 함수
export const isTablet = (): boolean => {
    return getCurrentBreakpoint() === 'tablet';
};

// 현재 화면이 작은 폰인지 확인하는 함수
export const isSmallPhone = (): boolean => {
    const current = getCurrentBreakpoint();
    return current === 'xs' || current === 'sm';
};
