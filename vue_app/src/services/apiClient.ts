/**
 * API client configuration using generated OpenAPI client
 */

import { isAxiosError } from "axios"

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

// Token rejected by server (e.g. signed with a rotated secret): drop it and
// reload, so the router guard redirects to login
client.instance.interceptors.response.use(undefined, (error: unknown) => {
  if (isAxiosError(error) && error.response?.status === 401 && tokenManager.get() != null) {
    tokenManager.clear()
    globalThis.location.reload()
  }
  return Promise.reject(error)
})

// Export SDK functions
export const api = {
  auth: { loginApiAuthLoginPost },
  config: { getConfigApiConfigGet },
  text: { improveTextApiTextPost },
  statistics: { getAllStatsApiStatsGet },
}
