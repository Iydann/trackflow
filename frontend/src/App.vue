<script setup>
import { useRouter } from 'vue-router'
import HomePage from './pages/HomePage.vue'
import LoginPage from './pages/LoginPage.vue'

const router = useRouter()
</script>

<template>
  <router-view />
</template>
