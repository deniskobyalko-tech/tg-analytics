import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, type ApiResponse } from '../api/client'

export interface Channel {
  id: number
  telegram_id: number
  username: string
  title: string
  description: string | null
  avatar_url: string | null
  subscribers_count: number
  avg_views: number
  er: number
  posts_per_week: number
}

export const useChannelsStore = defineStore('channels', () => {
  const current = ref<Channel | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function analyzeChannel(username: string): Promise<Channel | null> {
    loading.value = true
    error.value = null
    try {
      const resp = await api.post<ApiResponse<Channel>>('/channels/analyze', { username })
      if (resp.data.success && resp.data.data) {
        current.value = resp.data.data
        saveToRecent(resp.data.data)
        return resp.data.data
      }
      error.value = resp.data.error || 'Unknown error'
      return null
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Request failed'
      return null
    } finally {
      loading.value = false
    }
  }

  function getRecent(): Channel[] {
    const raw = localStorage.getItem('recent_channels')
    return raw ? JSON.parse(raw) : []
  }

  function saveToRecent(channel: Channel) {
    const recent = getRecent().filter(c => c.username !== channel.username)
    recent.unshift(channel)
    localStorage.setItem('recent_channels', JSON.stringify(recent.slice(0, 10)))
  }

  return { current, loading, error, analyzeChannel, getRecent }
})
