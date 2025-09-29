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
      <Text style={styles.label}>{t('login.selectLanguage')}</Text>
      
      <TouchableOpacity
        style={styles.selector}
        onPress={() => setIsModalVisible(true)}
      >
        <Text style={styles.selectedText}>
          {currentLanguage.nativeName}
        </Text>
        <Text style={styles.dropdownIcon}>▼</Text>
      </TouchableOpacity>

      <Modal
        visible={isModalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setIsModalVisible(false)}
      >
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setIsModalVisible(false)}
        >
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t('login.selectLanguage')}</Text>
            </View>
            
            <FlatList
              data={supportedLanguages}
              keyExtractor={(item) => item.code}
              renderItem={renderLanguageItem}
              showsVerticalScrollIndicator={false}
            />
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: Spacing.sm,
  },
  label: {
    fontSize: fs(3.5),
    color: NeutralColors.gray700,
    marginBottom: 6,
    fontWeight: '500',
  },
  selector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: NeutralColors.gray50,
    borderRadius: 8,
    paddingHorizontal: Spacing.md,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: NeutralColors.gray300,
    minHeight: 50,
  },
  selectedText: {
    fontSize: fs(4),
    color: NeutralColors.gray900,
    flex: 1,
  },
  dropdownIcon: {
    fontSize: fs(3),
    color: NeutralColors.gray500,
    marginLeft: Spacing.sm,
  },
  
  // 모달 스타일
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: wp(10),
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 16,
    maxHeight: '70%',
    width: '100%',
    maxWidth: 350,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 8,
  },
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
  
  // 언어 아이템 스타일
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