// src/core/theme/spacing.ts

export const Spacing = {
  xs: 4,    // 아주 작은 간격
  sm: 8,    // 작은 간격
  md: 16,   // 중간 간격 (기본)
  lg: 24,   // 큰 간격
  xl: 32,   // 아주 큰 간격
  xxl: 40,  // 매우 큰 간격
  xxxl: 48, // 가장 큰 간격
} as const;

export const ComponentSpacing = {
  // 컴포넌트 내부 여백
  buttonPaddingVertical: Spacing.md,
  buttonPaddingHorizontal: Spacing.lg,
  
  cardPadding: Spacing.md,
  cardMargin: Spacing.md,
  
  screenPadding: Spacing.md,
  sectionMargin: Spacing.lg,
  
  // 리스트 아이템 간격
  listItemSpacing: Spacing.md,
  listSectionSpacing: Spacing.lg,
  
  // 입력 필드
  inputPadding: Spacing.md,
  inputMargin: Spacing.sm,
  
  // 아이콘
  iconSpacing: Spacing.sm,
  iconPadding: Spacing.xs,
} as const;

export const BorderRadius = {
  small: 4,    // 작은 radius
  medium: 8,   // 중간 radius (기본)
  large: 12,   // 큰 radius
  xl: 16,      // 아주 큰 radius
  round: 50,   // 원형
} as const;