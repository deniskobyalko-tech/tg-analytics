<template>
  <div class="space-y-6">
    <!-- Summary cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-sm text-gray-500">Всего постов</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">{{ totalPosts }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-sm text-gray-500">Рекламных</div>
        <div class="text-2xl font-bold text-orange-600 mt-1">{{ adPosts.length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-sm text-gray-500">Доля рекламы</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">{{ adPercent }}%</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-sm text-gray-500">Ср. просмотры рекламы</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">{{ avgAdViews.toLocaleString('ru-RU') }}</div>
      </div>
    </div>

    <!-- Ad posts list -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Рекламные посты</h3>
      </div>

      <div v-if="loading" class="p-6 text-center text-gray-400">Загрузка...</div>
      <div v-else-if="adPosts.length === 0" class="p-6 text-center text-gray-400">
        Рекламные посты не найдены
      </div>
      <div v-else class="divide-y">
        <div v-for="post in adPosts" :key="post.telegram_post_id" class="px-6 py-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-900 line-clamp-2">{{ post.text || 'Без текста' }}</p>
              <div class="flex gap-4 mt-2 text-xs text-gray-500">
                <span>{{ formatDate(post.date) }}</span>
                <span>{{ post.views?.toLocaleString('ru-RU') }} просм.</span>
                <span v-if="post.forwards">{{ post.forwards }} пересылок</span>
                <span v-if="post.reactions">{{ post.reactions }} реакций</span>
              </div>
            </div>
            <div v-if="post.ad_price" class="text-right flex-shrink-0">
              <div class="text-sm font-semibold text-gray-900">{{ post.ad_price.toLocaleString('ru-RU') }} ₽</div>
              <div class="text-xs text-gray-500">
                CPV: {{ post.views ? (post.ad_price / post.views).toFixed(2) : '—' }} ₽
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api, type ApiResponse } from '../api/client'

interface Post {
  telegram_post_id: number
  text: string | null
  date: string
  views: number
  forwards: number
  reactions: number
  is_ad: boolean
  ad_price: number | null
}

const props = defineProps<{ username: string }>()

const allPosts = ref<Post[]>([])
const loading = ref(true)

const adPosts = computed(() => allPosts.value.filter(p => p.is_ad))
const totalPosts = computed(() => allPosts.value.length)
const adPercent = computed(() => {
  if (totalPosts.value === 0) return 0
  return Math.round((adPosts.value.length / totalPosts.value) * 100)
})
const avgAdViews = computed(() => {
  if (adPosts.value.length === 0) return 0
  const total = adPosts.value.reduce((sum, p) => sum + (p.views || 0), 0)
  return Math.round(total / adPosts.value.length)
})

onMounted(async () => {
  try {
    const resp = await api.get<ApiResponse<Post[]>>(`/channels/${props.username}/posts`, {
      params: { limit: 100 },
    })
    if (resp.data.success && resp.data.data) {
      allPosts.value = resp.data.data
    }
  } catch {
    // non-critical
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>
