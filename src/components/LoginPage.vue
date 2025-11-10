<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-6">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
      <div class="flex justify-center mb-4">
        <img src="/image-15.png" alt="logo" class="w-28 h-28 object-contain" />
      </div>

      <h2 class="text-2xl font-extrabold text-center mb-4">{{ isSignUp ? 'Create Account' : 'Welcome Back' }}</h2>

      <!-- Google sign-in button -->
      <button class="w-full flex items-center justify-center gap-3 border rounded-full py-2 px-4 shadow-sm hover:shadow-md mb-4 bg-white" type="button">
        <span aria-hidden>
          <img src="/assets/icon-google.png" alt="Google" class="w-6 h-6" />
        </span>
        <span class="font-medium text-sm">Continue With Google</span>
      </button>

      <div class="text-center text-sm text-gray-500 mb-4">Or</div>

      <form class="w-full flex flex-col gap-3" @submit.prevent="handleSubmit">
        <input
          v-model="identifier"
          type="text"
          placeholder="Enter email or username"
          class="w-full px-4 py-3 bg-gray-100 rounded-lg border border-transparent focus:outline-none focus:ring-2 focus:ring-indigo-200"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Enter password"
          class="w-full px-4 py-3 bg-gray-100 rounded-lg border border-transparent focus:outline-none focus:ring-2 focus:ring-indigo-200"
        />
        <button type="submit" class="w-full bg-black text-white rounded-full py-3 font-semibold">Continue</button>
      </form>

      <div class="text-xs text-gray-500 mt-4">
        By continuing, you agree to our Terms and Privacy Policy.
      </div>

      <div class="text-sm text-center mt-4">
        <span v-if="isSignUp">Already have an account? <button type="button" class="text-red-500 ml-2" @click="setSignUpState(false)">Log in</button></span>
        <span v-else>Don't have an account? <button type="button" class="text-red-500 ml-2" @click="setSignUpState(true)">Sign up</button></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { inject } from 'vue'

const router = useRouter()
const route = useRoute()
const auth = inject('auth')

const isSignUp = ref(Boolean(route.state?.isSignUp) || false)
const identifier = ref('')
const password = ref('')

// Keep `isSignUp` in sync with route state so external navigations (header Log in)
// always show the correct panel.
watch(route, (r) => {
  isSignUp.value = Boolean(r.state?.isSignUp) || false
})

const setSignUpState = (value) => {
  isSignUp.value = value
  // Update the router history state so subsequent navigation preserves intent
  router.replace({ path: '/login', state: { isSignUp: value } })
}

const handleSubmit = () => {
  const name = identifier.value ? identifier.value.split('@')[0] : 'User'
  auth?.login(name)
  alert(isSignUp.value ? 'Sign up successful!' : 'Login successful!')
  // After successful login/signup, go to home.
  router.push('/')
}
</script>
