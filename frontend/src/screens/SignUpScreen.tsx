import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { styles } from './SignUpScreen.styles';
import ScreenLayout from '../components/common/ScreenLayout';
import { authService } from '../services/authService';

interface SignUpScreenProps {
  navigation?: any;
}

export default function SignUpScreen({ navigation }: SignUpScreenProps) {
  const { t } = useTranslation();

  // ============================================
  // 상태 관리 (State Management)
  // ============================================

  // 필수 필드
  const [email, setEmail] = useState('');                          // username으로 사용
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // 선택 필드
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');

  // UI 상태
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // ============================================
  // 유효성 검증 함수들
  // ============================================

  // 이메일 형식 검증
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // 비밀번호 강도 검증 (최소 8자)
  const validatePassword = (password: string): boolean => {
    return password.length >= 8;
  };

  // 전화번호 검증 (숫자만, 10-16자리)
  const validatePhone = (phone: string): boolean => {
    if (!phone) return true; // 선택 필드이므로 빈 값 허용
    const phoneRegex = /^\d{10,16}$/;
    return phoneRegex.test(phone);
  };

  // ============================================
  // 전화번호 입력 핸들러 (숫자만 허용)
  // ============================================
  const handlePhoneChange = (text: string) => {
    const numbers = text.replace(/[^\d]/g, '');
    setPhone(numbers.slice(0, 16));
  };

  // ============================================
  // 회원가입 처리
  // ============================================
  const handleSignUp = async () => {
    // 필수 필드 검증
    if (!email || !password || !confirmPassword) {
      setErrorMessage(t('signup.fillRequired') || '필수 항목을 모두 입력하세요.');
      return;
    }

    // 이메일 형식 검증
    if (!validateEmail(email)) {
      setErrorMessage(t('signup.invalidEmail') || '올바른 이메일 주소를 입력하세요.');
      return;
    }

    // 비밀번호 일치 확인
    if (password !== confirmPassword) {
      setErrorMessage(t('signup.passwordMismatch') || '비밀번호가 일치하지 않습니다.');
      return;
    }

    // 비밀번호 강도 검증
    if (!validatePassword(password)) {
      setErrorMessage(t('signup.weakPassword') || '비밀번호는 최소 8자 이상이어야 합니다.');
      return;
    }

    // 전화번호 검증 (입력된 경우만)
    if (phone && !validatePhone(phone)) {
      setErrorMessage(t('signup.invalidPhone') || '전화번호는 10-16자리 숫자만 입력 가능합니다.');
      return;
    }

    // 약관 동의 확인
    if (!agreeToTerms) {
      setErrorMessage(t('signup.agreeTerms') || '이용 약관에 동의해주세요.');
      return;
    }

    setIsLoading(true);
    setErrorMessage('');

    try {
      // fullname 생성 (firstName + lastName)
      const fullname = `${firstName} ${lastName}`.trim() || undefined;

      // API 호출
      const response = await authService.signUp({
        username: email,     // 이메일을 username으로 사용
        password,
        fullname,            // 선택 (firstName + lastName)
        email: email,        // email 필드에도 저장
        phone: phone || undefined  // 선택
      });

      if (response.success) {
        Alert.alert(
          t('signup.success') || '회원가입 완료',
          t('signup.successMessage') || '회원가입이 완료되었습니다.',
          [
            {
              text: t('common.ok') || '확인',
              onPress: () => navigation?.goBack() // 로그인 화면으로 돌아가기
            }
          ]
        );
      } else {
        setErrorMessage(response.message || t('signup.error'));
      }
    } catch (error: any) {
      console.error('회원가입 오류:', error);
      setErrorMessage(error.message || t('signup.error') || '회원가입 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================
  // UI 렌더링
  // ============================================
  return (
    <ScreenLayout backgroundColor="#FFFFFF">
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* 뒤로가기 버튼 */}
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation?.goBack()}
          >
            <Text style={styles.backButtonText}>←</Text>
          </TouchableOpacity>

        {/* 로고 */}
        <View style={styles.logoContainer}>
          <Text style={styles.logo}>SMARTOKO</Text>
        </View>

        {/* 제목 */}
        <Text style={styles.title}>{t('signup.title') || 'Create a new account'}</Text>

        {/* 폼 */}
        <View style={styles.formContainer}>
          {/* 필수 필드 섹션 */}
          <Text style={styles.sectionTitle}>{t('signup.mandatoryFields') || 'Mandatory Fields'}</Text>

          {/* Email */}
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            placeholder={t('signup.emailPlaceholder') || 'Email'}
            placeholderTextColor="#999"
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="email-address"
          />

          {/* Password */}
          <View style={styles.passwordContainer}>
            <TextInput
              style={styles.passwordInput}
              value={password}
              onChangeText={setPassword}
              placeholder={t('signup.passwordPlaceholder') || 'Password'}
              placeholderTextColor="#999"
              secureTextEntry={!showPassword}
              autoCapitalize="none"
            />
            <TouchableOpacity
              style={styles.eyeIcon}
              onPress={() => setShowPassword(!showPassword)}
            >
              <Text style={styles.eyeIconText}>{showPassword ? '👁️' : '👁️‍🗨️'}</Text>
            </TouchableOpacity>
          </View>

          {/* Repeat Password */}
          <View style={styles.passwordContainer}>
            <TextInput
              style={styles.passwordInput}
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              placeholder={t('signup.repeatPasswordPlaceholder') || 'Repeat the Password'}
              placeholderTextColor="#999"
              secureTextEntry={!showConfirmPassword}
              autoCapitalize="none"
            />
            <TouchableOpacity
              style={styles.eyeIcon}
              onPress={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              <Text style={styles.eyeIconText}>{showConfirmPassword ? '👁️' : '👁️‍🗨️'}</Text>
            </TouchableOpacity>
          </View>

          {/* 선택 필드 섹션 */}
          <Text style={styles.sectionTitle}>{t('signup.optionalFields') || 'Optional Fields'}</Text>

          {/* First Name */}
          <TextInput
            style={styles.input}
            value={firstName}
            onChangeText={setFirstName}
            placeholder={t('signup.firstNamePlaceholder') || 'First Name'}
            placeholderTextColor="#999"
          />

          {/* Last Name */}
          <TextInput
            style={styles.input}
            value={lastName}
            onChangeText={setLastName}
            placeholder={t('signup.lastNamePlaceholder') || 'Last Name'}
            placeholderTextColor="#999"
          />

          {/* Phone */}
          <TextInput
            style={styles.input}
            value={phone}
            onChangeText={handlePhoneChange}
            placeholder={t('signup.phonePlaceholder') || 'Phone Number'}
            placeholderTextColor="#999"
            keyboardType="phone-pad"
            maxLength={16}
          />

          {/* 에러 메시지 */}
          {errorMessage ? (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{errorMessage}</Text>
            </View>
          ) : null}

          {/* 약관 동의 */}
          <TouchableOpacity
            style={styles.checkboxContainer}
            onPress={() => setAgreeToTerms(!agreeToTerms)}
          >
            <View style={[styles.checkbox, agreeToTerms && styles.checkboxChecked]}>
              {agreeToTerms && <Text style={styles.checkboxIcon}>✓</Text>}
            </View>
            <Text style={styles.checkboxLabel}>
              {t('signup.agreeTermsLabel') || 'I Agree and Create My Account'}
            </Text>
          </TouchableOpacity>

          {/* 회원가입 버튼 */}
          <TouchableOpacity
            style={[styles.signUpButton, isLoading && styles.buttonDisabled]}
            onPress={handleSignUp}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.signUpButtonText}>
                {t('signup.signUpButton') || 'Sign Up'}
              </Text>
            )}
          </TouchableOpacity>
        </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenLayout>
  );
}
