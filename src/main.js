import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/index.js'
import auth from './lib/auth.js'

const app = createApp(App)

app.use(router)
app.provide('auth', auth)

app.mount('#app')
