<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const secret = ref('')

async function handleLogin() {
  try {
    await authStore.login(secret.value)
    router.push({ name: 'text' })
  } catch (error) {
    // Error is already set in store
    console.error('Login failed:', error)
  }
}
</script>

<template>
  <v-container
    fluid
    class="fill-height"
    style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
  >
    <v-row
      align="center"
      justify="center"
    >
      <v-col
        cols="12"
        sm="8"
        md="6"
        lg="4"
      >
        <v-card>
          <v-card-title class="text-h4 text-center"> KI Korrekturleser </v-card-title>
          <v-card-subtitle class="text-center">
            KI-gestützte Textkorrektur und -verbesserung
          </v-card-subtitle>

          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="secret"
                label="Geheimnis"
                type="password"
                :disabled="authStore.isLoading"
                autocomplete="current-password"
                variant="outlined"
                required
              />

              <v-alert
                v-if="authStore.error"
                type="error"
                variant="tonal"
                class="mb-4"
              >
                {{ authStore.error }}
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                :loading="authStore.isLoading"
                :disabled="!secret"
                block
                size="large"
              >
                Anmelden
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
