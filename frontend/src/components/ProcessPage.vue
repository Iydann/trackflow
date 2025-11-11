<template>
  <div class="app-root">
    <NavigationHeader />
    <div class="app-main">
      <Sidebar />
      <section class="main-content">
        <div class="main-inner">
          <h1 class="font-extrabold text-black text-3xl mb-6">
            {{ process ? process.name : 'Processing' }}
          </h1>

          <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <div class="flex gap-4">
              <div class="w-48 h-32 bg-gray-100 rounded-md overflow-hidden flex-shrink-0">
                <img
                  v-if="process?.previewUrl"
                  :src="process.previewUrl"
                  alt="preview"
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-500">
                  No preview
                </div>
              </div>
              <div class="flex-1">
                <h3 class="font-semibold text-lg mb-2">{{ process?.name }}</h3>
                <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>
                    <span class="font-medium">Status:</span>
                    <span :class="process?.status === 'processing' ? 'text-blue-600' : 'text-green-600'" class="ml-2">
                      {{ process?.status ?? 'processing' }}
                    </span>
                  </div>
                  <div>
                    <span class="font-medium">Duration:</span>
                    <span class="ml-2">{{ formatDuration(process?.duration) }}</span>
                  </div>
                  <div>
                    <span class="font-medium">Resolution:</span>
                    <span class="ml-2">{{ process?.resolution ?? '-' }}</span>
                  </div>
                  <div>
                    <span class="font-medium">Start:</span>
                    <span class="ml-2">{{ process?.startTime ? new Date(process.startTime).toLocaleString() : '-' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div>
              <div class="flex justify-between mb-2">
                <span class="font-medium">Uploading video</span>
                <span>{{ uploadProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  :style="{ width: `${uploadProgress}%` }"
                />
              </div>
            </div>

            <div>
              <div class="flex justify-between mb-2">
                <span class="font-medium">Running detection</span>
                <span>{{ detectProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="bg-green-600 h-3 rounded-full transition-all duration-300"
                  :style="{ width: `${detectProgress}%` }"
                />
              </div>
            </div>

            <div v-if="detectProgress >= 100" class="mt-8 p-6 bg-gray-50 rounded-lg">
              <h3 class="font-semibold text-lg mb-4">Detection Results (sample)</h3>
              <div class="grid grid-cols-3 gap-6">
                <div class="bg-white p-4 rounded-md shadow-sm">
                  <div class="text-2xl font-bold text-blue-600">—</div>
                  <div class="text-sm text-gray-600">Total Vehicles</div>
                </div>
                <div class="bg-white p-4 rounded-md shadow-sm">
                  <div class="text-2xl font-bold text-green-600">—</div>
                  <div class="text-sm text-gray-600">Peak Hour Count</div>
                </div>
                <div class="bg-white p-4 rounded-md shadow-sm">
                  <div class="text-2xl font-bold text-pink-600">—</div>
                  <div class="text-sm text-gray-600">Avg/Hour</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import NavigationHeader from './NavigationHeader.vue'
import Sidebar from './Sidebar.vue'

const route = useRoute()
const uploadProgress = ref(0)
const detectProgress = ref(0)
const process = ref(null)

const getId = () => route.params?.id

const loadProcess = (id) => {
  process.value = null
  if (route.state && route.state.id) {
    process.value = route.state
    return
  }
  if (!id) return
  try {
    const raw = localStorage.getItem('trackflow_processes') || '[]'
    const arr = JSON.parse(raw)
    const found = arr.find((p) => String(p.id) === String(id))
    if (found) process.value = found
  } catch {
    // ignore
  }
}

const formatDuration = (s) => {
  if (!s) return '-'
  const mins = Math.floor(s / 60)
  const secs = String(Math.floor(s % 60)).padStart(2, '0')
  return `${mins}:${secs}`
}

onMounted(() => {
  loadProcess(getId())

  // react to param changes
  watch(() => route.params.id, (newId) => {
    loadProcess(newId)
  })

  let upTimer
  let detTimer

  upTimer = setInterval(() => {
    uploadProgress.value = Math.min(100, uploadProgress.value + 2)
  }, 150)

  detTimer = setInterval(() => {
    if (uploadProgress.value < 100) return
    detectProgress.value = Math.min(100, detectProgress.value + 1)
  }, 200)

  return () => {
    if (upTimer) clearInterval(upTimer)
    if (detTimer) clearInterval(detTimer)
  }
})

onUnmounted(() => {
  // cleanup handled by onMounted return
})
</script>
