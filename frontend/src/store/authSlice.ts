import {createSlice, PayloadAction} from '@reduxjs/toolkit';

// 로그인 상태
interface SmartOkOUser {
    user_seq: number;
    username: string;
    fullname: string | null;
    email: string;
    enabled: 0 | 1;
    status: 'A' | 'B' | 'C' | 'D' | 'F';
    ai_toggle_yn: 'Y' | 'N';
}

interface AuthState {
    isLoggedIn: boolean;
    user: SmartOkOUser | null;
    isLoading: boolean;
    error: string | null;
}

const initialState: AuthState = {
    isLoggedIn: false,
    user: null,
    isLoading: false,
    error: null,
};

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        loginStart: (state) => {
            state.isLoading = true;
            state.error = null;
        },

        loginSuccess: (state, action: PayloadAction<SmartOkOUser>) => {
            state.isLoading = false;
            state.isLoggedIn = true;
            state.user = action.payload;
            state.error = null;
        },

        loginFailure: (state, action: PayloadAction<string>) => {
            state.isLoading = false;
            state.isLoggedIn = false;
            state.user = null;
            state.error = action.payload;
        },

        logout: (state) => {
            state.isLoggedIn = false;
            state.user = null;
            state.isLoading = false;
            state.error = null;
        }
    }
});

export const { loginStart, loginSuccess, loginFailure, logout } = authSlice.actions;
export default authSlice.reducer;