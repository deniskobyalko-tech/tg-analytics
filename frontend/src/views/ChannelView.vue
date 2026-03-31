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

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="flex gap-4">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'pb-2 px-1 text-sm font-medium border-b-2 transition',
            activeTab === tab.id
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Tab content -->
    <GrowthChart v-if="activeTab === 'growth'" :username="channel.username" />
    <ContentAnalysis v-else-if="activeTab === 'content'" :username="channel.username" />
    <div v-else-if="activeTab === 'audience'" class="bg-white rounded-lg shadow p-6 text-center text-gray-400">
      Анализ аудитории — скоро
    </div>
    <div v-else-if="activeTab === 'ads'" class="bg-white rounded-lg shadow p-6 text-center text-gray-400">
      Анализ рекламы — скоро
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
import GrowthChart from '../components/GrowthChart.vue'
import ContentAnalysis from '../components/ContentAnalysis.vue'

const route = useRoute()
const channel = ref<Channel | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref('growth')

const tabs = [
  { id: 'growth', label: 'Динамика' },
  { id: 'content', label: 'Контент' },
  { id: 'audience', label: 'Аудитория' },
  { id: 'ads', label: 'Реклама' },
]

onMounted(async () => {
  try {
    const resp = await api.get<ApiResponse<Channel>>(`/channels/${route.params.username}`)
    if (resp.data.success && resp.data.data) {
      channel.value = resp.data.data
    } else {
      error.value = resp.data.error || 'Канал не найден'
    }
  } catch {
    error.value = 'Не удалось загрузить канал'
  } finally {
    loading.value = false
  }
})
</script>
