import * as SecureStore from 'expo-secure-store';
import { API_ENDPOINTS } from '../config/api';

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  message: string;  // 에러 코드 (USER_NOT_FOUND, ACCOUNT_DISABLED 등)
  error_data?: { count?: number; current?: number; remaining?: number };  // 에러 관련 추가 데이터
  user?: {
    user_seq: number;
    username: string;
    fullname: string | null;
    email: string;
    phone: string | null;
    enabled: string;  // "0" or "1"
    status: string;   // "A", "B", "C", "D", "F"
    status_msg: string | null;
    password_wrong_cnt: number;
    group_limit: number;
    device_limit: number;
    alarm_yn: string | null;
    alarm_line_yn: string | null;
    alarm_whatsapp_yn: string | null;
    ai_status: string | null;
    ai_toggle_yn: string | null;
    last_access_dt: string | null;
    reg_dt: string | null;
  };
  access_token?: string;
  session_token?: string;
  session_id?: string;
  token_type?: string;
  expires_in?: number;
}

interface SignUpData {
  username: string;
  password: string;
  fullname?: string;
  email?: string;
  phone?: string;
}

interface SignUpResponse {
  success: boolean;
  message: string;
  user_seq?: number;
}

interface AuthTokens {
  access_token?: string;
  session_token?: string;
  session_id?: string;
}

class AuthService {
  /**
   * 회원가입 요청
   */
  async signUp(data: SignUpData): Promise<SignUpResponse> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10초 타임아웃

    try {
      const response = await fetch(API_ENDPOINTS.SIGNUP, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const result = await response.json();

      if (response.ok && result.success) {
        console.log('✅ AuthService: 회원가입 성공');
        return result;
      } else {
        return {
          success: false,
          message: result.message || '회원가입에 실패했습니다.',
        };
      }
    } catch (error: any) {
      clearTimeout(timeoutId);
      console.error('❌ AuthService: 회원가입 오류', error);

      // 타임아웃 에러
      if (error.name === 'AbortError') {
        throw new Error('서버 응답 시간이 초과되었습니다.\n네트워크 상태를 확인하거나 잠시 후 다시 시도해주세요.');
      }

      // 네트워크 에러
      if (error.message.includes('Network request failed')) {
        throw new Error('서버에 연결할 수 없습니다.\n네트워크 연결을 확인해주세요.');
      }

      // 기타 에러
      throw new Error('회원가입 중 오류가 발생했습니다.\n잠시 후 다시 시도해주세요.');
    }
  }

  /**
   * 로그인 요청
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10초 타임아웃

    try {
      const response = await fetch(API_ENDPOINTS.LOGIN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (response.ok && data.success) {
        // 백엔드가 반환하는 데이터 구조:
        // { success, message, user: {...}, access_token, token_type, expires_in }

        // 토큰들을 SecureStore에 저장
        await this.saveTokens({
          access_token: data.access_token,
          session_token: data.session_token,
          session_id: data.session_id,
        });

        // 백엔드에서 받은 실제 사용자 정보 저장
        if (data.user) {
          await SecureStore.setItemAsync('user_data', JSON.stringify(data.user));
        }

        console.log('✅ AuthService: 로그인 및 토큰 저장 완료');

        // 백엔드 응답을 그대로 반환
        return data;
      } else {
        // 서버에서 실패 응답을 보낸 경우
        return {
          success: false,
          message: data.message || '로그인에 실패했습니다.',
          error_data: data.error_data,  // 🔥 에러 추가 데이터 전달 (비밀번호 틀린 횟수 등)
        };
      }
    } catch (error: any) {
      clearTimeout(timeoutId);
      console.error('❌ AuthService: 로그인 오류', error);

      // 타임아웃 에러
      if (error.name === 'AbortError') {
        throw new Error('서버 응답 시간이 초과되었습니다.\n네트워크 상태를 확인하거나 잠시 후 다시 시도해주세요.');
      }

      // 네트워크 에러
      if (error.message.includes('Network request failed')) {
        throw new Error('서버에 연결할 수 없습니다.\n- Wi-Fi 또는 모바일 데이터 연결을 확인해주세요.\n- 백엔드 서버가 실행 중인지 확인해주세요.');
      }

      // 기타 에러
      throw new Error('로그인 중 오류가 발생했습니다.\n잠시 후 다시 시도해주세요.');
    }
  }

  /**
   * 토큰들을 SecureStore에 저장
   */
  async saveTokens(tokens: AuthTokens): Promise<void> {
    try {
      if (tokens.access_token) {
        await SecureStore.setItemAsync('access_token', tokens.access_token);
      }
      if (tokens.session_token) {
        await SecureStore.setItemAsync('session_token', tokens.session_token);
      }
      if (tokens.session_id) {
        await SecureStore.setItemAsync('session_id', tokens.session_id);
      }
    } catch (error) {
      console.error('❌ AuthService: 토큰 저장 실패', error);
      throw error;
    }
  }

  /**
   * 저장된 토큰들 가져오기
   */
  async getTokens(): Promise<AuthTokens> {
    try {
      const [access_token, session_token, session_id] = await Promise.all([
        SecureStore.getItemAsync('access_token'),
        SecureStore.getItemAsync('session_token'),
        SecureStore.getItemAsync('session_id'),
      ]);

      return {
        access_token: access_token || undefined,
        session_token: session_token || undefined,
        session_id: session_id || undefined,
      };
    } catch (error) {
      console.error('❌ AuthService: 토큰 조회 실패', error);
      return {};
    }
  }

  /**
   * 저장된 사용자 정보 가져오기
   */
  async getUserData(): Promise<any> {
    try {
      const userData = await SecureStore.getItemAsync('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('❌ AuthService: 사용자 데이터 조회 실패', error);
      return null;
    }
  }

  /**
   * 로그아웃 (토큰 및 사용자 데이터 삭제)
   */
  async logout(): Promise<void> {
    try {
      await Promise.all([
        SecureStore.deleteItemAsync('access_token'),
        SecureStore.deleteItemAsync('session_token'),
        SecureStore.deleteItemAsync('session_id'),
        SecureStore.deleteItemAsync('user_data'),
      ]);
      console.log('✅ AuthService: 로그아웃 완료');
    } catch (error) {
      console.error('❌ AuthService: 로그아웃 실패', error);
      throw error;
    }
  }

  /**
   * 인증 헤더 생성 (JWT + 세션 토큰)
   */
  async getAuthHeaders(): Promise<Record<string, string>> {
    const tokens = await this.getTokens();
    const headers: Record<string, string> = {};

    if (tokens.access_token) {
      headers['Authorization'] = `Bearer ${tokens.access_token}`;
    }

    if (tokens.session_token) {
      headers['X-Session-Token'] = tokens.session_token;
    }

    if (tokens.session_id) {
      headers['X-Session-ID'] = tokens.session_id;
    }

    return headers;
  }

  /**
   * 로그인 상태 확인
   */
  async isLoggedIn(): Promise<boolean> {
    const tokens = await this.getTokens();
    return !!(tokens.access_token || tokens.session_token);
  }
}

export const authService = new AuthService();
export default authService;