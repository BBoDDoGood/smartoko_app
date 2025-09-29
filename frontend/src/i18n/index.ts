import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';
import AsyncStorage from '@react-native-async-storage/async-storage';

// 번역 리소스 import
import en from '../locales/en.json';
import ko from '../locales/ko.json';
import zh from '../locales/zh.json';
import ja from '../locales/ja.json';
import th from '../locales/th.json';
import fil from '../locales/fil.json';

// 지원하는 언어 정의 (ISO 639-1 + ISO 3166-1 표준)
export const supportedLanguages = [
  { code: 'en-US', name: 'English', nativeName: 'English' },
  { code: 'ko-KR', name: 'Korean', nativeName: '한국어' },
  { code: 'zh-CN', name: 'Chinese', nativeName: '中文' },
  { code: 'ja-JP', name: 'Japanese', nativeName: '日本語' },
  { code: 'th-TH', name: 'Thai', nativeName: 'ไทย' },
  { code: 'fil-PH', name: 'Filipino', nativeName: 'Filipino' },
];

// AsyncStorage에서 저장된 언어 가져오기
const getStoredLanguage = async (): Promise<string> => {
  try {
    const storedLang = await AsyncStorage.getItem('user_language');
    if (storedLang && supportedLanguages.find(lang => lang.code === storedLang)) {
      return storedLang;
    }
  } catch (error) {
    console.warn('언어 설정 불러오기 실패:', error);
  }
  
  // 저장된 언어가 없으면 디바이스 언어 확인
  const locales = Localization.getLocales();
  const deviceLocale = locales[0]?.languageTag || 'en-US';
  
  // 정확한 매치를 먼저 찾음 (예: ko-KR)
  let matchedLang = supportedLanguages.find(lang => lang.code === deviceLocale);
  
  // 정확한 매치가 없으면 언어 코드만으로 매치 (예: ko)
  if (!matchedLang) {
    const deviceLangCode = deviceLocale.split('-')[0];
    matchedLang = supportedLanguages.find(lang => lang.code.startsWith(deviceLangCode));
  }
  
  return matchedLang?.code || 'en-US';
};

// 언어 변경 함수
export const changeLanguage = async (languageCode: string): Promise<void> => {
  try {
    await AsyncStorage.setItem('user_language', languageCode);
    await i18next.changeLanguage(languageCode);
  } catch (error) {
    console.error('언어 변경 실패:', error);
  }
};

// i18n 초기화
const initI18n = async () => {
  const savedLanguage = await getStoredLanguage();
  
  await i18next
    .use(initReactI18next)
    .init({
      compatibilityJSON: 'v4',
      resources: {
        'en-US': { translation: en },
        'ko-KR': { translation: ko },
        'zh-CN': { translation: zh },
        'ja-JP': { translation: ja },
        'th-TH': { translation: th },
        'fil-PH': { translation: fil },
      },
      lng: savedLanguage,
      fallbackLng: 'en-US',
      interpolation: {
        escapeValue: false,
      },
      react: {
        useSuspense: false,
      },
    });
};

initI18n();

export default i18next;