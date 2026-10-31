<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Похожие каналы</h3>

    <div v-if="loading" class="text-center text-gray-400 py-4">Загрузка...</div>
    <div v-else-if="channels.length === 0" class="text-center text-gray-400 py-4">
      Похожие каналы пока не найдены
    </div>
    <div v-else class="space-y-3">
      <router-link
        v-for="ch in channels"
        :key="ch.username"
        :to="`/channel/${ch.username}`"
        class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition group"
      >
        <img
          v-if="ch.avatar_url"
          :src="ch.avatar_url"
          :alt="ch.title"
          class="w-10 h-10 rounded-full flex-shrink-0"
        />
        <div
          v-else
          class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-600 flex-shrink-0"
        >
          {{ ch.title[0] }}
        </div>

        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium text-gray-900 truncate group-hover:text-blue-600">
            {{ ch.title }}
          </div>
          <div class="text-xs text-gray-500">
            @{{ ch.username }}
          </div>
        </div>

        <div class="text-right flex-shrink-0">
          <div class="text-sm font-semibold text-blue-600">
            {{ Math.round(ch.similarity_score * 100) }}%
          </div>
          <div class="text-xs text-gray-400">
            {{ ch.subscribers_count?.toLocaleString('ru-RU') }} подп.
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type ApiResponse } from '../api/client'
import type { Channel } from '../stores/channels'

interface SimilarChannel extends Channel {
  similarity_score: number
  match_type: string
}

const props = defineProps<{ username: string }>()

const channels = ref<SimilarChannel[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const resp = await api.get<ApiResponse<SimilarChannel[]>>(`/channels/${props.username}/similar`)
    if (resp.data.success && resp.data.data) {
      channels.value = resp.data.data
    }
  } catch {
    // silently fail — sidebar is non-critical
  } finally {
    loading.value = false
  }
})
</script>
