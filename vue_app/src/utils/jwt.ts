/**
 * JWT token utilities
 */

interface JwtPayload {
  user_id: number
  username: string
  exp: number
}

/**
 * Decode JWT token without verification (client-side only)
 * The server validates the token - this is just for extracting data
 */
export function decodeJwt(token: string): JwtPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3 || parts[1] == null) return null

    const decoded = atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded) as JwtPayload
  } catch {
    return null
  }
}

/**
 * Check if JWT token is expired
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeJwt(token)
  if (payload?.exp == null || !Number.isFinite(payload.exp)) return true
  return payload.exp * 1000 < Date.now()
}
