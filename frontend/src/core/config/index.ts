// src/core/config/index.ts
import { developmentConfig } from './development';
import { stagingConfig } from './staging';
import { productionConfig } from './production';

export interface AppConfig {
  // Environment
  nodeEnv: string;
  appEnv: string;
  appName: string;
  appVersion: string;
  
  // API
  apiBaseUrl: string;
  apiVersion: string;
  apiTimeout: number;
  
  // WebSocket
  socketUrl: string;
  socketReconnectAttempts: number;
  socketHeartbeatInterval: number;
  
  // Features
  realtimeEnabled: boolean;
  offlineModeEnabled: boolean;
  analyticsEnabled: boolean;
  
  // Localization
  defaultLanguage: string;
  supportedLanguages: string[];
}

const getConfig = (): AppConfig => {
  const environment = __DEV__ ? 'development' : process.env.NODE_ENV || 'production';
  
  switch (environment) {
    case 'development':
      return developmentConfig;
    case 'staging':
      return stagingConfig;
    case 'production':
      return productionConfig;
    default:
      return developmentConfig;
  }
};

export const appConfig = getConfig();

// Helper functions
export const isDevelopment = () => appConfig.appEnv === 'development';
export const isStaging = () => appConfig.appEnv === 'staging';
export const isProduction = () => appConfig.appEnv === 'production';

// API helpers
export const getApiUrl = (endpoint: string) => 
  `${appConfig.apiBaseUrl}/${appConfig.apiVersion}${endpoint}`;