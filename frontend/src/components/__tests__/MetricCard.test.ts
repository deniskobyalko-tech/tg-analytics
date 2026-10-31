import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MetricCard from '../MetricCard.vue'

describe('MetricCard', () => {
  it('renders label and value', () => {
    const wrapper = mount(MetricCard, {
      props: { label: 'Subscribers', value: 5000 },
    })
    expect(wrapper.text()).toContain('Subscribers')
    expect(wrapper.text()).toContain('5')
  })

  it('formats percent', () => {
    const wrapper = mount(MetricCard, {
      props: { label: 'ER', value: 50, format: 'percent' },
    })
    expect(wrapper.text()).toContain('50%')
  })

  it('renders with zero value', () => {
    const wrapper = mount(MetricCard, {
      props: { label: 'Views', value: 0 },
    })
    expect(wrapper.text()).toContain('Views')
    expect(wrapper.text()).toContain('0')
  })
})
