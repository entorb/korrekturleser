import { vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
vi.stubGlobal('localStorage', localStorageMock)

// Mock import.meta.env for tests
vi.stubGlobal('import.meta', {
  env: {
    VITE_API_BASE_URL: 'http://127.0.0.1:9002',
    DEV: true,
    PROD: false,
    BASE_URL: '/korrekturleser-vue/'
  }
})
