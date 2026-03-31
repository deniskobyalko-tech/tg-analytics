<template>
  <div class="flex items-center gap-4 bg-white rounded-lg shadow p-6">
    <img
      v-if="channel.avatar_url"
      :src="channel.avatar_url"
      :alt="channel.title"
      class="w-16 h-16 rounded-full"
    />
    <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-2xl font-bold text-blue-600" v-else>
      {{ channel.title[0] }}
    </div>
    <div>
      <h1 class="text-2xl font-bold text-gray-900">{{ channel.title }}</h1>
      <div class="text-gray-500">@{{ channel.username }}</div>
      <p v-if="channel.description" class="text-sm text-gray-600 mt-1 line-clamp-2">
        {{ channel.description }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Channel } from '../stores/channels'
defineProps<{ channel: Channel }>()
</script>
