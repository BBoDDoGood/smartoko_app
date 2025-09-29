import { StyleSheet } from "react-native";
import { NeutralColors, PrimaryColors } from "../../core/theme/colors";
import { Spacing } from "../../core/theme/spacing";

export const loadingScreenStyles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: PrimaryColors.blue50,
        alignItems: 'center',
        justifyContent: 'center',
        padding: Spacing.lg,
    },
    text: {
        fontSize: 16,
        color: NeutralColors.gray600,
        textAlign: 'center',
        fontWeight: '500',
    },
    logo: {
        marginBottom: Spacing.md,
    },
})