// Plugins
import Components from 'unplugin-vue-components/vite'
import Vue from '@vitejs/plugin-vue'
import Vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import VueRouter from 'unplugin-vue-router/vite'
import { VitePWA } from 'vite-plugin-pwa'

// Utilities
import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'

import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  // TM: important when deploying not into the webserver root dir
  // error message "was blocked due to MIME type (“text/html”) mismatch"
  base: '/korrekturleser2/',
  build: {
    assetsInlineLimit: 4096,
    chunkSizeWarningLimit: 500,
    cssCodeSplit: true,
    minify: 'esbuild',
    sourcemap: false,
    target: 'esnext'
  },

  optimizeDeps: {
    exclude: [
      'unplugin-vue-router/runtime',
      'unplugin-vue-router/data-loaders',
      'unplugin-vue-router/data-loaders/basic'
    ],
    include: ['vue', 'vue-router', 'vuetify']
  },
  plugins: [
    Vue({
      template: { transformAssetUrls }
    }),
    Vuetify({
      autoImport: true,
      styles: 'sass'
    }),
    vueDevTools(),
    VueRouter({
      dts: 'vue_app/typed-router.d.ts'
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
    Components({
      dts: 'vue_app/components.d.ts'
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'android-chrome-192x192.png'],
      manifest: {
        name: 'Korrekturleser',
        short_name: 'Korrekturleser',
        description: 'Korrekturleser',
        theme_color: '#1976d2',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/korrekturleser2/',
        start_url: '/korrekturleser2/',
        icons: [
          {
            src: '/korrekturleser2/android-chrome-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/korrekturleser2/android-chrome-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: '/korrekturleser2/apple-touch-icon.png',
            sizes: '180x180',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365
              }
            }
          }
        ]
      }
    })
  ],
  define: { 'process.env': {} },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./vue_app/src', import.meta.url))
    },
    extensions: ['.js', '.json', '.jsx', '.mjs', '.ts', '.tsx', '.vue']
  },
  preview: { port: 4173, strictPort: true },
  server: { port: 5173, strictPort: true }
})
