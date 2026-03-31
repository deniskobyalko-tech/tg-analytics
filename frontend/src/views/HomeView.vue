<template>
  <div class="flex flex-col items-center pt-16">
    <h1 class="text-4xl font-bold text-gray-900 mb-2">TG Аналитика каналов</h1>
    <p class="text-gray-500 mb-8">Анализ любого Telegram канала</p>

    <form @submit.prevent="onSearch" class="w-full max-w-xl flex gap-2">
      <input
        v-model="query"
        type="text"
        placeholder="@канал или t.me/канал"
        class="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        :disabled="store.loading"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
      >
        {{ store.loading ? 'Анализирую...' : 'Анализ' }}
      </button>
    </form>

    <p v-if="store.error" class="mt-4 text-red-500">{{ store.error }}</p>

    <div v-if="recent.length" class="mt-12 w-full max-w-3xl">
      <h2 class="text-lg font-semibold text-gray-700 mb-4">Недавно просмотренные</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <router-link
          v-for="ch in recent"
          :key="ch.username"
          :to="`/channel/${ch.username}`"
          class="p-4 bg-white rounded-lg shadow hover:shadow-md transition"
        >
          <div class="font-medium text-gray-900">{{ ch.title }}</div>
          <div class="text-sm text-gray-500">@{{ ch.username }}</div>
          <div class="mt-2 text-sm text-gray-600">
            {{ formatNumber(ch.subscribers_count) }} подписчиков &middot; ER {{ ch.er }}%
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChannelsStore, type Channel } from '../stores/channels'

const store = useChannelsStore()
const router = useRouter()
const query = ref('')
const recent = ref<Channel[]>([])

onMounted(() => {
  recent.value = store.getRecent()
})

async function onSearch() {
  if (!query.value.trim()) return
  const channel = await store.analyzeChannel(query.value)
  if (channel) {
    router.push(`/channel/${channel.username}`)
  }
}

function formatNumber(n: number): string {
  return n.toLocaleString('ru-RU')
}
</script>
