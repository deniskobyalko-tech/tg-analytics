<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex gap-2 mb-4">
      <button
        v-for="d in [7, 30, 90]"
        :key="d"
        @click="days = d"
        :class="['px-3 py-1 rounded text-sm', days === d ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600']"
      >
        {{ d }} дн.
      </button>
    </div>
    <Line v-if="chartData" :data="chartData" :options="chartOptions" />
    <p v-else class="text-gray-400 text-center py-8">Нет данных о динамике</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { api, type ApiResponse } from '../api/client'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps<{ username: string }>()
const days = ref(30)
const chartData = ref<any>(null)

const chartOptions = {
  responsive: true,
  plugins: { legend: { display: true } },
  scales: { y: { beginAtZero: false } },
}

async function fetchHistory() {
  try {
    const resp = await api.get<ApiResponse<any[]>>(`/channels/${props.username}/history?days=${days.value}`)
    if (!resp.data.success || !resp.data.data?.length) {
      chartData.value = null
      return
    }
    const snapshots = resp.data.data
    chartData.value = {
      labels: snapshots.map((s: any) => s.date.slice(0, 10)),
      datasets: [
        {
          label: 'Подписчики',
          data: snapshots.map((s: any) => s.subscribers),
          borderColor: '#3b82f6',
          fill: false,
        },
        {
          label: 'Ср. просмотры',
          data: snapshots.map((s: any) => s.avg_views),
          borderColor: '#10b981',
          fill: false,
        },
      ],
    }
  } catch {
    chartData.value = null
  }
}

onMounted(fetchHistory)
watch(days, fetchHistory)
</script>
