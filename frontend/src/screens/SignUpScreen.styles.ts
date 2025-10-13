import { StyleSheet, Dimensions } from 'react-native';
import { PrimaryColors } from '../core/theme/colors';

const { width: screenWidth } = Dimensions.get('window');

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },

  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 40,
  },

  // 뒤로가기 버튼
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },

  backButtonText: {
    fontSize: 24,
    color: '#333',
  },

  // 로고
  logoContainer: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 30,
  },

  logo: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1E3A8A', // 다크 블루
    letterSpacing: 2,
  },

  // 제목
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
    marginBottom: 30,
  },

  // 폼
  formContainer: {
    width: '100%',
  },

  // 섹션 제목 (Mandatory Fields, Optional Fields)
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 12,
    marginTop: 8,
  },

  // 입력 필드
  input: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: '#333',
    marginBottom: 12,
  },

  // 비밀번호 입력 (눈 아이콘 포함)
  passwordContainer: {
    position: 'relative',
    marginBottom: 12,
  },

  passwordInput: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 14,
    paddingRight: 50, // 눈 아이콘 공간
    fontSize: 16,
    color: '#333',
  },

  eyeIcon: {
    position: 'absolute',
    right: 12,
    top: 12,
    padding: 8,
  },

  eyeIconText: {
    fontSize: 18,
  },

  // 에러 메시지
  errorContainer: {
    backgroundColor: '#FEE2E2',
    borderLeftWidth: 4,
    borderLeftColor: '#DC2626',
    borderRadius: 4,
    padding: 12,
    marginBottom: 16,
  },

  errorText: {
    color: '#991B1B',
    fontSize: 14,
  },

  // 약관 동의 체크박스
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 24,
  },

  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    borderRadius: 4,
    marginRight: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },

  checkboxChecked: {
    backgroundColor: PrimaryColors.blue600,
    borderColor: PrimaryColors.blue600,
  },

  checkboxIcon: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },

  checkboxLabel: {
    flex: 1,
    fontSize: 14,
    color: '#666',
  },

  // 회원가입 버튼
  signUpButton: {
    backgroundColor: PrimaryColors.blue600,
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 54,
  },

  signUpButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },

  buttonDisabled: {
    backgroundColor: '#9CA3AF',
    opacity: 0.7,
  },
});
