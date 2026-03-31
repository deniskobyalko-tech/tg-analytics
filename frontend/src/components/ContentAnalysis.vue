<template>
  <div class="bg-white rounded-lg shadow p-6 space-y-6">
    <div v-if="loading" class="text-center text-gray-400">Загрузка...</div>
    <div v-else-if="!posts.length" class="text-center text-gray-400">Нет данных о постах</div>
    <template v-else>
      <!-- Stats summary -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900">{{ posts.length }}</div>
          <div class="text-sm text-gray-500">Постов</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900">{{ adCount }}</div>
          <div class="text-sm text-gray-500">Рекламных</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900">{{ adPercent }}%</div>
          <div class="text-sm text-gray-500">Доля рекламы</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900">{{ bestHour }}:00</div>
          <div class="text-sm text-gray-500">Лучшее время</div>
        </div>
      </div>

      <!-- Top posts -->
      <div>
        <h3 class="text-lg font-semibold text-gray-700 mb-3">Топ-5 постов по просмотрам</h3>
        <div class="space-y-3">
          <div v-for="post in topPosts" :key="post.id" class="border rounded-lg p-3">
            <div class="flex justify-between items-start">
              <p class="text-sm text-gray-700 line-clamp-2 flex-1">{{ post.text || '(без текста)' }}</p>
              <span v-if="post.is_ad" class="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded">Реклама</span>
            </div>
            <div class="mt-2 text-xs text-gray-400 flex gap-4">
              <span>👁 {{ formatNumber(post.views) }}</span>
              <span>↗ {{ post.forwards }}</span>
              <span>❤ {{ post.reactions }}</span>
              <span>{{ formatDate(post.date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api, type ApiResponse } from '../api/client'

interface Post {
  id: number
  telegram_post_id: number
  text: string | null
  date: string
  views: number
  forwards: number
  reactions: number
  is_ad: boolean
}

const props = defineProps<{ username: string }>()
const posts = ref<Post[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const resp = await api.get<ApiResponse<Post[]>>(`/channels/${props.username}/posts?limit=100`)
    if (resp.data.success && resp.data.data) {
      posts.value = resp.data.data
    }
  } catch { /* empty */ } finally {
    loading.value = false
  }
})

const adCount = computed(() => posts.value.filter(p => p.is_ad).length)
const adPercent = computed(() => {
  if (!posts.value.length) return 0
  return Math.round((adCount.value / posts.value.length) * 100)
})

const topPosts = computed(() =>
  [...posts.value].sort((a, b) => b.views - a.views).slice(0, 5)
)

const bestHour = computed(() => {
  if (!posts.value.length) return 12
  const hours: Record<number, number> = {}
  posts.value.forEach(p => {
    const h = new Date(p.date).getHours()
    hours[h] = (hours[h] || 0) + 1
  })
  return Number(Object.entries(hours).sort((a, b) => b[1] - a[1])[0]?.[0] || 12)
})

function formatNumber(n: number): string {
  return n.toLocaleString('ru-RU')
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('ru-RU')
}
</script>
