<template>
  <div class="article-create-page">
    <div class="container">
      <!-- 标题区域 -->
      <div class="header">
        <h1 class="title">AI 爆款文章创作器</h1>
        <p class="subtitle">让 AI 帮你创作10万+爆款文章</p>
      </div>

      <!-- 输入区域 -->
      <div v-if="!isCreating && !isCompleted" class="input-section">
        <a-card :bordered="false" class="input-card">
          <a-form layout="vertical">
            <a-form-item label="请输入您想创作的文章选题">
              <a-textarea
                v-model:value="topic"
                placeholder="例如：2026年AI如何改变职场"
                :rows="4"
                :maxlength="500"
                show-count
                class="topic-input"
              />
            </a-form-item>
            <a-form-item>
              <a-button
                type="primary"
                size="large"
                block
                :loading="isCreating"
                :disabled="!topic.trim()"
                @click="startCreate"
                class="create-btn"
              >
                <template #icon>
                  <RocketOutlined />
                </template>
                开始创作
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 创作进度区域 -->
      <div v-if="isCreating" class="progress-section">
        <a-card :bordered="false" class="progress-card">
          <!-- 进度步骤 -->
          <a-steps :current="currentStep" class="steps">
            <a-step title="生成标题" />
            <a-step title="生成大纲" />
            <a-step title="生成正文" />
            <a-step title="分析配图" />
            <a-step title="生成配图" />
          </a-steps>

          <!-- 实时内容展示 -->
          <div class="content-preview">
            <!-- 标题 -->
            <div v-if="article.mainTitle" class="section">
              <h2 class="section-title">📝 文章标题</h2>
              <div class="title-box">
                <h3>{{ article.mainTitle }}</h3>
                <p class="subtitle-text">{{ article.subTitle }}</p>
              </div>
            </div>

            <!-- 大纲 -->
            <div v-if="article.outline && article.outline.length > 0" class="section">
              <h2 class="section-title">📋 文章大纲</h2>
              <div class="outline-box">
                <div v-for="item in article.outline" :key="item.section" class="outline-item">
                  <div class="outline-title">{{ item.section }}. {{ item.title }}</div>
                  <ul class="outline-points">
                    <li v-for="(point, idx) in item.points" :key="idx">{{ point }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- 正文 -->
            <div v-if="article.content" class="section">
              <h2 class="section-title">✍️ 文章正文</h2>
              <div class="content-box">
                <div v-html="markdownToHtml(article.content)" class="markdown-content"></div>
                <div v-if="isStreaming" class="cursor-blink">|</div>
              </div>
            </div>

            <!-- 配图 -->
            <div v-if="article.images && article.images.length > 0" class="section">
              <h2 class="section-title">🖼️ 文章配图</h2>
              <div class="images-grid">
                <div v-for="image in article.images" :key="image.position" class="image-item">
                  <img :src="image.url" :alt="image.description" />
                  <div class="image-info">
                    <span class="badge">{{ image.method }}</span>
                    <span class="keywords">{{ image.keywords }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 加载动画 -->
          <div v-if="!isCompleted" class="loading-indicator">
            <a-spin tip="AI 正在创作中..." />
          </div>
        </a-card>
      </div>

      <!-- 完成区域 -->
      <div v-if="isCompleted" class="complete-section">
        <a-result
          status="success"
          title="文章创作完成!"
          sub-title="您的爆款文章已经生成,快去查看吧~"
        >
          <template #extra>
            <a-space>
              <a-button type="primary" @click="viewArticle">查看文章</a-button>
              <a-button @click="resetCreate">再创作一篇</a-button>
            </a-space>
          </template>
        </a-result>
      </div>

      <!-- 错误提示 -->
      <a-modal
        v-model:open="errorVisible"
        title="创作失败"
        @ok="errorVisible = false"
      >
        <p>{{ errorMessage }}</p>
      </a-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { RocketOutlined } from '@ant-design/icons-vue'
import { createArticle, type ArticleVO, type OutlineItem, type ImageItem } from '@/api/articleController'
import { connectSSE, closeSSE, type SSEMessage } from '@/utils/sse'
import { marked } from 'marked'

const router = useRouter()

// 状态
const topic = ref('')
const isCreating = ref(false)
const isCompleted = ref(false)
const isStreaming = ref(false)
const currentStep = ref(0)
const taskId = ref('')
const errorVisible = ref(false)
const errorMessage = ref('')

// 文章数据
const article = ref<Partial<ArticleVO>>({
  mainTitle: '',
  subTitle: '',
  outline: [],
  content: '',
  images: [],
})

let eventSource: EventSource | null = null

// Markdown 转 HTML
const markdownToHtml = (markdown: string) => {
  return marked(markdown)
}

// 开始创作
const startCreate = async () => {
  if (!topic.value.trim()) {
    message.warning('请输入选题')
    return
  }

  isCreating.value = true
  currentStep.value = 0

  try {
    // 创建任务
    const res = await createArticle({ topic: topic.value })
    taskId.value = res.data

    // 建立 SSE 连接
    eventSource = connectSSE(taskId.value, {
      onMessage: handleSSEMessage,
      onError: handleSSEError,
      onComplete: handleSSEComplete,
    })
  } catch (error: any) {
    message.error(error.message || '创建任务失败')
    isCreating.value = false
  }
}

// 处理 SSE 消息
const handleSSEMessage = (msg: SSEMessage) => {
  console.log('SSE消息:', msg)

  switch (msg.type) {
    case 'AGENT1_COMPLETE':
      currentStep.value = 1
      article.value.mainTitle = msg.data?.mainTitle || msg.title?.mainTitle
      article.value.subTitle = msg.data?.subTitle || msg.title?.subTitle
      break

    case 'AGENT2_COMPLETE':
      currentStep.value = 2
      article.value.outline = msg.data || msg.outline
      break

    case 'AGENT3_STREAMING':
      isStreaming.value = true
      article.value.content += msg.data?.content || msg.content || ''
      break

    case 'AGENT3_COMPLETE':
      currentStep.value = 3
      isStreaming.value = false
      break

    case 'AGENT4_COMPLETE':
      currentStep.value = 4
      break

    case 'IMAGE_COMPLETE':
      if (!article.value.images) {
        article.value.images = []
      }
      article.value.images.push(msg.data || msg.image)
      break

    case 'AGENT5_COMPLETE':
      currentStep.value = 5
      break

    case 'ALL_COMPLETE':
      isCompleted.value = true
      message.success('文章创作完成!')
      break

    case 'ERROR':
      errorMessage.value = msg.message || '创作失败'
      errorVisible.value = true
      isCreating.value = false
      break
  }
}

// 处理 SSE 错误
const handleSSEError = (error: Event) => {
  console.error('SSE错误:', error)
  message.error('连接失败,请重试')
  isCreating.value = false
}

// 处理 SSE 完成
const handleSSEComplete = () => {
  console.log('SSE连接关闭')
}

// 查看文章
const viewArticle = () => {
  router.push(`/article/${taskId.value}`)
}

// 重新创作
const resetCreate = () => {
  topic.value = ''
  isCreating.value = false
  isCompleted.value = false
  currentStep.value = 0
  article.value = {
    mainTitle: '',
    subTitle: '',
    outline: [],
    content: '',
    images: [],
  }
}

// 组件卸载前关闭 SSE
onBeforeUnmount(() => {
  closeSSE(eventSource)
})
</script>

<style scoped lang="scss">
.article-create-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .header {
    text-align: center;
    margin-bottom: 40px;
    color: white;

    .title {
      font-size: 48px;
      font-weight: 700;
      margin: 0 0 16px;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }

    .subtitle {
      font-size: 20px;
      opacity: 0.9;
      margin: 0;
    }
  }

  .input-card,
  .progress-card {
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

    :deep(.ant-card-body) {
      padding: 40px;
    }
  }

  .topic-input {
    font-size: 16px;
    border-radius: 8px;
  }

  .create-btn {
    height: 56px;
    font-size: 18px;
    font-weight: 600;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
  }

  .steps {
    margin-bottom: 40px;
  }

  .content-preview {
    .section {
      margin-bottom: 32px;

      .section-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 16px;
        color: #1890ff;
      }
    }

    .title-box {
      padding: 24px;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      border-radius: 12px;

      h3 {
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 12px;
        color: #1a1a1a;
      }

      .subtitle-text {
        font-size: 16px;
        color: #666;
        margin: 0;
      }
    }

    .outline-box {
      .outline-item {
        margin-bottom: 16px;
        padding: 16px;
        background: #f5f5f5;
        border-radius: 8px;

        .outline-title {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .outline-points {
          margin: 0;
          padding-left: 20px;

          li {
            margin-bottom: 4px;
            color: #666;
          }
        }
      }
    }

    .content-box {
      padding: 24px;
      background: #fff;
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      position: relative;

      .markdown-content {
        line-height: 1.8;
        font-size: 16px;

        :deep(h2) {
          font-size: 24px;
          font-weight: 600;
          margin: 24px 0 16px;
          padding-bottom: 8px;
          border-bottom: 2px solid #eee;
        }

        :deep(p) {
          margin-bottom: 16px;
          text-indent: 2em;
        }
      }

      .cursor-blink {
        display: inline-block;
        animation: blink 1s infinite;
      }
    }

    .images-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;

      .image-item {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;

        &:hover {
          transform: translateY(-4px);
        }

        img {
          width: 100%;
          height: 200px;
          object-fit: cover;
        }

        .image-info {
          padding: 12px;
          background: #fff;
          display: flex;
          justify-content: space-between;
          align-items: center;

          .badge {
            padding: 4px 12px;
            background: #1890ff;
            color: white;
            border-radius: 12px;
            font-size: 12px;
          }

          .keywords {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }
  }

  .loading-indicator {
    text-align: center;
    padding: 40px 0;
  }

  .complete-section {
    :deep(.ant-result) {
      background: white;
      border-radius: 16px;
      padding: 60px 40px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}
</style>
