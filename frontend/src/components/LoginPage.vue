<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-6">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
      <div class="flex justify-center mb-4">
        <img src="/image-15.png" alt="logo" class="w-28 h-28 object-contain" />
      </div>

      <h2 class="text-2xl font-extrabold text-center mb-4">{{ isSignUp ? 'Create Account' : 'Welcome Back' }}</h2>

      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
        {{ error }}
      </div>

      <form class="w-full flex flex-col gap-3" @submit.prevent="handleSubmit">
        <input
          v-if="isSignUp"
          v-model="name"
          type="text"
          placeholder="Enter your name"
          class="w-full px-4 py-3 bg-gray-100 rounded-lg border border-transparent focus:outline-none focus:ring-2 focus:ring-indigo-200"
        />
        <input
          v-model="email"
          type="email"
          placeholder="Enter email"
          required
          class="w-full px-4 py-3 bg-gray-100 rounded-lg border border-transparent focus:outline-none focus:ring-2 focus:ring-indigo-200"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Enter password"
          required
          class="w-full px-4 py-3 bg-gray-100 rounded-lg border border-transparent focus:outline-none focus:ring-2 focus:ring-indigo-200"
        />
        <button 
          type="submit" 
          :disabled="loading"
          class="w-full bg-black text-white rounded-full py-3 font-semibold disabled:opacity-50"
        >
          {{ loading ? 'Please wait...' : (isSignUp ? 'Sign Up' : 'Log In') }}
        </button>
      </form>

      <div class="text-sm text-center mt-4">
        <span v-if="isSignUp">Already have an account? <button type="button" class="text-red-500 ml-2" @click="setSignUpState(false)">Log in</button></span>
        <span v-else>Don't have an account? <button type="button" class="text-red-500 ml-2" @click="setSignUpState(true)">Sign up</button></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '../lib/api.js'

const router = useRouter()
const route = useRoute()

const isSignUp = ref(Boolean(route.state?.isSignUp) || false)
const name = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

watch(route, (r) => {
  isSignUp.value = Boolean(r.state?.isSignUp) || false
})

const setSignUpState = (value) => {
  isSignUp.value = value
  error.value = null
  router.replace({ path: '/login', state: { isSignUp: value } })
}

const handleSubmit = async () => {
  error.value = null
  loading.value = true

  try {
    if (isSignUp.value) {
      await api.register(email.value, password.value, name.value)
    } else {
      await api.login(email.value, password.value)
    }
    
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'An error occurred'
  } finally {
    loading.value = false
  }
}
</script>
