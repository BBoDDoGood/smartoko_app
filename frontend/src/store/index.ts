import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import authReducer from './authSlice';
import dashboardReducer from './dashboardSlice';

// Redux Persist 설정 - 앱을 꺼도 로그인 상태 유지
const persistConfig = {
    key: "smartoko-auth",
    storage: AsyncStorage,
    whitelist: ['auth'],
};

// 로그인 정보 앱 재시작 후에도 유지
const persistedAuthReducer = persistReducer(persistConfig, authReducer);

// Redux Store 생성
export const store = configureStore({
    reducer: {
        auth: persistedAuthReducer, // 로그인 관련 상태 관리
        dashboard: dashboardReducer, // 대시보드 관련 상태 관리
    },

    // 미들웨어 설정
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
        serializableCheck: {
            ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE', 'persist/PAUSE', 'persist/PURGE', 'persist/REGISTER'],
        },
    }),
    // 개발자 도구 활성화 - 개발 모드에서만
    devTools: __DEV__,
});

// PersistStore 생성
export const persistor = persistStore(store);

// 타입 정의
export type RootState = ReturnType<typeof store.getState>;  // 전체 상태의 타입
export type AppDispatch = typeof store.dispatch;            // 액션 실행 함수의 타입


  