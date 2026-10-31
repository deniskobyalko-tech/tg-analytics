<template>
  <div class="space-y-4">
    <!-- Comments -->
    <details open class="bg-white rounded-lg shadow">
      <summary class="px-6 py-4 cursor-pointer font-semibold text-gray-900 hover:bg-gray-50">
        Комментарии
        <span class="text-sm font-normal text-gray-500 ml-2">{{ data.comments.total }} всего</span>
      </summary>
      <div class="px-6 pb-4 space-y-2">
        <div class="text-sm text-gray-600">Среднее на пост: {{ data.comments.avg_per_post }}</div>
        <div v-if="data.comments.top_posts.length" class="space-y-2">
          <div class="text-xs font-medium text-gray-500 uppercase">Топ по комментариям</div>
          <div v-for="p in data.comments.top_posts" :key="p.post_id" class="flex justify-between text-sm">
            <span class="text-gray-700 truncate flex-1">{{ p.text_preview }}</span>
            <span class="text-blue-600 font-medium ml-2 flex-shrink-0">{{ p.replies }} комм.</span>
          </div>
        </div>
        <div v-else class="text-sm text-gray-400">Данные о комментариях появятся после обновления</div>
      </div>
    </details>

    <!-- Members -->
    <details class="bg-white rounded-lg shadow">
      <summary class="px-6 py-4 cursor-pointer font-semibold text-gray-900 hover:bg-gray-50">
        Подписчики
        <span class="text-sm font-normal text-gray-500 ml-2">{{ data.members.total.toLocaleString('ru-RU') }}</span>
      </summary>
      <div class="px-6 pb-4 space-y-3">
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-green-600">+{{ data.members.joins_7d }}</div>
            <div class="text-xs text-gray-500">вступили за 7д</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-red-500">-{{ data.members.leaves_7d }}</div>
            <div class="text-xs text-gray-500">вышли за 7д</div>
          </div>
          <div>
            <div class="text-2xl font-bold" :class="data.members.net_growth_7d >= 0 ? 'text-green-600' : 'text-red-500'">
              {{ data.members.net_growth_7d >= 0 ? '+' : '' }}{{ data.members.net_growth_7d }}
            </div>
            <div class="text-xs text-gray-500">нетто за 7д</div>
          </div>
        </div>
        <div v-if="data.members.sample.length" class="max-h-48 overflow-y-auto">
          <div v-for="(m, idx) in data.members.sample" :key="idx" class="flex justify-between text-sm py-1 border-b border-gray-100 last:border-0">
            <span class="text-gray-700">{{ m.first_name || 'Без имени' }}</span>
            <span class="text-gray-400 text-xs">{{ m.username ? '@' + m.username : '' }}</span>
          </div>
        </div>
        <div v-else class="text-sm text-gray-400">Список подписчиков появится после обновления</div>
      </div>
    </details>

    <!-- Traffic sources -->
    <details class="bg-white rounded-lg shadow">
      <summary class="px-6 py-4 cursor-pointer font-semibold text-gray-900 hover:bg-gray-50">
        Источники трафика
      </summary>
      <div class="px-6 pb-4">
        <div v-if="data.traffic_sources.invite_links.length" class="space-y-2">
          <div v-for="link in data.traffic_sources.invite_links" :key="link.link" class="flex justify-between text-sm">
            <span class="text-gray-600 truncate flex-1 font-mono text-xs">{{ link.link }}</span>
            <span class="text-blue-600 font-medium ml-2 flex-shrink-0">{{ link.usage_count }} переходов</span>
          </div>
        </div>
        <div v-else class="text-sm text-gray-400">Нет данных об invite-ссылках</div>
      </div>
    </details>

    <!-- Post details -->
    <details class="bg-white rounded-lg shadow">
      <summary class="px-6 py-4 cursor-pointer font-semibold text-gray-900 hover:bg-gray-50">
        Детализация постов
      </summary>
      <div class="px-6 pb-4 space-y-3">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div><span class="text-gray-500">Ср. сохранений:</span> <span class="font-medium">{{ data.post_details.avg_saves }}</span></div>
          <div><span class="text-gray-500">Ср. ответов:</span> <span class="font-medium">{{ data.post_details.avg_replies }}</span></div>
        </div>
        <div v-if="Object.keys(data.post_details.reactions_breakdown).length">
          <div class="text-xs font-medium text-gray-500 uppercase mb-2">Реакции</div>
          <div class="flex flex-wrap gap-2">
            <div v-for="(count, emoji) in data.post_details.reactions_breakdown" :key="String(emoji)"
              class="bg-gray-100 rounded-full px-3 py-1 text-sm">
              {{ emoji }} {{ Number(count).toLocaleString('ru-RU') }}
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-400">Данные о реакциях появятся после обновления</div>
      </div>
    </details>

    <div v-if="!data.telethon_available" class="text-xs text-yellow-600 bg-yellow-50 rounded p-2">
      Часть данных недоступна (Telethon disconnected). Показаны данные Bot API.
    </div>
  </div>
</template>

<script setup lang="ts">
interface ExtendedData {
  bot_connected: boolean
  telethon_available: boolean
  fetched_at: string | null
  comments: { total: number; avg_per_post: number; top_posts: { post_id: number; text_preview: string; replies: number }[] }
  members: { total: number; sample: { username: string | null; first_name: string | null; joined_at: string | null }[]; joins_7d: number; leaves_7d: number; net_growth_7d: number }
  traffic_sources: { invite_links: { link: string; usage_count: number; creator_id: number | null }[] }
  post_details: { avg_saves: number; avg_replies: number; reactions_breakdown: Record<string, number> }
}

defineProps<{ data: ExtendedData }>()
</script>
