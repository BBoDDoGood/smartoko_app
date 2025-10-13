import { Dimensions, StyleSheet } from "react-native";
import { NeutralColors, PrimaryColors, SemanticColors } from "../core/theme/colors";
import { Spacing } from "../core/theme/spacing";

// 화면 크기 정보 가져오기
const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

// 반응형 계산 함수들
const wp = (percentage: number) => screenWidth * (percentage / 100);    //너비 백분율
const hp = (percentage: number) => screenHeight * (percentage / 100);    //높이 백분율
const fs = (size: number) => Math.max(screenWidth * (size / 100), 12);    //폰트 크기 백분율

export const styles = StyleSheet.create({
    // 메인 컨데이터
    container: {
        flex: 1,
        backgroundColor: PrimaryColors.blue50,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: wp(8),
        paddingVertical: hp(5),
    },

    // 헤더 섹션
    headerSection: {
        alignItems: 'center',
        marginBottom: hp(6),
    },

    // 로고
    logo: {
        width: wp(55),
        height: hp(10),
        maxWidth: 280,
        maxHeight: 120,
        minWidth: 150,
        minHeight: 60,
        marginBottom: hp(2),
    },
    
    // 큰 로고 (텍스트 없이 로고만 표시할 때)
    logoLarge: {
        width: wp(70),
        height: hp(15),
        maxWidth: 350,
        maxHeight: 180,
        minWidth: 200,
        minHeight: 100,
        marginBottom: hp(4),
    },
    title: {
        fontSize: fs(6),
        fontWeight: 'bold',
        color: PrimaryColors.blue900,
        textAlign: 'center',
        marginBottom: hp(1),
    },
    subtitle: {
        fontSize: fs(3.8),
        color: PrimaryColors.blue600,
        textAlign: 'center',
    },

    // 폼 섹션
    formSection: {
        width: '100%',
        maxWidth: wp(85) > 400 ? 400 : wp(85),
        minWidth: 280,
    },

    // 언어 선택기 컨테이너
    languageSelectorContainer: {
        marginBottom: hp(3),
    },

    // 입력 폼 컨테이너
    formContainer: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: Spacing.lg,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 5,
    },

    formTitle: {
        fontSize: fs(5),
        fontWeight: '600',
        color: NeutralColors.gray900,
        textAlign: 'center',
        marginBottom: hp(3),
    },

    // 입력 필드
    inputContainer: {
        marginBottom: hp(2),
    },
    inputLabel: {
        fontSize: fs(3.5),
        color: NeutralColors.gray700,
        marginBottom: hp(0.8),
        fontWeight: '500',
    },
    // 입력창
    input: {
        backgroundColor: NeutralColors.gray50,
      borderRadius: 8,
      paddingHorizontal: Spacing.md,
      paddingVertical: hp(2),
      fontSize: fs(4.2),
      borderWidth: 1,
      borderColor: NeutralColors.gray300,
      minHeight: 50,
      color: NeutralColors.gray900,
    },
    inputFocused: {
      borderColor: PrimaryColors.blue500,
      backgroundColor: 'white',
    },
    inputError: {
      borderColor: SemanticColors.danger500,
      backgroundColor: '#FEF2F2',
    },

    // 버튼
    buttonContainer: {
      marginTop: hp(3),
    },
    loginButton: {
      backgroundColor: PrimaryColors.blue600,
      borderRadius: 8,
      paddingVertical: hp(2.2),
      alignItems: 'center',
      minHeight: 52,
      shadowColor: PrimaryColors.blue600,
      shadowOffset: { width: 0, height: 3 },
      shadowOpacity: 0.3,
      shadowRadius: 6,
      elevation: 4,
    },
    loginButtonPressed: {
      backgroundColor: PrimaryColors.blue700,
      transform: [{ scale: 0.98 }],
    },
    loginButtonDisabled: {
      backgroundColor: NeutralColors.gray400,
      shadowOpacity: 0,
      elevation: 0,
    },
    loginButtonText: {
      color: 'white',
      fontSize: fs(4.5),
      fontWeight: '600',
    },

    // 상태 메시지
    messageContainer: {
      minHeight: hp(4),
      justifyContent: 'center',
      marginBottom: hp(2),
    },
    errorText: {
      color: SemanticColors.danger500,
      textAlign: 'center',
      fontSize: fs(3.5),
      paddingHorizontal: wp(2),
      lineHeight: fs(3.5) * 1.4,
      fontWeight: '500',
    },
    loadingText: {
      color: PrimaryColors.blue600,
      textAlign: 'center',
      fontSize: fs(3.5),
      fontStyle: 'italic',
    },

    // 개발자 카드 (개발 환경에서만 표시)
    devCard: {
        position: 'absolute',
        bottom: hp(5),
        left: wp(5),
        right: wp(5),
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderRadius: 8,
        padding: Spacing.md,
        maxWidth: wp(90),
        alignSelf: 'center',
    },
    devCardTitle: {
        color: '#00FF00',
        fontSize: fs(4),
        fontWeight: '600',
        marginBottom: hp(1),
        textAlign: 'center',
    },
    devCardText: {
        color: '#FFFFFF',
        fontSize: fs(3.2),
        marginBottom: hp(0.5),
        fontFamily: 'monospace',
    },

    // Forgot password 링크
    forgotPasswordLink: {
        alignSelf: 'flex-end',
        marginBottom: 16,
    },
    forgotPasswordText: {
        color: '#6B7280',
        fontSize: fs(3.5),
    },

    // Sign up 섹션
    signUpContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginTop: 20,
        alignItems: 'center',
    },
    signUpText: {
        color: '#6B7280',
        fontSize: fs(3.5),
    },
    signUpLink: {
        color: PrimaryColors.blue600,
        fontSize: fs(3.5),
        fontWeight: '600',
    },

    // 저작권 표시
    copyrightText: {
        color: '#9CA3AF',
        fontSize: fs(3),
        marginTop: 40,
        textAlign: 'center',
    },
});