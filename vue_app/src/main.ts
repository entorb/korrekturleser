import { createPinia } from "pinia"
import { Quasar } from "quasar"
import { createApp } from "vue"

import App from "./App.vue"
import quasarConfig from "./plugins/quasar.ts"
import router from "./router/index.ts"
import "./assets/ios-fixes.css"

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(Quasar, quasarConfig)

app.mount("#app")
