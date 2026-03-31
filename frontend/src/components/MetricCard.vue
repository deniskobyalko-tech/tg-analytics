<template>
  <div class="bg-white rounded-lg shadow p-4">
    <div class="text-sm text-gray-500">{{ label }}</div>
    <div class="text-2xl font-bold text-gray-900 mt-1">{{ formattedValue }}</div>
    <div v-if="suffix" class="text-sm text-gray-400">{{ suffix }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number
  suffix?: string
  format?: 'number' | 'percent'
}>()

const formattedValue = computed(() => {
  if (props.format === 'percent') return `${props.value}%`
  return props.value.toLocaleString('ru-RU')
})
</script>
