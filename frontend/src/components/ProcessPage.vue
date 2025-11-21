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
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="font-semibold text-lg">{{ process?.name }}</h3>
                  <span v-if="process?.status === 'completed'" class="px-2 py-1 text-xs font-semibold bg-green-100 text-green-700 rounded-full">
                    ✓ Completed
                  </span>
                </div>
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
            <div v-if="errorMessage" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {{ errorMessage }}
            </div>

            <div v-if="processingStatus" class="p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700">
              <strong>Status:</strong> {{ processingStatus }}
            </div>

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
              <h3 class="font-semibold text-lg mb-4">Detection Results</h3>
              
              <div v-if="totalVehicles !== null" class="mb-6">
                <div class="grid grid-cols-3 gap-6">
                  <div class="bg-white p-4 rounded-md shadow-sm">
                    <div class="text-3xl font-bold text-blue-600">{{ totalVehicles }}</div>
                    <div class="text-sm text-gray-600">Total Vehicles Detected</div>
                  </div>
                  <div class="bg-white p-4 rounded-md shadow-sm">
                    <div class="text-2xl font-bold text-green-600">
                      {{ vehiclesByClass?.car || 0 }}
                    </div>
                    <div class="text-sm text-gray-600">Cars (Mobil)</div>
                  </div>
                  <div class="bg-white p-4 rounded-md shadow-sm">
                    <div class="text-2xl font-bold text-pink-600">
                      {{ vehiclesByClass?.motorcycle || 0 }}
                    </div>
                    <div class="text-sm text-gray-600">Motorcycles (Motor)</div>
                  </div>
                  <div class="bg-white p-4 rounded-md shadow-sm">
                    <div class="text-2xl font-bold text-purple-600">
                      {{ vehiclesByClass?.truck || 0 }}
                    </div>
                    <div class="text-sm text-gray-600">Trucks (Truk)</div>
                  </div>
                  <div class="bg-white p-4 rounded-md shadow-sm">
                    <div class="text-2xl font-bold text-orange-600">
                      {{ vehiclesByClass?.bus || 0 }}
                    </div>
                    <div class="text-sm text-gray-600">Buses (Bus)</div>
                  </div>
                </div>
              </div>

              <!-- Debug Info -->
              <div v-if="apiResponse" class="mt-6 p-4 bg-white rounded border">
                <details>
                  <summary class="cursor-pointer font-medium text-gray-700">Debug Info (API Response)</summary>
                  <pre class="mt-2 text-xs overflow-auto max-h-64 bg-gray-50 p-3 rounded">{{ JSON.stringify(apiResponse, null, 2) }}</pre>
                </details>
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
import { api } from '../lib/api.js'

const route = useRoute()
const uploadProgress = ref(0)
const detectProgress = ref(0)
const process = ref(null)
const totalVehicles = ref(null)
const vehiclesByClass = ref(null)
const processingStatus = ref('Initializing...')
const errorMessage = ref(null)
const apiResponse = ref(null)

const getId = () => route.params?.id

const loadProcess = async (id) => {
  if (!id) return
  try {
    const data = await api.getProcess(id)
    process.value = {
      id: data.id,
      name: data.name,
      status: data.status,
      previewUrl: null,
      resolution: data.results?.video_info?.resolution || '-',
      duration: data.results?.video_info?.duration_seconds || 0,
      startTime: data.created_at
    }
    
    if (data.status === 'completed' && data.results) {
      uploadProgress.value = 100
      detectProgress.value = 100
      totalVehicles.value = data.total_vehicles || 0
      
      const typeCounts = data.results.vehicle_type_counts || {}
      vehiclesByClass.value = {
        car: typeCounts.Mobil || typeCounts.car || 0,
        motorcycle: typeCounts.Motor || typeCounts.motorcycle || 0,
        truck: typeCounts.Truk || typeCounts.truck || 0,
        bus: typeCounts.Bus || typeCounts.bus || 0
      }
      
      processingStatus.value = `Completed! Found ${totalVehicles.value} vehicles.`
      apiResponse.value = { statistics: data.results }
    } else if (data.status === 'processing') {
      pollProcessStatus(id)
    }
  } catch (e) {
    console.error('Error loading process:', e)
  }
}

const pollProcessStatus = async (id) => {
  const interval = setInterval(async () => {
    try {
      const data = await api.getProcess(id)
      
      if (data.status === 'completed') {
        clearInterval(interval)
        loadProcess(id)
      } else if (data.status === 'failed') {
        clearInterval(interval)
        errorMessage.value = data.error_message || 'Processing failed'
        processingStatus.value = 'Failed'
      }
      
      // Simulate progress
      if (uploadProgress.value < 100) {
        uploadProgress.value = Math.min(100, uploadProgress.value + 5)
      } else if (detectProgress.value < 95) {
        detectProgress.value = Math.min(95, detectProgress.value + 3)
      }
    } catch (e) {
      console.error('Polling error:', e)
    }
  }, 2000)
  
  onUnmounted(() => clearInterval(interval))
}

const formatDuration = (s) => {
  if (!s) return '-'
  const mins = Math.floor(s / 60)
  const secs = String(Math.floor(s % 60)).padStart(2, '0')
  return `${mins}:${secs}`
}

const moveToHistory = (processItem) => {
  // Backend handles this automatically
}

const processVideoWithAI = async (videoFile, processId) => {
  // Backend now handles AI processing automatically
  processingStatus.value = 'Processing on server...'
  uploadProgress.value = 10
  
  // Poll for status updates
  pollProcessStatus(processId)
}

onMounted(() => {
  const processId = getId()
  loadProcess(processId)

  watch(() => route.params.id, (newId) => {
    loadProcess(newId)
  })
})
</script>
