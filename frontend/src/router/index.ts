import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/channel/:username', name: 'channel', component: () => import('../views/ChannelView.vue') },
  { path: '/compare', name: 'compare', component: () => import('../views/CompareView.vue') },
  { path: '/catalog', name: 'catalog', component: () => import('../views/CatalogView.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
