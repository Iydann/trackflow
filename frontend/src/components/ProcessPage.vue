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

const route = useRoute()
const uploadProgress = ref(0)
const detectProgress = ref(0)
const process = ref(null)
const totalVehicles = ref(null)
const vehiclesByClass = ref(null)
const processingStatus = ref('Initializing...')
const errorMessage = ref(null)
const apiResponse = ref(null)

const API_BASE_URL = 'http://localhost:8000'

const getId = () => route.params?.id

const loadProcess = (id) => {
  process.value = null
  if (route.state && route.state.id) {
    process.value = route.state
    return
  }
  if (!id) return
  try {
    // Try to load from processes first
    const raw = localStorage.getItem('trackflow_processes') || '[]'
    const arr = JSON.parse(raw)
    let found = arr.find((p) => String(p.id) === String(id))
    
    // If not in processes, try history
    if (!found) {
      const historyRaw = localStorage.getItem('trackflow_history') || '[]'
      const historyArr = JSON.parse(historyRaw)
      found = historyArr.find((p) => String(p.id) === String(id))
    }
    
    if (found) {
      process.value = found
      
      // If already completed, set progress to 100 and show results
      if (found.status === 'completed' && found.results) {
        uploadProgress.value = 100
        detectProgress.value = 100
        totalVehicles.value = found.results.unique_vehicles || found.results.total_vehicles || 0
        
        const typeCounts = found.results.vehicle_type_counts || found.results.vehicles_by_class || {}
        vehiclesByClass.value = {
          car: typeCounts.Mobil || typeCounts.car || 0,
          motorcycle: typeCounts.Motor || typeCounts.motorcycle || 0,
          truck: typeCounts.Truk || typeCounts.truck || 0,
          bus: typeCounts.Bus || typeCounts.bus || 0
        }
        
        processingStatus.value = `Completed! Found ${totalVehicles.value} vehicles.`
        apiResponse.value = { statistics: found.results }
      }
    }
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

const moveToHistory = (processItem) => {
  try {
    // Add to history
    const historyRaw = localStorage.getItem('trackflow_history') || '[]'
    const historyArr = JSON.parse(historyRaw)
    
    // Check if already in history
    const existsInHistory = historyArr.some(h => h.id === processItem.id)
    if (!existsInHistory) {
      historyArr.unshift(processItem)
      localStorage.setItem('trackflow_history', JSON.stringify(historyArr))
      console.log('Moved to history:', processItem.id)
    }
    
    // Remove from processes
    const processRaw = localStorage.getItem('trackflow_processes') || '[]'
    const processArr = JSON.parse(processRaw)
    const filtered = processArr.filter(p => p.id !== processItem.id)
    localStorage.setItem('trackflow_processes', JSON.stringify(filtered))
    console.log('Removed from processes:', processItem.id)
    
    // Trigger storage event for sidebar to update
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'trackflow_processes',
      newValue: JSON.stringify(filtered)
    }))
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'trackflow_history',
      newValue: JSON.stringify(historyArr)
    }))
  } catch (e) {
    console.error('Failed to move to history:', e)
  }
}

const processVideoWithAI = async (videoFile, processId) => {
  try {
    processingStatus.value = 'Uploading video to AI server...'
    uploadProgress.value = 0
    
    // Create form data
    const formData = new FormData()
    formData.append('file', videoFile)
    formData.append('mode', 'track')
    formData.append('confidence', '0.25')
    formData.append('save_video', 'true')
    formData.append('draw_trails', 'true')

    // Simulate upload progress during actual upload
    const uploadInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 3
      }
    }, 300)

    console.log('Uploading video to AI backend...')

    // Upload and process video
    const response = await fetch(`${API_BASE_URL}/process`, {
      method: 'POST',
      body: formData
    })

    clearInterval(uploadInterval)
    uploadProgress.value = 100

    console.log('Response status:', response.status)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || `API error: ${response.status}`)
    }

    const result = await response.json()
    console.log('API Response:', result)
    
    // Store full response for debugging
    apiResponse.value = result
    
    processingStatus.value = 'AI detection completed! Processing results...'
    
    // Start detection progress animation
    detectProgress.value = 0
    const detectInterval = setInterval(() => {
      if (detectProgress.value < 100) {
        detectProgress.value += 5
      } else {
        clearInterval(detectInterval)
      }
    }, 50)

    // Wait a bit for animation
    await new Promise(resolve => setTimeout(resolve, 1000))
    detectProgress.value = 100

    console.log('Statistics:', result.statistics)

    // Update results immediately from API response
    if (result.statistics) {
      // Backend returns 'unique_vehicles' not 'total_vehicles'
      totalVehicles.value = result.statistics.unique_vehicles || result.statistics.total_vehicles || 0
      
      // Backend returns 'vehicle_type_counts' not 'vehicles_by_class'
      const typeCounts = result.statistics.vehicle_type_counts || result.statistics.vehicles_by_class || {}
      
      // Map vehicle type names to lowercase keys
      vehiclesByClass.value = {
        car: typeCounts.Mobil || typeCounts.car || 0,
        motorcycle: typeCounts.Motor || typeCounts.motorcycle || 0,
        truck: typeCounts.Truk || typeCounts.truck || 0,
        bus: typeCounts.Bus || typeCounts.bus || 0
      }
      
      processingStatus.value = `Detection completed! Found ${totalVehicles.value} vehicles.`
      
      console.log('Total vehicles detected:', totalVehicles.value)
      console.log('Vehicles by class:', vehiclesByClass.value)
      console.log('Raw statistics:', result.statistics)
      
      // Update localStorage with results
      try {
        const raw = localStorage.getItem('trackflow_processes') || '[]'
        const arr = JSON.parse(raw)
        const idx = arr.findIndex((p) => p.id === processId)
        if (idx >= 0) {
          arr[idx].status = 'completed'
          arr[idx].results = result.statistics
          arr[idx].output_video = result.output_video_path
          arr[idx].completedAt = new Date().toISOString()
          localStorage.setItem('trackflow_processes', JSON.stringify(arr))
          console.log('Updated localStorage with results')
          
          // Move to history after completion
          moveToHistory(arr[idx])
        }
      } catch (e) {
        console.error('Failed to update localStorage:', e)
      }
    } else {
      console.warn('No statistics in response')
      errorMessage.value = 'Detection completed but no statistics returned'
    }

    return result
  } catch (error) {
    console.error('AI Processing error:', error)
    errorMessage.value = `Processing failed: ${error.message}`
    processingStatus.value = 'Error occurred'
    return null
  }
}

onMounted(() => {
  loadProcess(getId())

  // react to param changes
  watch(() => route.params.id, (newId) => {
    loadProcess(newId)
  })

  // Get video file from route state or window storage
  let videoFile = route.state?.videoFile
  
  if (!videoFile) {
    try {
      const processKey = sessionStorage.getItem('trackflow_process_key')
      if (processKey && window[processKey]) {
        videoFile = window[processKey]
      }
    } catch (e) {
      // ignore
    }
  }

  // Only start processing if not already completed
  const isCompleted = process.value?.status === 'completed'
  
  if (isCompleted) {
    console.log('Process already completed, skipping AI processing')
  } else if (videoFile) {
    const processId = getId()
    processVideoWithAI(videoFile, processId)
  } else {
    // Fallback to fake progress if no file found
    errorMessage.value = 'No video file found. Using simulation mode.'
    
    let upTimer = setInterval(() => {
      uploadProgress.value = Math.min(100, uploadProgress.value + 2)
    }, 150)

    let detTimer = setInterval(() => {
      if (uploadProgress.value < 100) return
      detectProgress.value = Math.min(100, detectProgress.value + 1)
    }, 200)

    setTimeout(() => {
      clearInterval(upTimer)
      clearInterval(detTimer)
    }, 15000)
  }
})

onUnmounted(() => {
  // cleanup handled by onMounted return
})
</script>
