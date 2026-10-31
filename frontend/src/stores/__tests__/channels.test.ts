import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useChannelsStore } from '../channels'

describe('channels store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('getRecent returns empty array initially', () => {
    const store = useChannelsStore()
    expect(store.getRecent()).toEqual([])
  })

  it('initial state is correct', () => {
    const store = useChannelsStore()
    expect(store.current).toBeNull()
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })
})
