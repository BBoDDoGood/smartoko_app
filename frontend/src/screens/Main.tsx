import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { mainScreenStyles as styles } from './MainScreen.styles';
import { useAppDispatch, useCurrentUser } from '../store/hooks';
import { logout } from '../store/authSlice';
import { StyleSheet } from 'react-native';

export default function Main() {
  const dispatch = useAppDispatch();
  const user = useCurrentUser();

  const handleLogout = () => {
    console.log('🚪 로그아웃');
    dispatch(logout());
  };

  return (
    <ScrollView style={dashboardStyles.container}>
      {/* 헤더 */}
      <View style={dashboardStyles.header}>
        <View>
          <Text style={dashboardStyles.companyName}>Company Name</Text>
          <Text style={dashboardStyles.userName}>{user?.username}</Text>
        </View>
        <View style={dashboardStyles.headerIcons}>
          <TouchableOpacity style={dashboardStyles.iconButton}>
            <Text>🔔</Text>
          </TouchableOpacity>
          <TouchableOpacity style={dashboardStyles.iconButton}>
            <Text>⋮</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Today 섹션 */}
      <View style={dashboardStyles.todaySection}>
        <Text style={dashboardStyles.sectionTitle}>Today</Text>
        <TouchableOpacity>
          <Text style={dashboardStyles.viewAllLink}>View all →</Text>
        </TouchableOpacity>
      </View>

      {/* 통계 카드 그리드 */}
      <View style={dashboardStyles.statsGrid}>
        {/* 첫 번째 행 */}
        <View style={dashboardStyles.statsRow}>
          <View style={dashboardStyles.statCard}>
            <Text style={dashboardStyles.statIcon}>📊</Text>
            <Text style={dashboardStyles.statLabel}>Alarm Items</Text>
            <Text style={dashboardStyles.statValue}>00</Text>
          </View>
          <View style={dashboardStyles.statCard}>
            <Text style={dashboardStyles.statIcon}>📈</Text>
            <Text style={dashboardStyles.statLabel}>All Detect</Text>
            <Text style={dashboardStyles.statValue}>00</Text>
          </View>
        </View>

        {/* 두 번째 행 */}
        <View style={dashboardStyles.statsRow}>
          <View style={dashboardStyles.statCard}>
            <Text style={dashboardStyles.statIcon}>⚠️</Text>
            <Text style={dashboardStyles.statLabel}>Alert Detect</Text>
            <Text style={dashboardStyles.statValue}>00</Text>
          </View>
          <View style={dashboardStyles.statCard}>
            <Text style={dashboardStyles.statIcon}>✓</Text>
            <Text style={dashboardStyles.statLabel}>Normal Detect</Text>
            <Text style={dashboardStyles.statValue}>00</Text>
          </View>
        </View>
      </View>

      {/* Overview 섹션 */}
      <View style={dashboardStyles.overviewSection}>
        <View style={dashboardStyles.overviewTabs}>
          <TouchableOpacity style={[dashboardStyles.tab, dashboardStyles.tabActive]}>
            <Text style={dashboardStyles.tabTextActive}>Today</Text>
          </TouchableOpacity>
          <TouchableOpacity style={dashboardStyles.tab}>
            <Text style={dashboardStyles.tabText}>Yesterday</Text>
          </TouchableOpacity>
          <TouchableOpacity style={dashboardStyles.tab}>
            <Text style={dashboardStyles.tabText}>Weekly</Text>
          </TouchableOpacity>
        </View>

        <View style={dashboardStyles.overviewContent}>
          <Text style={dashboardStyles.overviewTitle}>Overview</Text>
          {/* 여기에 차트나 추가 콘텐츠를 넣을 수 있습니다 */}
        </View>
      </View>

      {/* 하단 네비게이션 */}
      <View style={dashboardStyles.bottomNav}>
        <TouchableOpacity style={dashboardStyles.navItem}>
          <Text style={dashboardStyles.navIcon}>🏠</Text>
        </TouchableOpacity>
        <TouchableOpacity style={dashboardStyles.navItem}>
          <Text style={dashboardStyles.navIcon}>📊</Text>
        </TouchableOpacity>
        <TouchableOpacity style={dashboardStyles.navItem}>
          <Text style={dashboardStyles.navIcon}>👤</Text>
        </TouchableOpacity>
        <TouchableOpacity style={dashboardStyles.navItem}>
          <Text style={dashboardStyles.navIcon}>⚙️</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const dashboardStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  companyName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  userName: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  headerIcons: {
    flexDirection: 'row',
    gap: 12,
  },
  iconButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  todaySection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  viewAllLink: {
    fontSize: 14,
    color: '#3B82F6',
  },
  statsGrid: {
    paddingHorizontal: 20,
    gap: 12,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 8,
    textAlign: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  overviewSection: {
    marginTop: 24,
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingTop: 16,
    minHeight: 300,
  },
  overviewTabs: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 8,
    marginBottom: 16,
  },
  tab: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  tabActive: {
    backgroundColor: '#3B82F6',
  },
  tabText: {
    fontSize: 14,
    color: '#6B7280',
  },
  tabTextActive: {
    fontSize: 14,
    color: 'white',
    fontWeight: '600',
  },
  overviewContent: {
    paddingHorizontal: 20,
  },
  overviewTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingVertical: 12,
    justifyContent: 'space-around',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  navItem: {
    alignItems: 'center',
    padding: 8,
  },
  navIcon: {
    fontSize: 24,
  },
});