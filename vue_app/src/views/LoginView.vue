<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('') // dummy field,added for password manager compatibility
const secret = ref('')

async function handleLogin() {
  try {
    await authStore.login(secret.value)
    // Use replace to prevent back button from returning to login
    await router.replace({ name: 'text' })
  } catch (error) {
    // Error is already set in store
    console.error('Login failed:', error)
  }
}
</script>

<template>
  <q-page-container>
    <q-page
      class="flex flex-center"
      style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    >
      <div style="width: 100%; max-width: 500px; padding: 20px">
        <q-card>
          <q-card-section>
            <div class="text-h4 text-center">KI Korrekturleser</div>
            <div class="text-subtitle2 text-center text-grey-7">
              KI-gestützte Textkorrektur und -verbesserung
            </div>
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="handleLogin">
              <!-- Hidden username field for accessibility and password managers -->
              <input
                v-model="username"
                type="text"
                autocomplete="username"
                style="display: none"
                tabindex="-1"
                aria-hidden="true"
              />

              <q-input
                v-model="secret"
                label="Geheimnis"
                type="password"
                :disable="authStore.isLoading"
                autocomplete="current-password"
                outlined
                required
                class="q-mb-md"
              />

              <q-banner
                v-if="authStore.error"
                class="bg-negative text-white q-mb-md"
                rounded
              >
                {{ authStore.error }}
              </q-banner>

              <q-btn
                type="submit"
                color="primary"
                :loading="authStore.isLoading"
                :disable="!secret"
                unelevated
                size="lg"
                class="full-width"
                label="Anmelden"
              />
            </q-form>
          </q-card-section>
        </q-card>
      </div>
    </q-page>
  </q-page-container>
</template>
