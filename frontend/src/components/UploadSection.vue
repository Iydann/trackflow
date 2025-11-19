<template>
  <section class="py-8 flex-1">
    <div class="w-full px-6">
      <ScrollArea>
        <div class="upload-content">
          <h1 class="text-3xl font-extrabold mb-3">Start Your Traffic Density Analysis</h1>

          <p class="text-gray-600 mb-6">
            Welcome to TrackFlow. Upload a 720p video (MP4) recorded from a stable, unobstructed
            camera angle. Before upload you'll draw a count line with 2 point to start the analysis.
          </p>

          <div class="p-4 bg-white rounded-xl shadow-sm requirements-card">
            <h2 class="text-lg font-bold mb-2">Requirements</h2>
            <ul class="list-disc pl-5 text-sm text-gray-700">
              <li>Resolution: 1280x720 (720p)</li>
              <li>Formats: .mp4</li>
              <li>Stable camera, minimal shake, clear lighting</li>
              <li>Max file size: .. GB</li>
            </ul>
          </div>

          <h2 class="text-xl font-semibold mt-6">Upload Video</h2>

          <div class="upload-block mt-6">
            <input
              ref="fileInputRef"
              type="file"
              accept="video/mp4"
              class="visually-hidden"
              @change="onFileChange"
            />

            <div
              v-if="!previewDataUrl"
              @dragover.prevent
              @dragenter.prevent="isDragActive = true"
              @dragleave.prevent="isDragActive = false"
              @drop.prevent="onDrop"
              @click="openFilePicker"
              role="button"
              tabindex="0"
              :class="[ 'w-full rounded-xl border-2 border-dashed border-gray-200 p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors duration-200 group', isDragActive ? 'bg-gray-50 border-indigo-300 ring-2 ring-indigo-200' : 'hover:bg-gray-50 hover:shadow-sm' ]"
            >
              <div class="text-5xl transform transition-transform duration-200 group-hover:scale-110">🎬</div>
              <div class="mt-3 text-lg font-semibold">Click to select the video to upload</div>
              <div class="text-sm text-gray-500 mt-1">Or drag &amp; drop video files here</div>
              <div class="text-xs text-gray-400 mt-2">Limit 2GB per file mp4.</div>
            </div>

            <div v-if="previewDataUrl" class="bg-white rounded-xl shadow p-4 video-preview-card">
              <div class="flex items-start gap-6 video-preview-inner">
                <img :src="previewDataUrl" alt="first frame" class="w-96 h-auto rounded-md video-thumb" />
                <div class="flex flex-col gap-3">
                  <Button variant="default" class="px-4 py-2" @click="startDefine">Start defining counting line</Button>
                  <Button variant="destructive" class="px-4 py-2" @click="removeVideo">Delete video</Button>
                </div>
              </div>
            </div>

            <!-- removed duplicate upload card and define-line section per user request -->
          </div>

        </div>
      </ScrollArea>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Button from './Button.vue'
import ScrollArea from './ScrollArea.vue'

const router = useRouter()
const fileInputRef = ref(null)
const videoUrl = ref(null)
const previewDataUrl = ref(null)
const isDragActive = ref(false)
const currentVideoFile = ref(null)

const openFilePicker = () => {
  fileInputRef.value?.click()
}

const handleFile = (file) => {
  if (!file) return

  currentVideoFile.value = file
  const url = URL.createObjectURL(file)
  videoUrl.value = url

  const video = document.createElement('video')
  video.src = url
  video.crossOrigin = 'anonymous'
  video.muted = true
  video.playsInline = true

  const capture = () => {
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 360
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      try {
        previewDataUrl.value = canvas.toDataURL('image/png')
      } catch {
        previewDataUrl.value = null
      }
    }
    video.removeEventListener('seeked', capture)
    video.pause()
  }

  const onLoaded = () => {
    video.currentTime = 0.001
    video.addEventListener('seeked', capture)
  }

  video.addEventListener('loadedmetadata', onLoaded)
  if (video.readyState >= 1) onLoaded()
}

const onFileChange = (e) => {
  const file = e.target.files?.[0] || null
  handleFile(file)
}

const onDrop = (e) => {
  isDragActive.value = false
  const file = e.dataTransfer.files?.[0] || null
  if (file) handleFile(file)
}

const removeVideo = () => {
  if (videoUrl.value) URL.revokeObjectURL(videoUrl.value)
  videoUrl.value = null
  previewDataUrl.value = null
}

const startDefine = () => {
  // Persist state to sessionStorage as a fallback for the define page
  try {
    // Store file reference with unique key
    const fileKey = `video_${Date.now()}`
    window[fileKey] = currentVideoFile.value
    
    sessionStorage.setItem(
      'trackflow_define_state',
      JSON.stringify({ 
        videoUrl: videoUrl.value, 
        previewDataUrl: previewDataUrl.value,
        fileKey: fileKey
      })
    )
  } catch (e) {
    // ignore
  }

  router.push({
    path: '/upload/define',
    state: { 
      videoUrl: videoUrl.value, 
      previewDataUrl: previewDataUrl.value,
      videoFile: currentVideoFile.value
    }
  })
}

onMounted(() => {
  // Cleanup on unmount
})

onUnmounted(() => {
  if (videoUrl.value) URL.revokeObjectURL(videoUrl.value)
})
</script>
