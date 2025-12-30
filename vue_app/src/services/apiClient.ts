/**
 * API client configuration using generated OpenAPI client
 */

import { OpenAPI } from '@/api'
import {
  AuthenticationService,
  ConfigurationService,
  TextImprovementService,
  StatisticsService
} from '@/api'
import { config } from '@/config/env'

// Configure the generated OpenAPI client
OpenAPI.BASE = config.apiBaseUrl

// Setup token injection for authenticated requests
OpenAPI.TOKEN = async () => {
  return localStorage.getItem('access_token') || ''
}

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
  },

  exists(): boolean {
    return this.get() !== null
  }
}

// Export services for easy use
export const api = {
  auth: AuthenticationService,
  config: ConfigurationService,
  text: TextImprovementService,
  statistics: StatisticsService
}

// Re-export useful types and errors
export { ApiError } from '@/api'
export type { OpenAPIConfig } from '@/api'
