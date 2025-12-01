<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/apiClient'
import type { UsageStatsResponse } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref<UsageStatsResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    goBack()
  }
}

onMounted(async () => {
  await loadStats()
  globalThis.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  globalThis.removeEventListener('keydown', handleKeyPress)
})

async function loadStats() {
  isLoading.value = true
  error.value = null

  try {
    stats.value = await api.statistics.getAllStatsApiStatsGet()
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Fehler beim Laden der Statistiken'
    console.error('Stats error:', err)
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  router.push({ name: 'text' })
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

function formatNumber(num: number | string | undefined): string {
  if (num === undefined || num === null) return '0'
  const numValue = typeof num === 'string' ? Number.parseInt(num, 10) : num
  return numValue.toLocaleString()
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('de-DE')
}

const dailyHeaders = [
  { title: '', key: 'date' },
  { title: '', key: 'user_name' },
  { title: '', key: 'cnt_requests' },
  { title: '', key: 'cnt_tokens' }
]

const totalHeaders = [
  { title: '', key: 'user_name' },
  { title: '', key: 'cnt_requests' },
  { title: '', key: 'cnt_tokens' }
]
</script>

<template>
  <v-app>
    <v-app-bar
      color="primary"
      prominent
    >
      <v-btn
        icon
        @click="goBack"
        title="Zurück (Esc)"
      >
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>

      <v-app-bar-title>Statistik</v-app-bar-title>

      <v-spacer />

      <span class="mr-4">{{ authStore.user?.user_name }}</span>

      <v-btn
        icon
        @click="handleLogout"
        title="Abmelden"
      >
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-card>
          <v-card-text>
            <!-- Loading -->
            <v-progress-circular
              v-if="isLoading"
              indeterminate
              color="primary"
              class="ma-4"
            />

            <!-- Error -->
            <v-alert
              v-else-if="error"
              type="error"
              variant="tonal"
            >
              {{ error }}
            </v-alert>

            <!-- Stats Content -->
            <div v-else-if="stats">
              <!-- Total Usage Table -->
              <v-card
                variant="outlined"
                class="mb-4"
              >
                <v-card-title class="text-h6">Gesamt</v-card-title>
                <v-data-table
                  :headers="totalHeaders"
                  :items="stats.total"
                  :items-per-page="-1"
                  hide-default-footer
                >
                  <template #[`header.user_name`]>
                    <v-icon title="Nutzer">mdi-account-outline</v-icon>
                  </template>
                  <template #[`header.cnt_requests`]>
                    <v-icon title="Anfragen">mdi-send</v-icon>
                  </template>
                  <template #[`header.cnt_tokens`]>
                    <v-icon title="Token">mdi-pound</v-icon>
                  </template>
                  <template #[`item.cnt_requests`]="{ item }">
                    {{ formatNumber(item.cnt_requests) }}
                  </template>
                  <template #[`item.cnt_tokens`]="{ item }">
                    {{ formatNumber(item.cnt_tokens) }}
                  </template>
                </v-data-table>
              </v-card>

              <!-- Daily Usage Table -->
              <v-card variant="outlined">
                <v-card-title class="text-h6">Täglich</v-card-title>
                <v-data-table
                  :headers="dailyHeaders"
                  :items="stats.daily"
                  :items-per-page="10"
                >
                  <template #[`header.date`]>
                    <v-icon title="Datum">mdi-calendar</v-icon>
                  </template>
                  <template #[`header.user_name`]>
                    <v-icon title="Nutzer">mdi-account-outline</v-icon>
                  </template>
                  <template #[`header.cnt_requests`]>
                    <v-icon title="Anfragen">mdi-send</v-icon>
                  </template>
                  <template #[`header.cnt_tokens`]>
                    <v-icon title="Token">mdi-pound</v-icon>
                  </template>
                  <template #[`item.date`]="{ item }">
                    {{ formatDate(item.date) }}
                  </template>
                  <template #[`item.cnt_requests`]="{ item }">
                    {{ formatNumber(item.cnt_requests) }}
                  </template>
                  <template #[`item.cnt_tokens`]="{ item }">
                    {{ formatNumber(item.cnt_tokens) }}
                  </template>
                </v-data-table>
              </v-card>
            </div>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>
