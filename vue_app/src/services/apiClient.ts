/**
 * API client configuration using generated OpenAPI client
 */

import {
  OpenAPI,
  AuthenticationService,
  ConfigurationService,
  TextOperationsService,
  StatisticsService
} from '@/api'
import { config } from '@/config/env'
import { isTokenExpired } from '@/utils/jwt'

// Configure the generated OpenAPI client
OpenAPI.BASE = config.apiBaseUrl

// Token management helpers
export const tokenManager = {
  get(): string | null {
    return localStorage.getItem('access_token')
  },

  set(token: string): void {
    localStorage.setItem('access_token', token)
  },

  clear(): void {
    localStorage.removeItem('access_token')
  }
}

// Setup token injection for authenticated requests
// Checks token expiry before each request
OpenAPI.TOKEN = async () => {
  const token = tokenManager.get()
  return token != null && !isTokenExpired(token) ? token : ''
}

// Export services
export const api = {
  auth: AuthenticationService,
  config: ConfigurationService,
  text: TextOperationsService,
  statistics: StatisticsService
}
