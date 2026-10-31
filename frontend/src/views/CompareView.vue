<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">Сравнение каналов</h1>

    <!-- Channel selector -->
    <div class="bg-white rounded-lg shadow p-6">
      <p class="text-sm text-gray-500 mb-3">Введите 2-4 канала для сравнения через запятую</p>
      <form @submit.prevent="onCompare" class="flex gap-2">
        <input
          v-model="input"
          type="text"
          placeholder="@channel1, @channel2, @channel3"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          :disabled="loading"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Загрузка...' : 'Сравнить' }}
        </button>
      </form>
      <p v-if="error" class="mt-2 text-sm text-red-500">{{ error }}</p>
    </div>

    <!-- Comparison table -->
    <div v-if="channels.length >= 2" class="bg-white rounded-lg shadow overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b bg-gray-50">
            <th class="text-left px-4 py-3 text-gray-500 font-medium">Метрика</th>
            <th
              v-for="ch in channels"
              :key="ch.username"
              class="text-center px-4 py-3 min-w-[140px]"
            >
              <router-link :to="`/channel/${ch.username}`" class="text-blue-600 hover:underline font-medium">
                {{ ch.title }}
              </router-link>
              <div class="text-xs text-gray-400 font-normal">@{{ ch.username }}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="metric in metrics" :key="metric.key" class="border-b last:border-0">
            <td class="px-4 py-3 text-gray-600 font-medium">{{ metric.label }}</td>
            <td
              v-for="ch in channels"
              :key="ch.username"
              class="px-4 py-3 text-center"
              :class="isBest(metric.key, ch) ? 'text-green-600 font-semibold' : 'text-gray-900'"
            >
              {{ formatMetric(metric, ch) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading && channels.length === 0 && !error" class="text-center py-12 text-gray-400">
      Введите названия каналов для сравнения
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api, type ApiResponse } from '../api/client'
import type { Channel } from '../stores/channels'

const input = ref('')
const channels = ref<Channel[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

interface Metric {
  key: keyof Channel
  label: string
  format: 'number' | 'percent' | 'float'
}

const metrics: Metric[] = [
  { key: 'subscribers_count', label: 'Подписчики', format: 'number' },
  { key: 'avg_views', label: 'Ср. просмотры', format: 'number' },
  { key: 'er', label: 'ER', format: 'percent' },
  { key: 'posts_per_week', label: 'Постов/нед.', format: 'float' },
]

async function onCompare() {
  const raw = input.value
    .split(',')
    .map(s => s.trim().replace(/^@/, '').replace(/^https?:\/\/t\.me\//, ''))
    .filter(Boolean)
    .join(',')

  if (!raw) return

  loading.value = true
  error.value = null
  channels.value = []

  try {
    const resp = await api.get<ApiResponse<Channel[]>>(`/compare`, {
      params: { channels: raw },
    })
    if (resp.data.success && resp.data.data) {
      channels.value = resp.data.data
    } else {
      error.value = resp.data.error || 'Ошибка сравнения'
    }
  } catch {
    error.value = 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

function isBest(key: keyof Channel, ch: Channel): boolean {
  if (channels.value.length < 2) return false
  const val = Number(ch[key]) || 0
  return channels.value.every(c => val >= (Number(c[key]) || 0))
}

function formatMetric(metric: Metric, ch: Channel): string {
  const val = Number(ch[metric.key]) || 0
  if (metric.format === 'number') return val.toLocaleString('ru-RU')
  if (metric.format === 'percent') return `${val}%`
  return String(val)
}
</script>
