<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center gap-6">
        <router-link to="/" class="text-xl font-bold text-blue-600">TG Analytics</router-link>
        <router-link to="/catalog" class="text-gray-600 hover:text-gray-900">Catalog</router-link>
        <router-link to="/compare" class="text-gray-600 hover:text-gray-900">Compare</router-link>
      </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-6">
      <router-view />
    </main>
  </div>
</template>
