<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/apiClient'
import type { UsageStatsResponse } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const myUsage = ref<Record<string, number | string> | null>(null)
const allStats = ref<UsageStatsResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    goBack()
  }
}

onMounted(async () => {
  await loadStats()
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})

async function loadStats() {
  isLoading.value = true
  error.value = null

  try {
    myUsage.value = await api.stats.getMyUsageApiStatsMyUsageGet()

    try {
      allStats.value = await api.stats.getUsageStatsApiStatsGet()
    } catch {
      console.log('All stats not available (admin only)')
    }
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
  const numValue = typeof num === 'string' ? parseInt(num, 10) : num
  return numValue.toLocaleString()
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString()
}

const dailyHeaders = [
  { title: 'Datum', key: 'date' },
  { title: 'Nutzer', key: 'user_name' },
  { title: 'Anfragen', key: 'cnt_requests' },
  { title: 'Token', key: 'cnt_tokens' }
]

const totalHeaders = [
  { title: 'Nutzer', key: 'user_name' },
  { title: 'Anfragen gesamt', key: 'total_requests' },
  { title: 'Token gesamt', key: 'total_tokens' }
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
            <div v-else-if="myUsage">
              <!-- My Usage Section -->
              <v-card
                variant="outlined"
                class="mb-4"
              >
                <v-card-text>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th class="text-center" />
                        <th class="text-center">
                          <v-icon title="Anfragen">mdi-send</v-icon>
                        </th>
                        <th class="text-center">
                          <v-icon title="Token">mdi-pound</v-icon>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td class="text-center">
                          <v-icon title="Diese Sitzung">mdi-clock-outline</v-icon>
                        </td>
                        <td class="text-center">{{ formatNumber(authStore.totalRequests) }}</td>
                        <td class="text-center">{{ formatNumber(authStore.totalTokens) }}</td>
                      </tr>
                      <tr>
                        <td class="text-center">
                          <v-icon title="Gesamt">mdi-chart-bar</v-icon>
                        </td>
                        <td class="text-center">{{ formatNumber(myUsage.total_requests) }}</td>
                        <td class="text-center">{{ formatNumber(myUsage.total_tokens) }}</td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>

              <!-- Admin Statistics -->
              <div v-if="allStats">
                <v-card
                  variant="outlined"
                  class="mb-4"
                >
                  <v-card-title>Statistiken aller Nutzer</v-card-title>
                </v-card>

                <!-- Total Usage Table -->
                <v-card
                  variant="outlined"
                  class="mb-4"
                >
                  <v-card-title class="text-h6">Gesamtnutzung pro Nutzer</v-card-title>
                  <v-data-table
                    :headers="totalHeaders"
                    :items="allStats.total"
                    :items-per-page="-1"
                    hide-default-footer
                  >
                    <template #[`item.total_requests`]="{ item }">
                      {{ formatNumber(item.total_requests) }}
                    </template>
                    <template #[`item.total_tokens`]="{ item }">
                      {{ formatNumber(item.total_tokens) }}
                    </template>
                  </v-data-table>
                </v-card>

                <!-- Daily Usage Table -->
                <v-card variant="outlined">
                  <v-card-title class="text-h6">Tägliche Nutzung</v-card-title>
                  <v-data-table
                    :headers="dailyHeaders"
                    :items="allStats.daily"
                    :items-per-page="10"
                  >
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
            </div>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>
