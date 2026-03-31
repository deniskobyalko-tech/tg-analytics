import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
})

export interface ApiResponse<T = unknown> {
  success: boolean
  data: T | null
  error: string | null
  meta: { total: number; page: number; limit: number } | null
}
