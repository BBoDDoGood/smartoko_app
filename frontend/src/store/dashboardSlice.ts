import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { DashboardResponse, DashboardState } from '../types/dashboard';
import { dashboardService } from '../services/dashboardService';

// 대시보드 데이터 조회 비동기 액션
export const fetchDashboardData = createAsyncThunk(
    'dashboard/fetchData',
    async (userLanguage: string = 'ko-KR', { rejectWithValue }) => {
        try {
            const data = await dashboardService.getDashboardOverview(userLanguage);
            return data;
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : '대시보드 조회 실패');
        }
    }
);

// 대시보드 새로고침 비동기 액션
export const refreshDashboard = createAsyncThunk(
    'dashboard/refresh',
    async (userLanguage: string = 'ko-KR', { rejectWithValue }) => {
        try {
            const data = await dashboardService.refreshDashboard(userLanguage);
            return data;
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : '새로고침 실패');
        }
    }
);

const initialState: DashboardState = {
    data: null,
    isLoading: false,
    error: null,
    lastUpdated: null,
};

const dashboardSlice = createSlice({
    name: 'dashboard',
    initialState,
    reducers: {
        clearError: (state) => {
            state.error = null;
        },
        clearDashboard: (state) => {
            state.data = null;
            state.error = null;
            state.lastUpdated = null;
        },
    },
    extraReducers: (builder) => {
        builder
            // fetchDashboardData 액션
            .addCase(fetchDashboardData.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(fetchDashboardData.fulfilled, (state, action: PayloadAction<DashboardResponse>) => {
                state.isLoading = false;
                state.data = action.payload;
                state.error = null;
                state.lastUpdated = new Date().toISOString();
            })
            .addCase(fetchDashboardData.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
            })
            
            // refreshDashboard 액션
            .addCase(refreshDashboard.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(refreshDashboard.fulfilled, (state, action: PayloadAction<DashboardResponse>) => {
                state.isLoading = false;
                state.data = action.payload;
                state.error = null;
                state.lastUpdated = new Date().toISOString();
            })
            .addCase(refreshDashboard.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
            });
    },
});

export const { clearError, clearDashboard } = dashboardSlice.actions;
export default dashboardSlice.reducer;