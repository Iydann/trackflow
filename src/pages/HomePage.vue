<template>
  <div class="app-root">
    <NavigationHeader />
    <div class="app-main">
      <Sidebar />
      <MainContent v-if="!showUpload" />
      <UploadSection v-else />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavigationHeader from '../components/NavigationHeader.vue'
import Sidebar from '../components/Sidebar.vue'
import MainContent from '../components/MainContent.vue'
import UploadSection from '../components/UploadSection.vue'

const route = useRoute()
const showUpload = computed(() => route.path === '/upload')
</script>
