<template>
  <section class="flex-1 overflow-auto">
    <div class="max-w-6xl mx-auto px-6 py-12">
      <!-- Hero Section -->
      <div class="flex flex-col items-center gap-6 mb-20">
        <div class="inline-block px-4 py-2 bg-indigo-50 text-indigo-700 rounded-full text-sm font-semibold">
          AI-Powered Vehicle Detection
        </div>
        <h1 class="text-5xl md:text-6xl font-extrabold text-center leading-tight">
          Analyze Traffic with<br />
          <span class="text-indigo-600">TrackFlow AI</span>
        </h1>
        <p class="text-center text-lg text-gray-600 max-w-2xl">
          Upload CCTV footage and let our AI detect vehicles, track congestion patterns, and generate detailed analytics with interactive visualizations.
        </p>

        <div class="flex gap-4 mt-6">
          <Button @click="goToUpload" class="px-6 py-3 text-lg" variant="default">
            Try Now
          </Button>
          <Button @click="scrollToLearnMore" class="px-6 py-3 text-lg" variant="outline">
            Learn More
          </Button>
        </div>

        <div class="w-full mt-12 rounded-2xl overflow-hidden border border-gray-200 shadow-lg bg-gradient-to-br from-indigo-50 to-purple-50">
          <div class="aspect-video flex items-center justify-center">
            <div class="text-center text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 mx-auto mb-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <p class="text-lg font-medium">Demo Video Placeholder</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Features Section -->
      <div ref="learnMoreSection" class="mb-20">
        <h2 class="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <!-- Step 1 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-2">1. Upload Video</h3>
            <p class="text-gray-600">Upload your CCTV footage (MP4, 720p recommended) up to 2GB in size.</p>
          </div>

          <!-- Step 2 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-2">2. AI Processing</h3>
            <p class="text-gray-600">Our YOLOv8 AI detects and tracks vehicles frame by frame with real-time progress.</p>
          </div>

          <!-- Step 3 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-2">3. Get Insights</h3>
            <p class="text-gray-600">View detailed analytics with vehicle counts, traffic density, and interactive charts.</p>
          </div>
        </div>
      </div>

      <!-- Features List -->
      <div class="mb-20">
        <h2 class="text-3xl font-bold text-center mb-12">Key Features</h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="flex gap-4 items-start">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-lg mb-1">Real-time Progress Tracking</h4>
              <p class="text-gray-600">Monitor AI detection progress frame by frame</p>
            </div>
          </div>

          <div class="flex gap-4 items-start">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-lg mb-1">Line Crossing Detection</h4>
              <p class="text-gray-600">Define custom counting lines to track specific zones</p>
            </div>
          </div>

          <div class="flex gap-4 items-start">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-lg mb-1">Vehicle Classification</h4>
              <p class="text-gray-600">Detect cars, motorcycles, trucks, and buses</p>
            </div>
          </div>

          <div class="flex gap-4 items-start">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-lg mb-1">Interactive Visualizations</h4>
              <p class="text-gray-600">Traffic density charts and time-series graphs</p>
            </div>
          </div>

          <div class="flex gap-4 items-start">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-lg mb-1">Supports Large Files</h4>
              <p class="text-gray-600">Upload videos up to 2GB with async processing</p>
            </div>
          </div>

          <div class="flex gap-4 items-start">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-lg mb-1">History & Analytics</h4>
              <p class="text-gray-600">Save and review past analyses anytime</p>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA Section -->
      <div class="bg-gray-50 border border-gray-200 rounded-2xl p-12 text-center">
        <h2 class="text-3xl font-bold mb-4 text-gray-900">Ready to Get Started?</h2>
        <p class="text-lg mb-8 text-gray-600">Start analyzing your traffic footage in minutes</p>
        <div class="flex items-center justify-center gap-4">
          <Button @click="goToUpload" class="px-8 py-3 text-lg font-semibold" variant="default">
            Try Now
          </Button>
          <Button @click="scrollToLearnMore" class="px-8 py-3 text-lg" variant="outline">
            Learn More
          </Button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from './Button.vue'

const router = useRouter()
const learnMoreSection = ref(null)

const goToUpload = () => {
  router.push('/upload')
}

const scrollToLearnMore = () => {
  if (learnMoreSection.value) {
    learnMoreSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>
