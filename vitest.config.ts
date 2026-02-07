import { fileURLToPath } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig, configDefaults } from 'vitest/config'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./vue_app/src', import.meta.url))
    }
  },
  test: {
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      exclude: [
        ...configDefaults.exclude,
        '.coverage/**',
        '.venv/**',
        '**/*.spec.ts',
        '**/*.test.ts',
        'coverage/**',
        'dist/**',
        'e2e/**',
        'vue_app/__tests__/**'
      ]
    },
    environment: 'jsdom',
    exclude: [...configDefaults.exclude, 'e2e/**', 'node_modules/'],
    root: fileURLToPath(new URL('./', import.meta.url)),
    setupFiles: ['./vue_app/__tests__/setup.ts'],
    css: {
      modules: {
        classNameStrategy: 'non-scoped'
      }
    },
    server: {
      deps: {
        inline: ['vuetify']
      }
    }
  }
})
