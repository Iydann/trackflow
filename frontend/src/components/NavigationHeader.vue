<template>
  <header class="flex items-center justify-between px-7 py-4 bg-white border-b sticky top-0 z-20">
    <div class="flex items-center gap-3">
      <img src="/image-15.png" alt="TrackFlow logo" class="h-9 w-auto object-contain" />
      <h1 class="font-extrabold text-2xl">TrackFlow</h1>
    </div>

    <nav class="flex items-center gap-3">
        <template v-if="!user">
          <Button variant="ghost" class="px-3 py-2 font-semibold" @click="openSignUp">Sign up</Button>
          <Button class="px-3 py-2 rounded-full" @click="openLogin">Log in</Button>
        </template>
        <template v-else>
          <div class="relative flex items-center gap-3" ref="userBtnRef">
            <button class="flex items-center gap-2 bg-gray-100 border border-transparent px-2 py-1 rounded-full" @click="toggleMenu">
              <div class="w-8 h-8 rounded-full bg-indigo-300 text-white flex items-center justify-center font-bold">{{ user.name.charAt(0).toUpperCase() }}</div>
              <span class="font-semibold text-gray-800 hidden md:inline">{{ user.name }}</span>
            </button>

            <div v-if="showMenu" class="absolute right-0 mt-2 bg-white border border-gray-100 shadow-lg rounded-lg min-w-[180px] z-50 overflow-hidden" role="menu" aria-label="User menu">
              <button class="block w-full text-left px-4 py-2 font-medium text-gray-700 hover:bg-gray-50" @click="goToProfile">Profile</button>
              <button class="block w-full text-left px-4 py-2 font-medium text-gray-700 hover:bg-gray-50" @click="goToSettings">Settings</button>
              <button class="block w-full text-left px-4 py-2 font-medium text-gray-700 hover:bg-gray-50" @click="openHelp">Help</button>
              <div class="h-px bg-gray-100" />
              <button class="block w-full text-left px-4 py-2 font-semibold text-red-600 hover:bg-gray-50" @click="logout">Log out</button>
            </div>

            <Button variant="ghost" class="px-3 py-2 hidden" @click="logout">Log Out</Button>
          </div>
        </template>
    </nav>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from './Button.vue'
import { api } from '../lib/api.js'

const router = useRouter()
const showMenu = ref(false)
const userBtnRef = ref(null)

const user = computed(() => {
  const userData = localStorage.getItem('trackflow_user')
  return userData ? JSON.parse(userData) : null
})

const handleDocumentClick = (e) => {
  const btn = userBtnRef.value
  if (!btn) return
  if (!btn.contains(e.target)) {
    showMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})

const openLogin = () => {
  router.push({ path: '/login', state: { isSignUp: false } })
}

const openSignUp = () => {
  router.push({ path: '/login', state: { isSignUp: true } })
}

const logout = () => {
  api.logout()
  showMenu.value = false
  router.push('/')
  window.location.reload()
}

const toggleMenu = (e) => {
  e.stopPropagation()
  showMenu.value = !showMenu.value
}

const goToProfile = () => { showMenu.value = false; router.push('/profile') }
const goToSettings = () => { showMenu.value = false; router.push('/profile?tab=settings') }
const openHelp = () => { showMenu.value = false; window.open('https://example.com/help', '_blank') }
</script>
