import React from 'react';
import { View, StyleSheet, StatusBar } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import LanguageSelector from '../LanguageSelector';

interface ScreenLayoutProps {
  children: React.ReactNode;
  showLanguageSelector?: boolean;  // 언어 선택기 표시 여부 (기본 true)
  backgroundColor?: string;
}

/**
 * 모든 화면에 공통으로 적용되는 레이아웃 컴포넌트
 * - 언어 선택기를 우측 상단에 고정 표시
 */
export default function ScreenLayout({
  children,
  showLanguageSelector = true,
  backgroundColor = '#F5F5F5',
}: ScreenLayoutProps) {
  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor }]} edges={['top', 'left', 'right']}>
      <StatusBar barStyle="dark-content" backgroundColor={backgroundColor} />

      <View style={styles.container}>
        {/* 언어 선택기 - 우측 상단 고정 */}
        {showLanguageSelector && (
          <View style={styles.languageSelectorFixed}>
            <LanguageSelector />
          </View>
        )}

        {/* 화면 내용 */}
        {children}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    flex: 1,
    position: 'relative',
  },
  languageSelectorFixed: {
    position: 'absolute',
    top: 16,
    right: 16,
    zIndex: 1000,
    minWidth: 100,
    maxWidth: 120,
  },
});