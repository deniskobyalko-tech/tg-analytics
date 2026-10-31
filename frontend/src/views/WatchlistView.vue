<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Отслеживаемые каналы</h1>
        <p class="text-sm text-gray-500 mt-1">Каналы с расширенной аналитикой (Tier 2)</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Загрузка...</div>
    <div v-else-if="channels.length === 0" class="text-center py-12">
      <div class="text-gray-400 mb-2">Нет отслеживаемых каналов</div>
      <p class="text-sm text-gray-500">
        Добавьте канал в отслеживание на странице канала
      </p>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="ch in channels"
        :key="ch.username"
        class="bg-white rounded-lg shadow p-4"
      >
        <router-link :to="`/channel/${ch.username}`" class="block hover:text-blue-600 transition">
          <div class="flex items-center gap-3 mb-3">
            <img
              v-if="ch.avatar_url"
              :src="ch.avatar_url"
              :alt="ch.title"
              class="w-10 h-10 rounded-full"
            />
            <div
              v-else
              class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-600"
            >
              {{ ch.title[0] }}
            </div>
            <div class="min-w-0">
              <div class="font-medium text-gray-900 truncate">{{ ch.title }}</div>
              <div class="text-xs text-gray-500">@{{ ch.username }}</div>
            </div>
          </div>
        </router-link>

        <div class="grid grid-cols-2 gap-2 text-sm mb-3">
          <div>
            <span class="text-gray-500">Подп.:</span>
            <span class="font-medium ml-1">{{ ch.subscribers_count?.toLocaleString('ru-RU') }}</span>
          </div>
          <div>
            <span class="text-gray-500">ER:</span>
            <span class="font-medium ml-1">{{ ch.er }}%</span>
          </div>
        </div>

        <button
          @click="removeFromWatchlist(ch.username)"
          class="w-full px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50 transition"
        >
          Убрать из отслеживания
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type ApiResponse } from '../api/client'
import type { Channel } from '../stores/channels'

const channels = ref<Channel[]>([])
const loading = ref(true)

onMounted(async () => {
  await loadWatchlist()
})

async function loadWatchlist() {
  loading.value = true
  try {
    const resp = await api.get<ApiResponse<Channel[]>>('/watchlist')
    if (resp.data.success && resp.data.data) {
      channels.value = resp.data.data
    }
  } catch {
    // non-critical
  } finally {
    loading.value = false
  }
}

async function removeFromWatchlist(username: string) {
  try {
    await api.delete(`/watchlist/${username}`)
    channels.value = channels.value.filter(c => c.username !== username)
  } catch {
    // non-critical
  }
}
</script>
