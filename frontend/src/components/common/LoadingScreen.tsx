import React from "react";
import { Text, View } from "react-native";
import { loadingScreenStyles as styles } from "./LoadingScreen.styles";

export function LoadingScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.text}>SmartOkO 로딩 중...</Text>
        </View>
    );
}