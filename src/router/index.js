import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import UploadPage from '../pages/UploadPage.vue'
import DefineLinePage from '../pages/DefineLinePage.vue'
import ProcessPage from '../pages/ProcessPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadPage
  },
  {
    path: '/upload/define',
    name: 'DefineLine',
    component: DefineLinePage
  },
  {
    path: '/process/:id',
    name: 'Process',
    component: ProcessPage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
