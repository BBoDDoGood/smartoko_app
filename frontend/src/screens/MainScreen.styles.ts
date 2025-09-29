import { StyleSheet } from "react-native";
import { NeutralColors, PrimaryColors, SemanticColors } from "../core/theme/colors";
import { Spacing } from "../core/theme/spacing";

export const mainScreenStyles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: PrimaryColors.blue50,
        alignItems: 'center',
        justifyContent: 'center',
        padding: Spacing.lg,
    },

    // 타이틀 섹션
    titleSection: {
        alignItems: 'center',
        marginBottom: Spacing.xl,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: PrimaryColors.blue900,
        textAlign: 'center',
        marginBottom: Spacing.sm,
    },
    subtitle: {
        fontSize: 16,
        color: PrimaryColors.blue600,
        textAlign: 'center',
    },

    // 사용자 정보 카드
    userInfoCard: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: Spacing.lg,
        marginBottom: Spacing.xl,
        shadowColor: '#000',
        shadowOffset: {
          width: 0,
          height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
        width: '100%',
        maxWidth: 320,
      },
      userInfoHeader: {
        fontSize: 18,
        fontWeight: '600',
        color: PrimaryColors.blue800,
        textAlign: 'center',
        marginBottom: Spacing.md,
      },
      userInfoRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: Spacing.sm,
        borderBottomWidth: 1,
        borderBottomColor: NeutralColors.gray200,
      },
      userInfoRowLast: {
        borderBottomWidth: 0,
      },
      userInfoLabel: {
        fontSize: 14,
        color: NeutralColors.gray600,
        fontWeight: '500',
      },
      userInfoValue: {
        fontSize: 14,
        color: NeutralColors.gray900,
        fontWeight: '400',
        flex: 1,
        textAlign: 'right',
      },
  
      // 버튼 섹션
      buttonSection: {
        width: '100%',
        maxWidth: 320,
      },
      logoutButton: {
        backgroundColor: SemanticColors.danger500,
        paddingHorizontal: Spacing.lg,
        paddingVertical: Spacing.md,
        borderRadius: 8,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: {
          width: 0,
          height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
      },
      logoutButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
      },
  
      // 상태 표시
      statusBadge: {
        paddingHorizontal: Spacing.sm,
        paddingVertical: Spacing.xs,
        borderRadius: 12,
        alignSelf: 'center',
        marginTop: Spacing.sm,
      },
      statusBadgeActive: {
        backgroundColor: SemanticColors.success500,
      },
      statusBadgeText: {
        color: 'white',
        fontSize: 12,
        fontWeight: '600',
      },
    });