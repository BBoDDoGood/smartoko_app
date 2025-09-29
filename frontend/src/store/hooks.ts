import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './index';

// 기본 Redux 도구들 
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// SmartOkO 전용 편의 도구들
export const useAuth = () => useAppSelector((state) => state.auth);
export const useCurrentUser = () => useAppSelector((state) => state.auth.user);
export const useIsLoggedIn = () => useAppSelector((state) => state.auth.isLoggedIn);