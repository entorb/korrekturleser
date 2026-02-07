import { createPinia } from 'pinia'
import { Quasar } from 'quasar'
import { createApp } from 'vue'

import App from './App.vue'
import quasarConfig from './plugins/quasar'
import router from './router'
import './assets/ios-fixes.css'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(Quasar, quasarConfig)

app.mount('#app')
