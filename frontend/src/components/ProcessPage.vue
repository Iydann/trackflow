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
                  
                  <!-- Show line crossing count if available -->
                  <div v-if="vehiclesCrossedLine !== null && vehiclesCrossedLine !== undefined" class="bg-white p-4 rounded-md shadow-sm border-2 border-yellow-400">
                    <div class="text-3xl font-bold text-yellow-600">{{ vehiclesCrossedLine }}</div>
                    <div class="text-sm text-gray-600">Vehicles Crossed Line</div>
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

              <!-- Traffic Density Analysis (All vehicles) -->
              <div v-if="densityLevel" class="mt-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                <h4 class="font-semibold text-lg mb-3">Analisis Kepadatan Lalu Lintas</h4>
                <div class="flex items-center gap-6">
                  <div class="flex-1">
                    <div class="mb-2">
                      <div class="flex justify-between text-sm mb-1">
                        <span class="font-medium">Tingkat Kepadatan:</span>
                        <span class="font-bold text-indigo-700">{{ densityLevel }}</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-4">
                        <div
                          class="h-4 rounded-full transition-all"
                          :class="getDensityColor(densityPercentage)"
                          :style="{ width: `${densityPercentage}%` }"
                        />
                      </div>
                    </div>
                    <div class="text-sm text-gray-700">
                      <strong>Rata-rata:</strong> {{ avgVehiclesPerMinute }} kendaraan/menit
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-4xl font-bold text-indigo-600">{{ densityPercentage }}%</div>
                    <div class="text-xs text-gray-600">Kepadatan</div>
                  </div>
                </div>
              </div>

              <!-- Traffic Density Analysis (Crossed vehicles only) -->
              <div v-if="crossedDensityLevel" class="mt-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                <h4 class="font-semibold text-lg mb-3">Kepadatan Jalur (yang melewati garis)</h4>
                <div class="flex items-center gap-6">
                  <div class="flex-1">
                    <div class="mb-2">
                      <div class="flex justify-between text-sm mb-1">
                        <span class="font-medium">Tingkat Kepadatan:</span>
                        <span class="font-bold text-yellow-700">{{ crossedDensityLevel }}</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-4">
                        <div
                          class="h-4 rounded-full transition-all"
                          :class="getDensityColor(crossedDensityPercentage)"
                          :style="{ width: `${crossedDensityPercentage}%` }"
                        />
                      </div>
                    </div>
                    <div class="text-sm text-gray-700">
                      <strong>Rata-rata:</strong> {{ avgCrossedPerMinute }} kendaraan/menit
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-4xl font-bold text-yellow-600">{{ crossedDensityPercentage }}%</div>
                    <div class="text-xs text-gray-600">Kepadatan Jalur</div>
                  </div>
                </div>
              </div>

              <!-- Time Series Chart -->
              <div v-if="timeSeries && timeSeries.length > 0" class="mt-6 bg-white p-6 rounded-lg border">
                <TrafficChart :time-series="timeSeries" :show-crossed="vehiclesCrossedLine !== null" />
              </div>

              <!-- Per-Minute Table -->
              <div v-if="timeSeries && timeSeries.length > 0" class="mt-6 bg-white rounded-lg border">
                <div class="p-4 border-b flex justify-between items-center">
                  <h4 class="font-semibold text-lg">Data Per Menit</h4>
                  <button 
                    @click="downloadCSV" 
                    class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition text-sm font-medium"
                  >
                    📥 Download CSV
                  </button>
                </div>
                <div class="overflow-auto max-h-96">
                  <table class="w-full text-sm">
                    <thead class="bg-gray-50 sticky top-0">
                      <tr>
                        <th class="px-4 py-3 text-left font-semibold">Menit</th>
                        <th class="px-4 py-3 text-right font-semibold">Kendaraan Terdeteksi</th>
                        <th v-if="vehiclesCrossedLine !== null" class="px-4 py-3 text-right font-semibold">Melewati Garis</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, idx) in timeSeries" :key="idx" class="border-t hover:bg-gray-50">
                        <td class="px-4 py-2">{{ item.minute }}</td>
                        <td class="px-4 py-2 text-right font-medium">{{ item.vehicles }}</td>
                        <td v-if="vehiclesCrossedLine !== null" class="px-4 py-2 text-right font-medium text-yellow-700">{{ item.crossed || 0 }}</td>
                      </tr>
                    </tbody>
                  </table>
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
import { useRoute, useRouter } from 'vue-router'
import NavigationHeader from './NavigationHeader.vue'
import Sidebar from './Sidebar.vue'
import TrafficChart from './TrafficChart.vue'
import { api } from '../lib/api.js'

const route = useRoute()
const router = useRouter()
const uploadProgress = ref(0)
const detectProgress = ref(0)
const process = ref(null)
const totalVehicles = ref(null)
const vehiclesCrossedLine = ref(null)
const vehiclesByClass = ref(null)
const timeSeries = ref(null)
const avgVehiclesPerMinute = ref(null)
const densityLevel = ref(null)
const densityPercentage = ref(null)
const avgCrossedPerMinute = ref(null)
const crossedDensityLevel = ref(null)
const crossedDensityPercentage = ref(null)
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
      
      // Extract line crossing count if available
      if (data.results.vehicles_crossed_line !== null && data.results.vehicles_crossed_line !== undefined) {
        vehiclesCrossedLine.value = data.results.vehicles_crossed_line
      }
      
      // Extract time series data
      if (data.results.time_series) {
        timeSeries.value = data.results.time_series
      }
      
      // Extract density analysis
      if (data.results.avg_vehicles_per_minute !== null && data.results.avg_vehicles_per_minute !== undefined) {
        avgVehiclesPerMinute.value = data.results.avg_vehicles_per_minute
      }
      if (data.results.density_level) {
        densityLevel.value = data.results.density_level
      }
      if (data.results.density_percentage !== null && data.results.density_percentage !== undefined) {
        densityPercentage.value = data.results.density_percentage
      }

      // Extract crossed-only density analysis (if available)
      if (data.results.avg_crossed_per_minute !== null && data.results.avg_crossed_per_minute !== undefined) {
        avgCrossedPerMinute.value = data.results.avg_crossed_per_minute
      }
      if (data.results.crossed_density_level) {
        crossedDensityLevel.value = data.results.crossed_density_level
      }
      if (data.results.crossed_density_percentage !== null && data.results.crossed_density_percentage !== undefined) {
        crossedDensityPercentage.value = data.results.crossed_density_percentage
      }
      
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

const getDensityColor = (percentage) => {
  if (percentage < 30) return 'bg-green-500'
  if (percentage < 60) return 'bg-yellow-500'
  if (percentage < 80) return 'bg-orange-500'
  return 'bg-red-500'
}

const downloadCSV = () => {
  if (!timeSeries.value || timeSeries.value.length === 0) return
  
  const processName = process.value?.name || 'traffic_data'
  const filename = `${processName.replace(/\.[^/.]+$/, '')}_per_minute.csv`
  
  // Create CSV header
  let csv = 'Menit,Kendaraan Terdeteksi'
  if (vehiclesCrossedLine.value !== null) {
    csv += ',Melewati Garis'
  }
  csv += '\n'
  
  // Add data rows
  timeSeries.value.forEach(item => {
    csv += `${item.minute},${item.vehicles}`
    if (vehiclesCrossedLine.value !== null) {
      csv += `,${item.crossed || 0}`
    }
    csv += '\n'
  })
  
  // Add summary
  csv += '\nRingkasan\n'
  csv += `Total Kendaraan,${totalVehicles.value}\n`
  if (vehiclesCrossedLine.value !== null) {
    csv += `Total Melewati Garis,${vehiclesCrossedLine.value}\n`
  }
  csv += `Rata-rata per Menit (Semua),${avgVehiclesPerMinute.value}\n`
  csv += `Tingkat Kepadatan (Semua),${densityLevel.value}\n`
  csv += `Persentase Kepadatan (Semua),${densityPercentage.value}%\n`
  if (avgCrossedPerMinute.value !== null && crossedDensityLevel.value !== null && crossedDensityPercentage.value !== null) {
    csv += `Rata-rata per Menit (Melewati Garis),${avgCrossedPerMinute.value}\n`
    csv += `Tingkat Kepadatan (Melewati Garis),${crossedDensityLevel.value}\n`
    csv += `Persentase Kepadatan (Melewati Garis),${crossedDensityPercentage.value}%\n`
  }
  
  // Create download link
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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

onMounted(async () => {
  const processId = getId()
  
  // Check if we're in upload mode (redirected from DefineLine)
  if (processId === 'uploading') {
    try {
      // Retrieve upload data from sessionStorage
      const uploadDataStr = sessionStorage.getItem('trackflow_upload_data')
      const fileKey = sessionStorage.getItem('trackflow_upload_file_key')
      
      if (!uploadDataStr || !fileKey || !window[fileKey]) {
        errorMessage.value = 'Upload data not found. Please try again.'
        router.push('/upload')
        return
      }
      
      const uploadData = JSON.parse(uploadDataStr)
      const videoFile = window[fileKey]
      
      // Initialize process display
      process.value = {
        id: 'uploading',
        name: uploadData.fileName,
        status: 'uploading',
        previewUrl: null,
        resolution: '-',
        duration: 0,
        startTime: new Date().toISOString()
      }
      
      processingStatus.value = 'Uploading video...'
      uploadProgress.value = 0
      detectProgress.value = 0
      
      // Start upload with progress tracking
      const result = await api.uploadAndProcess(
        videoFile,
        uploadData.lineCoordinates,
        (percent) => {
          uploadProgress.value = percent
          if (percent < 100) {
            processingStatus.value = `Uploading video... ${percent}%`
          } else {
            processingStatus.value = 'Upload complete. Processing...'
          }
        }
      )
      
      // Clean up sessionStorage and window global
      sessionStorage.removeItem('trackflow_upload_data')
      sessionStorage.removeItem('trackflow_upload_file_key')
      delete window[fileKey]
      
      // Navigate to actual process ID and start polling
      uploadProgress.value = 100
      router.replace(`/process/${result.processId}`)
      pollProcessStatus(result.processId)
      
    } catch (error) {
      console.error('Upload error:', error)
      errorMessage.value = error.response?.data?.error || 'Upload failed. Please try again.'
      processingStatus.value = 'Failed'
      
      // Clean up on error
      sessionStorage.removeItem('trackflow_upload_data')
      const fileKey = sessionStorage.getItem('trackflow_upload_file_key')
      if (fileKey) {
        delete window[fileKey]
        sessionStorage.removeItem('trackflow_upload_file_key')
      }
    }
  } else {
    // Normal process loading
    loadProcess(processId)
  }

  watch(() => route.params.id, (newId) => {
    if (newId !== 'uploading') {
      loadProcess(newId)
    }
  })
})
</script>
