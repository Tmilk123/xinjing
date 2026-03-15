<script setup>
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const type = route.params.type
</script>

<template>
  <div class="min-h-screen bg-hero-gradient flex items-center justify-center">
    <div class="text-center">
      <div class="text-5xl mb-4">📋</div>
      <h2 class="text-2xl font-bold text-gray-800 mb-2">{{ type }} 评估</h2>
      <p class="text-gray-500 mb-6">功能开发中，请从辅助筛查页面进入</p>
      <button class="btn-primary" @click="router.push('/screening')">前往辅助筛查</button>
    </div>
  </div>
</template>
