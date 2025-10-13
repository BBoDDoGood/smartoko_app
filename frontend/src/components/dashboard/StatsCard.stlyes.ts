import { StyleSheet } from "react-native";

export const StatsCardStyles = StyleSheet.create({
    container: {
        backgroundColor: '#FFFFFF',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    title: {
        fontSize: 14,
        color: '#666',
        marginBottom: 8,
    },
    value: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#2196F3',
    }
})