<template>
  <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
    <div class="text-blue-500 text-xl flex-shrink-0">i</div>
    <div>
      <div class="font-medium text-blue-900">Расширенная статистика недоступна</div>
      <p class="text-sm text-blue-700 mt-1">
        Добавьте <span class="font-mono font-semibold">@{{ botUsername }}</span>
        в админы канала для доступа к комментариям, подписчикам, источникам трафика и детализации постов.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ botUsername: string }>()
</script>
