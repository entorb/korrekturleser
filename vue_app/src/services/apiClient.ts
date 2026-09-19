/**
 * API client configuration using generated OpenAPI client
 */

import { client } from "@/api/client.gen.ts"
import {
  getAllStatsApiStatsGet,
  getConfigApiConfigGet,
  improveTextApiTextPost,
  loginApiAuthLoginPost,
} from "@/api/index.ts"
import { config } from "@/config/env.ts"
import { isTokenExpired } from "@/utils/jwt.ts"

// Configure the generated client
client.setConfig({
  baseURL: config.apiBaseUrl,
})

// Token management helpers
export const tokenManager = {
  get(): string | null {
    return localStorage.getItem("access_token")
  },

  set(token: string): void {
    localStorage.setItem("access_token", token)
  },

  clear(): void {
    localStorage.removeItem("access_token")
  },
}

// Setup token injection for authenticated requests
// Checks token expiry before each request
client.setConfig({
  auth() {
    const token = tokenManager.get()
    return token != null && !isTokenExpired(token) ? token : ""
  },
})

// Export SDK functions
export const api = {
  auth: { loginApiAuthLoginPost },
  config: { getConfigApiConfigGet },
  text: { improveTextApiTextPost },
  statistics: { getAllStatsApiStatsGet },
}
