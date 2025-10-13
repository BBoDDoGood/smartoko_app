import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  FlatList,
  StyleSheet,
  Dimensions
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { supportedLanguages, changeLanguage } from '../i18n';
import { PrimaryColors, NeutralColors } from '../core/theme/colors';
import { Spacing } from '../core/theme/spacing';

// 화면 크기 정보
const { width: screenWidth } = Dimensions.get('window');
const wp = (percentage: number) => screenWidth * (percentage / 100);
const fs = (size: number) => Math.max(screenWidth * (size / 100), 12);

interface LanguageSelectorProps {
  style?: object;
}

interface LanguageItem {
  code: string;
  name: string;
  nativeName: string;
}

export default function LanguageSelector({ style }: LanguageSelectorProps) {
  const { t, i18n } = useTranslation();
  const [isModalVisible, setIsModalVisible] = useState(false);

  const currentLanguage = supportedLanguages.find(
    lang => lang.code === i18n.language
  ) || supportedLanguages[0];

  const handleLanguageSelect = async (languageCode: string) => {
    await changeLanguage(languageCode);
    setIsModalVisible(false);
  };

  const renderLanguageItem = ({ item }: { item: LanguageItem }) => (
    <TouchableOpacity
      style={[
        styles.languageItem,
        item.code === currentLanguage.code && styles.selectedLanguageItem
      ]}
      onPress={() => handleLanguageSelect(item.code)}
    >
      <Text style={[
        styles.languageText,
        item.code === currentLanguage.code && styles.selectedLanguageText
      ]}>
        {item.nativeName}
      </Text>
      <Text style={[
        styles.languageSubText,
        item.code === currentLanguage.code && styles.selectedLanguageSubText
      ]}>
        {item.name}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={[styles.container, style]}>
      {/* 언어 선택 버튼 */}
      <TouchableOpacity
        style={styles.selector}
        onPress={() => setIsModalVisible(true)}
      >
        <Text style={styles.selectedText}>
          {currentLanguage.nativeName}
        </Text>
        <Text style={styles.dropdownIcon}>▼</Text>
      </TouchableOpacity>

      {/* Modal 팝업 */}
      <Modal
        visible={isModalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setIsModalVisible(false)}
      >
        {/* 어두운 배경 (클릭하면 닫힘) */}
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setIsModalVisible(false)}
        >
          {/* Modal 내용 박스 (클릭해도 안 닫힘) */}
          <TouchableOpacity activeOpacity={1}>
            <View style={styles.modalContent}>
              {/* 헤더 */}
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>{t('login.selectLanguage')}</Text>
              </View>

              {/* 언어 목록 */}
              <FlatList
                data={supportedLanguages}
                keyExtractor={(item) => item.code}
                renderItem={renderLanguageItem}
                showsVerticalScrollIndicator={false}
              />
            </View>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },

  // 언어 선택 버튼
  selector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: NeutralColors.gray50,
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: NeutralColors.gray200,
    minHeight: 32,
  },
  selectedText: {
    fontSize: fs(3.2),
    color: NeutralColors.gray700,
    fontWeight: '500',
  },
  dropdownIcon: {
    fontSize: fs(2.5),
    color: NeutralColors.gray500,
    marginLeft: 6,
  },

  // Modal 어두운 배경
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: wp(10),
  },

  // Modal 내용 박스
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 16,
    width: wp(80),
    maxWidth: 350,
    maxHeight: '70%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 8,
  },

  // Modal 헤더
  modalHeader: {
    padding: Spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: NeutralColors.gray200,
  },
  modalTitle: {
    fontSize: fs(4.5),
    fontWeight: '600',
    color: NeutralColors.gray900,
    textAlign: 'center',
  },

  // 언어 아이템
  languageItem: {
    padding: Spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: NeutralColors.gray100,
  },
  selectedLanguageItem: {
    backgroundColor: PrimaryColors.blue50,
    borderLeftWidth: 4,
    borderLeftColor: PrimaryColors.blue500,
  },
  languageText: {
    fontSize: fs(4.2),
    color: NeutralColors.gray900,
    fontWeight: '500',
    marginBottom: 2,
  },
  selectedLanguageText: {
    color: PrimaryColors.blue700,
    fontWeight: '600',
  },
  languageSubText: {
    fontSize: fs(3.5),
    color: NeutralColors.gray600,
  },
  selectedLanguageSubText: {
    color: PrimaryColors.blue600,
  },
});
