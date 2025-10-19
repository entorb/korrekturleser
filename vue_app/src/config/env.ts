/**
 * Environment variable validation and configuration
 */

interface AppConfig {
  apiBaseUrl: string
  isDevelopment: boolean
  isProduction: boolean
}

function validateEnv(): AppConfig {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

  if (!apiBaseUrl) {
    throw new Error('VITE_API_BASE_URL environment variable is not defined')
  }

  return {
    apiBaseUrl,
    isDevelopment: import.meta.env.DEV,
    isProduction: import.meta.env.PROD
  }
}

export const config = validateEnv()
