<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
</script>

<template>
  <div class="prose">
    <h1 class="text-2xl font-bold">{{ msg }}</h1>

    <div class="mt-4 p-4 bg-white rounded-md shadow-sm">
      <button type="button" class="px-3 py-2 bg-indigo-600 text-white rounded-md" @click="count++">count is {{ count }}</button>
      <p class="mt-2">
        Edit <code>components/HelloWorld.vue</code> to test HMR
      </p>
    </div>

    <p class="mt-4">
      Check out <a class="text-blue-600 underline" href="https://vuejs.org/guide/quick-start.html#local" target="_blank">create-vue</a>, the official Vue + Vite starter
    </p>
    <p>
      Learn more about IDE Support for Vue in the <a class="text-blue-600 underline" href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support" target="_blank">Vue Docs Scaling up Guide</a>.
    </p>
    <p class="text-sm text-gray-500">Click on the Vite and Vue logos to learn more</p>
  </div>
</template>
