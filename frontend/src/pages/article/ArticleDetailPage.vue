<template>
  <div class="article-detail-page">
    <div class="container">
      <div class="header-actions">
        <a-button @click="goBack">
          <template #icon>
            <ArrowLeftOutlined />
          </template>
          返回
        </a-button>
        <a-space>
          <a-button @click="exportMarkdown">
            <template #icon>
              <DownloadOutlined />
            </template>
            导出 Markdown
          </a-button>
        </a-space>
      </div>

      <a-spin :spinning="loading" tip="加载中...">
        <a-card :bordered="false" v-if="article">
          <!-- 标题 -->
          <div class="title-section">
            <h1 class="main-title">{{ article.mainTitle }}</h1>
            <p class="sub-title">{{ article.subTitle }}</p>
            <div class="meta-info">
              <a-tag :color="getStatusColor(article.status)">
                {{ getStatusText(article.status) }}
              </a-tag>
              <span class="time">创建于 {{ formatDate(article.createTime) }}</span>
            </div>
          </div>

          <a-divider />

          <!-- 大纲 -->
          <div v-if="article.outline && article.outline.length > 0" class="outline-section">
            <h2 class="section-title">📋 文章大纲</h2>
            <div class="outline-list">
              <div v-for="item in article.outline" :key="item.section" class="outline-item">
                <div class="outline-title">{{ item.section }}. {{ item.title }}</div>
                <ul class="outline-points">
                  <li v-for="(point, idx) in item.points" :key="idx">{{ point }}</li>
                </ul>
              </div>
            </div>
          </div>

          <a-divider />

          <!-- 正文 -->
          <div v-if="article.content" class="content-section">
            <h2 class="section-title">✍️ 文章正文</h2>
            <div v-html="markdownToHtml(article.content)" class="markdown-content"></div>
          </div>

          <!-- 配图 -->
          <div v-if="article.images && article.images.length > 0" class="images-section">
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
        </a-card>
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { ArrowLeftOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import { getArticle, type ArticleVO } from '@/api/articleController'
import { marked } from 'marked'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const article = ref<ArticleVO | null>(null)

// Markdown 转 HTML
const markdownToHtml = (markdown: string) => {
  return marked(markdown)
}

// 加载文章
const loadArticle = async () => {
  const taskId = route.params.taskId as string
  if (!taskId) {
    message.error('文章ID不存在')
    return
  }

  loading.value = true
  try {
    const res = await getArticle(taskId)
    article.value = res.data
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 导出 Markdown
const exportMarkdown = () => {
  if (!article.value) return

  let markdown = `# ${article.value.mainTitle}\n\n`
  markdown += `> ${article.value.subTitle}\n\n`
  
  if (article.value.outline && article.value.outline.length > 0) {
    markdown += `## 目录\n\n`
    article.value.outline.forEach(item => {
      markdown += `${item.section}. ${item.title}\n`
    })
    markdown += `\n---\n\n`
  }

  markdown += article.value.content || ''

  if (article.value.images && article.value.images.length > 0) {
    markdown += `\n\n## 配图\n\n`
    article.value.images.forEach(image => {
      markdown += `![${image.description}](${image.url})\n\n`
    })
  }

  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${article.value.mainTitle}.md`
  a.click()
  URL.revokeObjectURL(url)
  
  message.success('导出成功')
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    PENDING: 'default',
    PROCESSING: 'processing',
    COMPLETED: 'success',
    FAILED: 'error',
  }
  return colorMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    PENDING: '等待中',
    PROCESSING: '生成中',
    COMPLETED: '已完成',
    FAILED: '失败',
  }
  return textMap[status] || status
}

onMounted(() => {
  loadArticle()
})
</script>

<style scoped lang="scss">
.article-detail-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;

  .container {
    max-width: 1000px;
    margin: 0 auto;
  }

  .header-actions {
    display: flex;
    justify-content: space-between;
    margin-bottom: 24px;
  }

  .title-section {
    margin-bottom: 24px;

    .main-title {
      font-size: 32px;
      font-weight: 700;
      margin: 0 0 12px;
      color: #1a1a1a;
    }

    .sub-title {
      font-size: 18px;
      color: #666;
      margin: 0 0 16px;
    }

    .meta-info {
      display: flex;
      align-items: center;
      gap: 12px;
      color: #999;
      font-size: 14px;
    }
  }

  .section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #1890ff;
  }

  .outline-section {
    margin-bottom: 32px;

    .outline-list {
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
  }

  .content-section {
    margin-bottom: 32px;

    .markdown-content {
      line-height: 1.8;
      font-size: 16px;
      color: #333;

      :deep(h2) {
        font-size: 24px;
        font-weight: 600;
        margin: 32px 0 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #eee;
      }

      :deep(h3) {
        font-size: 20px;
        font-weight: 600;
        margin: 24px 0 12px;
      }

      :deep(p) {
        margin-bottom: 16px;
        text-indent: 2em;
      }

      :deep(ul), :deep(ol) {
        margin-bottom: 16px;
        padding-left: 2em;
      }

      :deep(li) {
        margin-bottom: 8px;
      }
    }
  }

  .images-section {
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
}
</style>
