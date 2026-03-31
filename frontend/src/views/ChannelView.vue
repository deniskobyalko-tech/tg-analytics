<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
  <div v-else-if="error" class="text-center py-12 text-red-500">{{ error }}</div>
  <div v-else-if="channel" class="space-y-6">
    <ChannelHeader :channel="channel" />

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <MetricCard label="Подписчики" :value="channel.subscribers_count" />
      <MetricCard label="Ср. просмотры" :value="channel.avg_views" />
      <MetricCard label="ER" :value="channel.er" format="percent" />
      <MetricCard label="Постов/нед." :value="channel.posts_per_week" />
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <p class="text-gray-400 text-center">Подробная аналитика скоро будет</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api, type ApiResponse } from '../api/client'
import type { Channel } from '../stores/channels'
import ChannelHeader from '../components/ChannelHeader.vue'
import MetricCard from '../components/MetricCard.vue'

const route = useRoute()
const channel = ref<Channel | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const resp = await api.get<ApiResponse<Channel>>(`/channels/${route.params.username}`)
    if (resp.data.success && resp.data.data) {
      channel.value = resp.data.data
    } else {
      error.value = resp.data.error || 'Channel not found'
    }
  } catch {
    error.value = 'Не удалось загрузить канал'
  } finally {
    loading.value = false
  }
})
</script>
