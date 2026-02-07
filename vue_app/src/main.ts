import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar } from 'quasar'

import App from './App.vue'
import router from './router'
import quasarConfig from './plugins/quasar'
import './assets/ios-fixes.css'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(Quasar, quasarConfig)

app.mount('#app')
