// src/core/config/production.ts
import { AppConfig } from './index';

export const productionConfig: AppConfig = {
  // Environment
  nodeEnv: 'production',
  appEnv: 'production',
  appName: 'SmartOkO',
  appVersion: '1.0.0',
  
  // API
  apiBaseUrl: 'https://api.smartoko.com',
  apiVersion: 'v1',
  apiTimeout: 5000,
  
  // WebSocket
  socketUrl: 'wss://socket.smartoko.com',
  socketReconnectAttempts: 3,
  socketHeartbeatInterval: 60000,
  
  // Features
  realtimeEnabled: true,
  offlineModeEnabled: true,
  analyticsEnabled: true,
  
  // Localization
  defaultLanguage: 'ko',
  supportedLanguages: ['ko', 'en', 'zh', 'ja', 'th', 'ph'],
};