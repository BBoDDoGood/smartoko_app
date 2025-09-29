import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, Image } from 'react-native';
import { useTranslation } from 'react-i18next';
import { styles } from './LoginScreen.styles';
import authService from '../services/authService';
import LanguageSelector from '../components/LanguageSelector';
import '../i18n';

interface User {
    user_seq: number;
    username: string;
    fullname: string | null;
    email: string;
    ai_toggle_yn: 'Y' | 'N';
}

interface LoginScreenProps {
    onLoginSuccess: (user: User) => void;
}

export default function LoginScreen({ onLoginSuccess }: LoginScreenProps) {
    const { t } = useTranslation();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async () => {
        if (!username.trim() || !password.trim()) {
            Alert.alert(t('login.error'), t('login.loginRequired'));
            return;
        }

        setIsLoading(true);
        try {
            // AuthService를 통한 로그인
            const result = await authService.login({
                username: username.trim(),
                password: password.trim(),
            });

            if (result.success && result.user) {
                // 즉시 메인 페이지로 이동 (Alert 없이)
                console.log('✅ 로그인 성공:', result.user.username);
                onLoginSuccess(result.user);
            } else {
                Alert.alert(t('login.loginFailed'), result.message || t('login.loginFailedMessage'));
            }
        } catch (error: any) {
            Alert.alert(t('login.error'), error.message || t('login.serverError'));
            console.error('❌ 로그인 오류:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            {/* 헤더 섹션 */}
            <View style={styles.headerSection}>
                <Image 
                    source={require('../../assets/images/smartoko_logo_dark.png')}
                    style={styles.logoLarge}
                    resizeMode="contain"
                />
            </View>

            {/* 폼 섹션 */}
            <View style={styles.formSection}>
                {/* 언어 선택 */}
                <View style={styles.languageSelectorContainer}>
                    <LanguageSelector />
                </View>
                
                <View style={styles.formContainer}>
                    <Text style={styles.formTitle}>{t('login.title')}</Text>

                    {/* 이메일 입력 */}
                    <View style={styles.inputContainer}>
                        <Text style={styles.inputLabel}>{t('login.email')}</Text>
                        <TextInput
                            style={styles.input}
                            value={username}
                            onChangeText={setUsername}
                            placeholder={t('login.emailPlaceholder')}
                            autoCapitalize="none"
                            autoCorrect={false}
                            keyboardType="email-address"
                        />
                    </View>

                    {/* 비밀번호 입력 */}
                    <View style={styles.inputContainer}>
                        <Text style={styles.inputLabel}>{t('login.password')}</Text>
                        <TextInput
                            style={styles.input}
                            value={password}
                            onChangeText={setPassword}
                            placeholder={t('login.passwordPlaceholder')}
                            secureTextEntry
                            autoCapitalize="none"
                            autoCorrect={false}
                        />
                    </View>

                    {/* 로딩 메시지 */}
                    {isLoading && (
                        <View style={styles.messageContainer}>
                            <Text style={styles.loadingText}>{t('login.loggingIn')}</Text>
                        </View>
                    )}

                    {/* 로그인 버튼 */}
                    <View style={styles.buttonContainer}>
                        <TouchableOpacity
                            style={[
                                styles.loginButton,
                                isLoading && styles.loginButtonDisabled
                            ]}
                            onPress={handleLogin}
                            disabled={isLoading}
                        >
                            <Text style={styles.loginButtonText}>
                                {isLoading ? t('login.loggingIn') : t('login.loginButton')}
                            </Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </View>

        </View>
    );
}