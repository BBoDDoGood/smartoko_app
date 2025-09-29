// src/core/config/development.ts
import { AppConfig } from './index';

export const developmentConfig: AppConfig = {
  // Environment
  nodeEnv: 'development',
  appEnv: 'development',
  appName: 'SmartOkO Dev',
  appVersion: '1.0.0-dev',
  
  // API
  apiBaseUrl: 'http://localhost:3000',
  apiVersion: 'v1',
  apiTimeout: 10000,
  
  // WebSocket
  socketUrl: 'ws://localhost:3001',
  socketReconnectAttempts: 5,
  socketHeartbeatInterval: 30000,
  
  // Features
  realtimeEnabled: true,
  offlineModeEnabled: true,
  analyticsEnabled: false,
  
  // Localization
  defaultLanguage: 'ko',
  supportedLanguages: ['ko', 'en', 'zh', 'ja', 'th', 'ph'],
};