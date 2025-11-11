<template>
  <div class="relative overflow-hidden" :class="customClass">
    <div class="h-full w-full overflow-auto rounded-[inherit]">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  class: String
})

const customClass = computed(() => props.class || '')
</script>

<style scoped>
div::-webkit-scrollbar {
  width: 10px;
}

div::-webkit-scrollbar-track {
  background: transparent;
}

div::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 9999px;
}

div::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
