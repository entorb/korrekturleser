/**
 * API client configuration using generated OpenAPI client
 */

import axios from 'axios'
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

// Setup token injection for authenticated requests
// Checks token expiry before each request
OpenAPI.TOKEN = async () => {
  const token = localStorage.getItem('access_token')

  if (!token) {
    return ''
  }

  // Check if token is expired before using it
  if (isTokenExpired(token)) {
    // Token is expired, clear it and return empty string
    // The interceptor below will handle the 401 response
    tokenManager.clear()
    return ''
  }

  return token
}

// Add axios interceptor to handle 401 responses (expired/invalid tokens)
axios.interceptors.response.use(
  response => response,
  error => {
    // If we get a 401 Unauthorized, clear the token and redirect to login
    if (error.response?.status === 401) {
      const currentToken = tokenManager.get()
      if (currentToken) {
        // Token exists but is invalid/expired, clear it
        tokenManager.clear()

        // Only redirect if not already on login page
        if (globalThis.location.pathname !== '/korrekturleser-vue/login') {
          // Use replace to avoid back button issues
          globalThis.location.replace('/korrekturleser-vue/login')
        }
      }
    }
    return Promise.reject(error)
  }
)

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
  text: TextOperationsService,
  statistics: StatisticsService
}

// Re-export useful types and errors
export { ApiError } from '@/api'
export type { OpenAPIConfig } from '@/api'
