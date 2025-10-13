// src/core/theme/colors.ts

export const PrimaryColors = {
  // Main Blue Palette (Navy Blue Theme)
  blue50: '#E3F2FD',
  blue100: '#BBDEFB',
  blue200: '#90CAF9',
  blue300: '#64B5F6',
  blue400: '#42A5F5',
  blue500: '#2196F3',  // Main brand color
  blue600: '#1E3A8A',  // 진한 남색 (Navy Blue) - 버튼 기본 색상
  blue700: '#1E40AF',  // 약간 밝은 남색 - 버튼 눌렀을 때
  blue800: '#1E3A70',  // 더 진한 남색
  blue900: '#0D1B3E',  // 가장 진한 남색
} as const;

export const SemanticColors = {
  // Success (안전)
  success50: '#E8F5E8',
  success500: '#4CAF50',
  success700: '#388E3C',
  
  // Warning (주의)
  warning50: '#FFF3E0',
  warning500: '#FF9800', 
  warning700: '#F57C00',
  
  // Danger (위험)
  danger50: '#FFEBEE',
  danger500: '#F44336',
  danger700: '#D32F2F',
  
  // Info (정보)
  info50: '#E1F5FE',
  info500: '#03A9F4',
  info700: '#0277BD',
  
  // Critical (치명적)
  critical50: '#FCE4EC',
  critical500: '#E91E63',
  critical700: '#AD1457',
} as const;

export const NeutralColors = {
  // Gray Scale
  gray50: '#FAFAFA',
  gray100: '#F5F5F5',
  gray200: '#EEEEEE',
  gray300: '#E0E0E0',
  gray400: '#BDBDBD',
  gray500: '#9E9E9E',
  gray600: '#757575',
  gray700: '#616161',
  gray800: '#424242',
  gray900: '#212121',
  
  // Pure Colors
  white: '#FFFFFF',
  black: '#000000',
} as const;

// 위험도별 색상 매핑
export const RiskLevelColors = {
  safe: SemanticColors.success500,
  low: PrimaryColors.blue400,
  medium: SemanticColors.warning500,
  high: SemanticColors.danger500,
  critical: SemanticColors.critical500,
} as const;