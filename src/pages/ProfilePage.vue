<template>
  <div class="app-root">
    <NavigationHeader />
    <div class="app-main">
      <Sidebar />
      <section class="flex-1 overflow-auto p-12">
        <div class="max-w-5xl mx-auto">
          <h1 class="text-3xl font-extrabold mb-6">Profile</h1>
          <div class="bg-white rounded-lg shadow-sm border p-6">
            <p class="text-gray-600">Profile page content coming soon.</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import NavigationHeader from '../components/NavigationHeader.vue'
import Sidebar from '../components/Sidebar.vue'
</script>
