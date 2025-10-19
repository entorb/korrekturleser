import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(vuetify)

// Initialize auth state from localStorage before mounting
const authStore = useAuthStore()
authStore.fetchUserInfo().then(() => {
  app.mount('#app')
})
