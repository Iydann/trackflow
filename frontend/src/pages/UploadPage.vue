<template>
  <div class="app-root">
    <NavigationHeader />
    <div class="app-main">
      <Sidebar />
      <UploadSection />
    </div>
  </div>
</template>

<script setup>
import NavigationHeader from '../components/NavigationHeader.vue'
import Sidebar from '../components/Sidebar.vue'
import UploadSection from '../components/UploadSection.vue'
</script>
