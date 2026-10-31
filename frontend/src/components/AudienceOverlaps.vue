<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-2">Пересечение аудитории</h3>
    <p class="text-sm text-gray-500 mb-4">
      Оценка на основе пересылок и упоминаний между каналами
    </p>

    <div v-if="loading" class="text-center text-gray-400 py-8">Загрузка...</div>
    <div v-else-if="overlaps.length === 0" class="text-center text-gray-400 py-8">
      Данные о пересечении аудитории пока отсутствуют.
      <br />
      <span class="text-xs">Данные появятся после накопления истории пересылок.</span>
    </div>
    <div v-else class="space-y-4">
      <div
        v-for="item in overlaps"
        :key="item.username"
        class="flex items-center gap-4"
      >
        <router-link
          :to="`/channel/${item.username}`"
          class="flex items-center gap-3 flex-1 min-w-0 hover:text-blue-600 transition"
        >
          <img
            v-if="item.avatar_url"
            :src="item.avatar_url"
            :alt="item.title"
            class="w-8 h-8 rounded-full flex-shrink-0"
          />
          <div
            v-else
            class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-600 flex-shrink-0"
          >
            {{ item.title[0] }}
          </div>
          <div class="truncate">
            <span class="text-sm font-medium">{{ item.title }}</span>
            <span class="text-xs text-gray-400 ml-1">@{{ item.username }}</span>
          </div>
        </router-link>

        <!-- Overlap bar -->
        <div class="w-32 flex-shrink-0">
          <div class="flex items-center gap-2">
            <div class="flex-1 bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-500 h-2 rounded-full transition-all"
                :style="{ width: `${Math.min(item.overlap_percent, 100)}%` }"
              />
            </div>
            <span class="text-sm font-semibold text-gray-700 w-12 text-right">
              {{ item.overlap_percent.toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type ApiResponse } from '../api/client'
import type { Channel } from '../stores/channels'

interface OverlapChannel extends Channel {
  overlap_percent: number
  calculated_at: string | null
}

const props = defineProps<{ username: string }>()

const overlaps = ref<OverlapChannel[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const resp = await api.get<ApiResponse<OverlapChannel[]>>(`/channels/${props.username}/audience`)
    if (resp.data.success && resp.data.data) {
      overlaps.value = resp.data.data
    }
  } catch {
    // non-critical
  } finally {
    loading.value = false
  }
})
</script>
