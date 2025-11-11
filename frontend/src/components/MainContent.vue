<template>
  <section class="flex-1 overflow-auto p-12">
    <div class="max-w-5xl mx-auto">
      <ScrollArea>
        <div class="flex flex-col items-center gap-6">
          <h1 class="text-5xl font-extrabold text-center">Vehicle Detection, Congestion Timeline Maker</h1>
          <p class="text-center text-lg text-gray-700 max-w-2xl">
            Upload 720p CCTV video in mp4 format, the system will detect objects with YOLO and LLM to compile a timeline table, the timeline will be visualized with a graph
          </p>

          <div class="flex gap-4 mt-4">
            <Button class="btn-try" variant="default">Try Now</Button>
            <Button class="btn-learn" variant="outline">Learn more</Button>
          </div>

          <div class="w-full mt-8 grid gap-8">
            <div class="w-full h-96 rounded-2xl bg-gray-100"></div>
            <div class="w-full h-96 rounded-2xl bg-gray-100"></div>
          </div>
        </div>
      </ScrollArea>
    </div>
  </section>
</template>

<script setup>
import Button from './Button.vue'
import ScrollArea from './ScrollArea.vue'
</script>
