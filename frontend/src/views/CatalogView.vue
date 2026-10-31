<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">Каталог каналов</h1>
      <div class="flex gap-2">
        <select v-model="sortBy" @change="loadChannels" class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="subscribers_count">По подписчикам</option>
          <option value="er">По ER</option>
          <option value="avg_views">По просмотрам</option>
          <option value="posts_per_week">По частоте</option>
        </select>
      </div>
    </div>

    <!-- Search -->
    <div class="flex gap-2">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Поиск по названию..."
        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        @input="onSearch"
      />
    </div>

    <div class="flex flex-col md:flex-row gap-6">
      <!-- Categories sidebar -->
      <div class="md:w-48 flex-shrink-0">
        <h3 class="text-sm font-semibold text-gray-500 uppercase mb-2">Категории</h3>
        <ul class="space-y-1">
          <li>
            <button
              @click="selectedCategory = null; loadChannels()"
              :class="[
                'w-full text-left px-3 py-1.5 rounded text-sm transition',
                !selectedCategory ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
              ]"
            >
              Все
            </button>
          </li>
          <li v-for="cat in categories" :key="cat.slug">
            <button
              @click="selectedCategory = cat.slug; loadChannels()"
              :class="[
                'w-full text-left px-3 py-1.5 rounded text-sm transition',
                selectedCategory === cat.slug ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
              ]"
            >
              {{ cat.name }}
            </button>
          </li>
        </ul>
      </div>

      <!-- Channel grid -->
      <div class="flex-1">
        <div v-if="loading" class="text-center py-12 text-gray-400">Загрузка...</div>
        <div v-else-if="channels.length === 0" class="text-center py-12 text-gray-400">
          Каналов пока нет. Добавьте каналы через поиск на главной.
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <router-link
            v-for="ch in channels"
            :key="ch.username"
            :to="`/channel/${ch.username}`"
            class="p-4 bg-white rounded-lg shadow hover:shadow-md transition"
          >
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
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span class="text-gray-500">Подп.:</span>
                <span class="font-medium ml-1">{{ formatNumber(ch.subscribers_count) }}</span>
              </div>
              <div>
                <span class="text-gray-500">ER:</span>
                <span class="font-medium ml-1">{{ ch.er }}%</span>
              </div>
              <div>
                <span class="text-gray-500">Просм.:</span>
                <span class="font-medium ml-1">{{ formatNumber(ch.avg_views) }}</span>
              </div>
              <div>
                <span class="text-gray-500">Пост/нед:</span>
                <span class="font-medium ml-1">{{ ch.posts_per_week }}</span>
              </div>
            </div>
          </router-link>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
          <button
            v-for="p in totalPages"
            :key="p"
            @click="page = p; loadChannels()"
            :class="[
              'px-3 py-1 rounded text-sm',
              page === p ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ p }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type ApiResponse } from '../api/client'
import type { Channel } from '../stores/channels'

interface Category {
  id: number
  name: string
  slug: string
}

const categories = ref<Category[]>([])
const channels = ref<Channel[]>([])
const loading = ref(true)
const selectedCategory = ref<string | null>(null)
const sortBy = ref('subscribers_count')
const page = ref(1)
const total = ref(0)
const limit = 12
const searchQuery = ref('')
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const totalPages = ref(0)

onMounted(async () => {
  await Promise.all([loadCategories(), loadChannels()])
})

async function loadCategories() {
  try {
    const resp = await api.get<ApiResponse<Category[]>>('/categories')
    if (resp.data.success && resp.data.data) {
      categories.value = resp.data.data
    }
  } catch {
    // non-critical
  }
}

async function loadChannels() {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      limit,
      sort: sortBy.value,
    }
    if (selectedCategory.value) params.category = selectedCategory.value

    let resp
    if (searchQuery.value.trim()) {
      resp = await api.get<ApiResponse<Channel[]>>('/search', {
        params: { q: searchQuery.value, page: page.value, limit },
      })
    } else {
      resp = await api.get<ApiResponse<Channel[]>>('/catalog', { params })
    }

    if (resp.data.success) {
      channels.value = resp.data.data || []
      total.value = resp.data.meta?.total || 0
      totalPages.value = Math.ceil(total.value / limit)
    }
  } catch {
    channels.value = []
  } finally {
    loading.value = false
  }
}

function onSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadChannels()
  }, 300)
}

function formatNumber(n: number): string {
  return n.toLocaleString('ru-RU')
}
</script>
