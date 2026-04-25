import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
  input: 'http://localhost:9002/openapi.json',
  output: {
    path: 'vue_app/src/api',
    postProcess: ['biome:format']
  },
  plugins: ['@hey-api/client-axios', '@hey-api/typescript', '@hey-api/sdk']
})
