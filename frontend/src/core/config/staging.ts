// src/core/config/staging.ts
import { AppConfig } from './index';

export const stagingConfig: AppConfig = {
  // Environment
  nodeEnv: 'production',
  appEnv: 'staging',
  appName: 'SmartOkO Staging',
  appVersion: '1.0.0-staging',
  
  // API
  apiBaseUrl: 'https://staging-api.smartoko.com',
  apiVersion: 'v1',
  apiTimeout: 8000,
  
  // WebSocket
  socketUrl: 'wss://staging-socket.smartoko.com',
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