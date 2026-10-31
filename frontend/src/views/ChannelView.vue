<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
  <div v-else-if="error" class="text-center py-12 text-red-500">{{ error }}</div>
  <div v-else-if="channel" class="space-y-6">
    <ChannelHeader :channel="channel" />

    <!-- Action buttons -->
    <div class="flex gap-3">
      <button
        @click="toggleWatchlist"
        :disabled="watchlistLoading"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium transition',
          isTracked
            ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
            : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
        ]"
      >
        {{ isTracked ? 'В отслеживании' : 'Отслеживать' }}
      </button>
      <a
        :href="`/api/channels/${channel.username}/export?format=csv`"
        class="px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition"
      >
        CSV (посты)
      </a>
      <a
        :href="`/api/channels/${channel.username}/export?format=csv&type=metrics`"
        class="px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition"
      >
        CSV (метрики)
      </a>
      <button
        v-if="!extendedData"
        @click="loadExtended"
        :disabled="extendedLoading"
        class="px-4 py-2 rounded-lg text-sm font-medium bg-purple-100 text-purple-700 hover:bg-purple-200 transition disabled:opacity-50"
      >
        {{ extendedLoading ? 'Загрузка...' : 'Расширенная статистика' }}
      </button>
    </div>

    <!-- Extended stats -->
    <p v-if="extendedError" class="text-sm text-red-500">{{ extendedError }}</p>
    <BotConnectBanner
      v-if="extendedData && !extendedData.bot_connected"
      :bot-username="extendedData.bot_username || 'tg_analytics_stats_bot'"
    />
    <ExtendedStats v-if="extendedData && extendedData.bot_connected" :data="extendedData" />

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <MetricCard label="Подписчики" :value="channel.subscribers_count" />
      <MetricCard label="Ср. просмотры" :value="channel.avg_views" />
      <MetricCard label="ER" :value="channel.er" format="percent" />
      <MetricCard label="Постов/нед." :value="channel.posts_per_week" />
    </div>

    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Main content area -->
      <div class="flex-1 min-w-0 space-y-6">
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
        <AudienceOverlaps v-else-if="activeTab === 'audience'" :username="channel.username" />
        <AdsAnalysis v-else-if="activeTab === 'ads'" :username="channel.username" />
      </div>

      <!-- Sidebar: Similar channels -->
      <div class="lg:w-80 flex-shrink-0">
        <SimilarChannels :username="channel.username" />
      </div>
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
import SimilarChannels from '../components/SimilarChannels.vue'
import AudienceOverlaps from '../components/AudienceOverlaps.vue'
import AdsAnalysis from '../components/AdsAnalysis.vue'
import ExtendedStats from '../components/ExtendedStats.vue'
import BotConnectBanner from '../components/BotConnectBanner.vue'

const route = useRoute()
const channel = ref<Channel | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref('growth')
const isTracked = ref(false)
const watchlistLoading = ref(false)
const extendedData = ref<any>(null)
const extendedLoading = ref(false)
const extendedError = ref<string | null>(null)

const tabs = [
  { id: 'growth', label: 'Динамика' },
  { id: 'content', label: 'Контент' },
  { id: 'audience', label: 'Аудитория' },
  { id: 'ads', label: 'Реклама' },
]

async function loadExtended() {
  if (!channel.value) return
  extendedLoading.value = true
  extendedError.value = null
  try {
    const resp = await api.get<ApiResponse<any>>(`/channels/${channel.value.username}/extended`)
    if (resp.data.success && resp.data.data) {
      extendedData.value = resp.data.data
    } else {
      extendedError.value = resp.data.error || 'Ошибка загрузки'
    }
  } catch {
    extendedError.value = 'Не удалось загрузить расширенную статистику'
  } finally {
    extendedLoading.value = false
  }
}

async function toggleWatchlist() {
  if (!channel.value) return
  watchlistLoading.value = true
  try {
    if (isTracked.value) {
      await api.delete(`/watchlist/${channel.value.username}`)
      isTracked.value = false
    } else {
      await api.post(`/watchlist/${channel.value.username}`)
      isTracked.value = true
    }
  } catch {
    // non-critical
  } finally {
    watchlistLoading.value = false
  }
}

onMounted(async () => {
  try {
    const resp = await api.get<ApiResponse<Channel>>(`/channels/${route.params.username}`)
    if (resp.data.success && resp.data.data) {
      channel.value = resp.data.data
      isTracked.value = resp.data.data.is_tracked ?? false
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
