<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useLoginUserStore } from '@/stores/loginUser'
import { RocketOutlined, UnorderedListOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const loginUserStore = useLoginUserStore()

const goToCreate = () => {
  router.push('/create')
}

const goToList = () => {
  router.push('/article/list')
}
</script>

<template>
  <div id="homePage">
    <div class="hero-section">
      <div class="container">
        <h1 class="hero-title">AI 爆款文章创作器</h1>
        <p class="hero-subtitle">让 AI 帮你创作 10万+ 爆款文章，只需不到 10 分钟</p>
        <a-space size="large" class="hero-actions">
          <a-button type="primary" size="large" @click="goToCreate">
            <template #icon>
              <RocketOutlined />
            </template>
            开始创作
          </a-button>
          <a-button size="large" @click="goToList">
            <template #icon>
              <UnorderedListOutlined />
            </template>
            我的文章
          </a-button>
        </a-space>
      </div>
    </div>

    <div class="features-section">
      <div class="container">
        <h2 class="section-title">核心功能</h2>
        <a-row :gutter="24">
          <a-col :xs="24" :sm="12" :md="8">
            <a-card :bordered="false" class="feature-card">
              <template #cover>
                <div class="feature-icon">📝</div>
              </template>
              <a-card-meta title="智能生成标题" description="AI 自动分析选题，生成吸引眼球的爆款标题" />
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-card :bordered="false" class="feature-card">
              <template #cover>
                <div class="feature-icon">📋</div>
              </template>
              <a-card-meta title="自动生成大纲" description="智能规划文章结构，确保逻辑清晰完整" />
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-card :bordered="false" class="feature-card">
              <template #cover>
                <div class="feature-icon">✍️</div>
              </template>
              <a-card-meta title="流式生成正文" description="实时展示创作过程，体验打字机般的流畅输出" />
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-card :bordered="false" class="feature-card">
              <template #cover>
                <div class="feature-icon">🖼️</div>
              </template>
              <a-card-meta title="智能配图" description="自动检索高质量无版权图片，完美匹配内容" />
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-card :bordered="false" class="feature-card">
              <template #cover>
                <div class="feature-icon">⚡</div>
              </template>
              <a-card-meta title="快速高效" description="5-10分钟完成全文创作，效率提升10倍" />
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-card :bordered="false" class="feature-card">
              <template #cover>
                <div class="feature-icon">💾</div>
              </template>
              <a-card-meta title="导出分享" description="支持 Markdown 导出，轻松分享到各大平台" />
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
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 120px 20px;
  text-align: center;
  color: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  margin: 0 0 24px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: 24px;
  margin: 0 0 40px;
  opacity: 0.95;
}

.hero-actions {
  display: inline-flex;
  gap: 16px;
}

.hero-actions :deep(.ant-btn-lg) {
  height: 56px;
  padding: 0 40px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 28px;
  transition: all 0.3s;
}

.hero-actions :deep(.ant-btn-primary) {
  background: white;
  color: #667eea;
  border: none;
}

.hero-actions :deep(.ant-btn-primary:hover) {
  background: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.hero-actions :deep(.ant-btn:not(.ant-btn-primary)) {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
}

.hero-actions :deep(.ant-btn:not(.ant-btn-primary):hover) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.features-section {
  padding: 80px 20px;
  background: #f5f5f5;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  text-align: center;
  margin: 0 0 60px;
  color: #1a1a1a;
}

.feature-card {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  height: 100%;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 64px;
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.feature-card :deep(.ant-card-meta-title) {
  font-size: 18px;
  font-weight: 600;
}

.feature-card :deep(.ant-card-meta-description) {
  color: #666;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 16px;
  }
}
</style>
