<template>
  <div class="app-root">
    <NavigationHeader />
    <div class="app-main">
      <Sidebar />

      <section class="main-content">
        <div class="main-inner">
          <h1 class="font-extrabold text-black text-2xl mb-4">Start defining counting line</h1>
          <p class="text-sm text-gray-600 mb-4">Click twice on the image to place the start and end points of the counting line.</p>

          <div class="w-full bg-black flex items-center justify-center rounded-lg overflow-hidden define-canvas-wrap">
            <canvas
              ref="canvasRef"
              @click="onCanvasClick"
              class="define-canvas"
              style="cursor: crosshair; display:block;"
            />
          </div>

          <div class="mt-8 flex items-center gap-3">
            <Button @click="confirm" class="px-4 py-2 bg-black text-white rounded hover:bg-black/90">
              Confirm
            </Button>
            <Button @click="goBack" variant="outline" class="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50">
              Back
            </Button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Button from './Button.vue'
import NavigationHeader from './NavigationHeader.vue'
import Sidebar from './Sidebar.vue'

const router = useRouter()
const route = useRoute()
const canvasRef = ref(null)
const imgRef = ref(null)
const points = ref([])

// Try to obtain preview/video either from route.state or from sessionStorage fallback
const routeState = route.state || {}
let previewDataUrl = routeState.previewDataUrl
let videoUrl = routeState.videoUrl
let videoFile = routeState.videoFile
let fileKey = null

if (!previewDataUrl && !videoUrl) {
  try {
    const raw = sessionStorage.getItem('trackflow_define_state')
    if (raw) {
      const parsed = JSON.parse(raw)
      previewDataUrl = parsed.previewDataUrl
      videoUrl = parsed.videoUrl
      fileKey = parsed.fileKey
      if (fileKey && window[fileKey]) {
        videoFile = window[fileKey]
      }
    }
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  const img = new Image()
  img.crossOrigin = 'anonymous'

  const canvas = canvasRef.value
  const setupCanvasSize = (w, h) => {
    if (!canvas) return
    canvas.width = w
    canvas.height = h
    // keep canvas responsive in layout
    canvas.style.maxWidth = '100%'
    canvas.style.height = 'auto'
  }

  img.onload = () => {
    imgRef.value = img
    setupCanvasSize(img.width, img.height)
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    redraw()
  }

  if (previewDataUrl) {
    img.src = previewDataUrl
  } else if (videoUrl) {
    const video = document.createElement('video')
    video.src = videoUrl
    video.muted = true
    video.playsInline = true
    video.addEventListener('loadeddata', () => {
      setupCanvasSize(video.videoWidth, video.videoHeight)
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      redraw()
    })
    try { video.load() } catch (e) { /* ignore load errors */ }
  }
})

const redraw = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  if (imgRef.value) ctx.drawImage(imgRef.value, 0, 0, canvas.width, canvas.height)

  ctx.lineWidth = 4
  ctx.strokeStyle = '#22c55e'
  ctx.fillStyle = '#22c55e'

  if (points.value.length === 1) {
    const p = points.value[0]
    ctx.beginPath()
    ctx.arc(p.x, p.y, 6, 0, Math.PI * 2)
    ctx.fill()
  } else if (points.value.length >= 2) {
    const p1 = points.value[0]
    const p2 = points.value[1]
    ctx.beginPath()
    ctx.moveTo(p1.x, p1.y)
    ctx.lineTo(p2.x, p2.y)
    ctx.stroke()
    ctx.beginPath()
    ctx.arc(p1.x, p1.y, 6, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(p2.x, p2.y, 6, 0, Math.PI * 2)
    ctx.fill()
  }
}

const onCanvasClick = (e) => {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = ((e.clientX - rect.left) / rect.width) * canvas.width
  const y = ((e.clientY - rect.top) / rect.height) * canvas.height

  if (points.value.length >= 2) {
    points.value = [{ x, y }]
  } else {
    points.value.push({ x, y })
  }

  redraw()
}

const reset = () => {
  points.value = []
  redraw()
}

const confirm = () => {
  if (points.value.length < 2) {
    alert('Please select two points first.')
    return
  }

  const processId = `process-${Date.now()}`
  const startTime = new Date().toISOString()

  const processObj = {
    id: processId,
    name: videoFile?.name || 'Uploaded Video',
    timestamp: new Date().toLocaleString(),
    status: 'processing',
    path: `/process/${processId}`,
    videoUrl: videoUrl || null,
    previewUrl: previewDataUrl || null,
    duration: 0,
    resolution: '',
    line: {
      start: [points.value[0].x, points.value[0].y],
      end: [points.value[1].x, points.value[1].y]
    },
    startTime
  }

  try {
    const existing = JSON.parse(localStorage.getItem('trackflow_processes') || '[]')
    existing.unshift(processObj)
    localStorage.setItem('trackflow_processes', JSON.stringify(existing))
    
    // Trigger storage event for sidebar to update
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'trackflow_processes',
      newValue: JSON.stringify(existing)
    }))
  } catch {
    // ignore
  }

  // Store video file and line for processing
  if (videoFile) {
    const processKey = `process_${processId}`
    window[processKey] = videoFile
    try {
      sessionStorage.setItem('trackflow_process_key', processKey)
      sessionStorage.setItem('trackflow_process_line', JSON.stringify(processObj.line))
    } catch (e) {
      // ignore
    }
  }

  router.push({
    path: `/process/${processId}`,
    state: { ...processObj, videoFile: videoFile }
  })

  if (videoUrl) {
    const v = document.createElement('video')
    v.src = videoUrl
    v.addEventListener('loadedmetadata', () => {
      try {
        const raw = localStorage.getItem('trackflow_processes') || '[]'
        const arr = JSON.parse(raw)
        const idx = arr.findIndex((p) => p.id === processId)
        if (idx >= 0) {
          arr[idx].duration = Math.floor(v.duration)
          arr[idx].resolution = `${v.videoWidth}x${v.videoHeight}`
          localStorage.setItem('trackflow_processes', JSON.stringify(arr))
        }
      } catch {
        // ignore
      }
    })
    try {
      v.load()
    } catch {
      // ignore
    }
  }
}

const goBack = () => {
  router.back()
}
</script>
