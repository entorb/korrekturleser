<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Try to restore user session if token exists
  authStore.fetchUserInfo()
})
</script>

<template>
  <v-app>
    <router-view />
  </v-app>
</template>
