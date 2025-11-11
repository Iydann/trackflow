<template>
  <button
    :class="[baseClass, variantClass, sizeClass, customClass]"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'].includes(v)
  },
  size: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'sm', 'lg', 'icon'].includes(v)
  },
  class: String
})

const baseClass = 'inline-flex items-center justify-center gap-2 border-0 cursor-pointer transition-transform duration-150 ease-out'

const variantClass = computed(() => {
  const variants = {
    default: 'bg-black text-white rounded-full font-semibold shadow-md hover:bg-black/90 active:translate-y-0 active:shadow-sm',
    destructive: 'bg-red-600 text-white rounded-full font-semibold hover:bg-red-700',
    outline: 'bg-white text-black border border-black rounded-full hover:bg-black hover:text-white',
    secondary: 'bg-gray-100 text-black rounded-full hover:bg-gray-200',
    ghost: 'bg-transparent hover:bg-black/5',
    link: 'bg-transparent underline text-blue-600 p-0'
  }
  return variants[props.variant] || variants.default
})

const sizeClass = computed(() => {
  const sizes = {
    default: 'h-10 px-5',
    sm: 'h-9 px-3 text-sm',
    lg: 'h-12 px-6 text-lg',
    icon: 'h-10 w-10 p-0'
  }
  return sizes[props.size] || sizes.default
})

const customClass = computed(() => props.class || '')
</script>
