import { describe, expect, it } from 'vitest'
import { decodeJwt, isTokenExpired } from '../jwt'

function encodePart(obj: object): string {
  return btoa(JSON.stringify(obj)).replaceAll('+', '-').replaceAll('/', '_')
}

function makeToken(payload: object): string {
  return `${encodePart({ alg: 'none', typ: 'JWT' })}.${encodePart(payload)}.${encodePart({})}`
}

describe('decodeJwt', () => {
  it('decodes a valid JWT payload', () => {
    const token = makeToken({ user_id: 1, username: 'TestUser', exp: 1_234_567_890 })

    expect(decodeJwt(token)).toEqual({ user_id: 1, username: 'TestUser', exp: 1_234_567_890 })
  })

  it('returns null for a token without three parts', () => {
    expect(decodeJwt('only.two')).toBeNull()
  })

  it('returns null for invalid base64', () => {
    expect(decodeJwt('header.%%%invalid%%%.signature')).toBeNull()
  })

  it('returns null for invalid JSON payload', () => {
    const part = btoa('not json')
    expect(decodeJwt(`header.${part}.signature`)).toBeNull()
  })
})

describe('isTokenExpired', () => {
  it('returns false for a token expiring in the future', () => {
    const token = makeToken({ exp: Math.floor(Date.now() / 1000) + 3600 })

    expect(isTokenExpired(token)).toBe(false)
  })

  it('returns true for a token expired in the past', () => {
    const token = makeToken({ exp: Math.floor(Date.now() / 1000) - 3600 })

    expect(isTokenExpired(token)).toBe(true)
  })

  it('returns true for a token without exp claim', () => {
    const token = makeToken({ user_id: 1, username: 'TestUser' })

    expect(isTokenExpired(token)).toBe(true)
  })

  it('returns true for a malformed token', () => {
    expect(isTokenExpired('not.a.jwt')).toBe(true)
  })
})
