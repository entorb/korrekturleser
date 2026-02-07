<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

import type { UsageStatsResponse } from '@/api'
import { api } from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref<UsageStatsResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Escape') router.push({ name: 'text' })
}

async function loadStats() {
  isLoading.value = true
  error.value = null

  try {
    stats.value = await api.statistics.getAllStatsApiStatsGet()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Fehler beim Laden der Statistiken'
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadStats()
  globalThis.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  globalThis.removeEventListener('keydown', handleKeyPress)
})

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

const formatNumber = (num: number | string | undefined = 0): string =>
  (typeof num === 'string' ? Number.parseInt(num, 10) : num || 0).toLocaleString()

const formatDate = (dateStr: string): string => new Date(dateStr).toLocaleDateString('de-DE')
</script>

<template>
  <q-page-container>
    <q-header
      elevated
      class="bg-primary"
    >
      <q-toolbar>
        <q-toolbar-title>Statistik</q-toolbar-title>

        <span class="q-mr-md">{{ authStore.user?.user_name }}</span>

        <q-btn
          flat
          round
          dense
          icon="arrow_back"
          @click="router.push({ name: 'text' })"
        >
          <q-tooltip>Zurück (Esc)</q-tooltip>
        </q-btn>

        <q-btn
          flat
          round
          dense
          icon="logout"
          @click="handleLogout"
        >
          <q-tooltip>Abmelden</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-page class="q-pa-md">
      <q-card>
        <q-card-section>
          <!-- Loading -->
          <div
            v-if="isLoading"
            class="row justify-center q-pa-lg"
          >
            <q-spinner
              color="primary"
              size="3em"
            />
          </div>

          <!-- Error -->
          <q-banner
            v-else-if="error"
            class="bg-negative text-white"
            rounded
          >
            {{ error }}
          </q-banner>

          <!-- Stats Content -->
          <div v-else-if="stats">
            <!-- Total Usage Table -->
            <q-card
              bordered
              class="q-mb-md"
            >
              <q-card-section>
                <div class="text-h6">Gesamt</div>
              </q-card-section>
              <q-markup-table>
                <thead>
                  <tr>
                    <th scope="col">
                      <q-icon name="account_circle">
                        <q-tooltip>Nutzer</q-tooltip>
                      </q-icon>
                    </th>
                    <th scope="col">
                      <q-icon name="send">
                        <q-tooltip>Anfragen</q-tooltip>
                      </q-icon>
                    </th>
                    <th scope="col">
                      <q-icon name="tag">
                        <q-tooltip>Token</q-tooltip>
                      </q-icon>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in stats.total"
                    :key="item.user_name"
                  >
                    <td>{{ item.user_name }}</td>
                    <td>{{ formatNumber(item.cnt_requests) }}</td>
                    <td>{{ formatNumber(item.cnt_tokens) }}</td>
                  </tr>
                </tbody>
              </q-markup-table>
            </q-card>

            <!-- Daily Usage Table -->
            <q-card bordered>
              <q-card-section>
                <div class="text-h6">Täglich</div>
              </q-card-section>
              <q-markup-table>
                <thead>
                  <tr>
                    <th scope="col">
                      <q-icon name="calendar_today">
                        <q-tooltip>Datum</q-tooltip>
                      </q-icon>
                    </th>
                    <th scope="col">
                      <q-icon name="account_circle">
                        <q-tooltip>Nutzer</q-tooltip>
                      </q-icon>
                    </th>
                    <th scope="col">
                      <q-icon name="send">
                        <q-tooltip>Anfragen</q-tooltip>
                      </q-icon>
                    </th>
                    <th scope="col">
                      <q-icon name="tag">
                        <q-tooltip>Token</q-tooltip>
                      </q-icon>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in stats.daily"
                    :key="`${item.date}-${item.user_name}`"
                  >
                    <td>{{ formatDate(item.date) }}</td>
                    <td>{{ item.user_name }}</td>
                    <td>{{ formatNumber(item.cnt_requests) }}</td>
                    <td>{{ formatNumber(item.cnt_tokens) }}</td>
                  </tr>
                </tbody>
              </q-markup-table>
            </q-card>
          </div>
        </q-card-section>
      </q-card>
    </q-page>
  </q-page-container>
</template>
