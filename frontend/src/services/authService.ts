import * as SecureStore from 'expo-secure-store';
import { API_ENDPOINTS } from '../config/api';

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  message: string;
  user?: {
    user_seq: number;
    username: string;
    fullname: string | null;
    email: string;
    ai_toggle_yn: 'Y' | 'N';
  };
  access_token?: string;
  session_token?: string;
  session_id?: string;
  token_type?: string;
  expires_in?: number;
}

interface AuthTokens {
  access_token?: string;
  session_token?: string;
  session_id?: string;
}

class AuthService {
  /**
   * 로그인 요청
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await fetch(API_ENDPOINTS.LOGIN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // 토큰들을 SecureStore에 저장
        await this.saveTokens({
          access_token: data.access_token,
          session_token: data.session_token,
          session_id: data.session_id,
        });

        // 사용자 정보도 저장
        if (data.user) {
          await SecureStore.setItemAsync('user_data', JSON.stringify(data.user));
        }

        console.log('✅ AuthService: 로그인 및 토큰 저장 완료');
      }

      return data;
    } catch (error) {
      console.error('❌ AuthService: 로그인 오류', error);
      throw new Error('서버 연결에 실패했습니다. 네트워크를 확인해주세요.');
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