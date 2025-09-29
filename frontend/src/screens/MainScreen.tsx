import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { mainScreenStyles as styles } from './MainScreen.styles';

interface User {
    user_seq: number;
    username: string;
    fullname: string | null;
    email: string;
    ai_toggle_yn: 'Y' | 'N';
}

interface MainScreenProps {
    user: User;
    onLogout: () => void;
}

export default function MainScreen({ user, onLogout }: MainScreenProps) {

    return (
        <View style={styles.container}>
            {/* 타이틀 섹션 */}
            <View style={styles.titleSection}>
                <Text style={styles.title}>SmartOkO AI</Text>
                <Text style={styles.subtitle}>모니터링 시스템</Text>
            </View>

            {/* 사용자 정보 카드 */}
            {user && (
                <View style={styles.userInfoCard}>
                    <Text style={styles.userInfoHeader}>
                        환영합니다, {user.fullname || user.username}님!
                    </Text>

                    <View style={styles.userInfoRow}>
                        <Text style={styles.userInfoLabel}>사용자 ID</Text>
                        <Text style={styles.userInfoValue}>{user.username}</Text>
                    </View>

                    <View style={styles.userInfoRow}>
                        <Text style={styles.userInfoLabel}>이메일</Text>
                        <Text style={styles.userInfoValue}>{user.email || '미설정'}</Text>
                    </View>

                    <View style={[styles.userInfoRow, styles.userInfoRowLast]}>
                        <Text style={styles.userInfoLabel}>AI 기능</Text>
                        <Text style={styles.userInfoValue}>
                            {user.ai_toggle_yn === 'Y' ? '활성화' : '비활성화'}
                        </Text>
                    </View>

                    <View style={[styles.statusBadge, styles.statusBadgeActive]}>
                        <Text style={styles.statusBadgeText}>온라인</Text>
                    </View>
                </View>
            )}

            {/* 버튼 섹션 */}
            <View style={styles.buttonSection}>
                <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
                    <Text style={styles.logoutButtonText}>로그아웃</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}