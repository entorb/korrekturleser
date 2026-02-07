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
    const payload = parts[1]
    if (parts.length !== 3 || payload === undefined || payload.length === 0) {
      return null
    }

    // Decode the payload (second part)
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
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
  if (!payload || typeof payload.exp !== 'number' || Number.isNaN(payload.exp)) {
    return true
  }

  // exp is in seconds, Date.now() is in milliseconds
  return payload.exp * 1000 < Date.now()
}
