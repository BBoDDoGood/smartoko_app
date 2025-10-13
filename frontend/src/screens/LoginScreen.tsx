import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, Image, KeyboardAvoidingView, ScrollView, Platform } from 'react-native';
import { useTranslation } from 'react-i18next';
import { styles } from './LoginScreen.styles';
import authService from '../services/authService';
import ScreenLayout from '../components/common/ScreenLayout';
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
            const result = await authService.login({
                username: username.trim(),
                password: password.trim(),
            });

            if (result.success && result.user) {
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
        <ScreenLayout>
            <KeyboardAvoidingView
                style={{ flex: 1 }}
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
            >
                <ScrollView
                    contentContainerStyle={{ justifyContent: 'center', paddingHorizontal: 32, paddingVertical: 40, minHeight: '100%' }}
                    keyboardShouldPersistTaps="handled"
                    showsVerticalScrollIndicator={false}
                    bounces={false}
                >
                    <View style={{ alignItems: 'center', width: '100%' }}>
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
                            <View style={styles.formContainer}>
                                <Text style={styles.formTitle}>{t('login.title')}</Text>

                                {/* 이메일 입력 */}
                                <View style={styles.inputContainer}>
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

                                {/* Forgot password 링크 */}
                                <TouchableOpacity style={styles.forgotPasswordLink}>
                                    <Text style={styles.forgotPasswordText}>
                                        {t('login.forgotPassword')}
                                    </Text>
                                </TouchableOpacity>

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
                                            {isLoading ? t('login.signingIn') : t('login.signInButton')}
                                        </Text>
                                    </TouchableOpacity>
                                </View>

                                {/* Sign up 링크 */}
                                <View style={styles.signUpContainer}>
                                    <Text style={styles.signUpText}>
                                        {t('login.noAccount')}{' '}
                                    </Text>
                                    <TouchableOpacity>
                                        <Text style={styles.signUpLink}>
                                            {t('login.signUpLink')}
                                        </Text>
                                    </TouchableOpacity>
                                </View>
                            </View>
                        </View>

                        {/* © 2025 APEX All Rights Reserved */}
                        <Text style={styles.copyrightText}>
                            © 2025 APEX All Rights Reserved
                        </Text>
                    </View>
                </ScrollView>
            </KeyboardAvoidingView>
        </ScreenLayout>
    );
}