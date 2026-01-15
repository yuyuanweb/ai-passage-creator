<script setup lang="ts">
import { useLoginUserStore } from '@/stores/loginUser'

const loginUserStore = useLoginUserStore()
</script>

<template>
  <div id="homePage">
    <div class="container">
      <!-- 网站标题和描述 -->
      <div class="hero-section">
        <h1 class="hero-title">项目模板</h1>
        <p class="hero-description">Spring Boot + Vue 全栈项目初始化模板</p>
      </div>

      <!-- 欢迎信息 -->
      <div class="welcome-section">
        <a-card class="welcome-card">
          <template #title>
            <span>👋 欢迎使用</span>
          </template>
          <p v-if="loginUserStore.loginUser.id">
            欢迎回来，{{ loginUserStore.loginUser.userName }}！
          </p>
          <p v-else>
            请先 <router-link to="/user/login">登录</router-link> 或
            <router-link to="/user/register">注册</router-link>
          </p>
        </a-card>
      </div>

      <!-- 功能介绍 -->
      <div class="features-section">
        <h2 class="section-title">模板特性</h2>
        <a-row :gutter="[24, 24]">
          <a-col :xs="24" :sm="12" :md="8">
            <a-card class="feature-card">
              <template #title>🔐 用户模块</template>
              <p>完整的用户注册、登录、权限管理功能</p>
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-card class="feature-card">
              <template #title>📝 接口文档</template>
              <p>集成 Knife4j，自动生成 API 文档</p>
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-card class="feature-card">
              <template #title>🗃️ 数据持久化</template>
              <p>MyBatis-Flex + MySQL + Redis 数据存储</p>
            </a-card>
          </a-col>
        </a-row>
      </div>
    </div>
  </div>
</template>

<style scoped>
#homePage {
  width: 100%;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 英雄区域 */
.hero-section {
  text-align: center;
  padding: 80px 0 60px;
  margin-bottom: 28px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 20px;
  margin: 0;
  color: #64748b;
}

/* 欢迎区域 */
.welcome-section {
  margin-bottom: 40px;
}

.welcome-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
}

/* 功能介绍区域 */
.features-section {
  margin-bottom: 60px;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #1e293b;
  text-align: center;
}

.feature-card {
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-description {
    font-size: 16px;
  }
}
</style>
