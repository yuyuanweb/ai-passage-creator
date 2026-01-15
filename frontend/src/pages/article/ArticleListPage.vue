<template>
  <div class="article-list-page">
    <div class="container">
      <div class="header">
        <h1>我的文章</h1>
        <a-button type="primary" size="large" @click="goToCreate">
          <template #icon>
            <PlusOutlined />
          </template>
          创作新文章
        </a-button>
      </div>

      <a-card :bordered="false">
        <a-table
          :columns="columns"
          :data-source="dataSource"
          :loading="loading"
          :pagination="pagination"
          @change="handleTableChange"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'title'">
              <div class="title-cell">
                <div class="main-title">{{ record.mainTitle || '-' }}</div>
                <div class="sub-title">{{ record.subTitle || '-' }}</div>
              </div>
            </template>

            <template v-else-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)">
                {{ getStatusText(record.status) }}
              </a-tag>
            </template>

            <template v-else-if="column.key === 'createTime'">
              {{ formatDate(record.createTime) }}
            </template>

            <template v-else-if="column.key === 'action'">
              <a-space>
                <a-button type="link" size="small" @click="viewArticle(record)">
                  查看
                </a-button>
                <a-popconfirm
                  title="确定要删除这篇文章吗?"
                  ok-text="确定"
                  cancel-text="取消"
                  @confirm="deleteArticle(record)"
                >
                  <a-button type="link" size="small" danger>删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { listArticle, deleteArticle as deleteArticleApi, type ArticleVO } from '@/api/articleController'
import dayjs from 'dayjs'

const router = useRouter()

const columns = [
  {
    title: '选题',
    dataIndex: 'topic',
    key: 'topic',
    width: 200,
  },
  {
    title: '标题',
    key: 'title',
    width: 300,
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
  },
  {
    title: '创建时间',
    key: 'createTime',
    width: 180,
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
  },
]

const loading = ref(false)
const dataSource = ref<ArticleVO[]>([])
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await listArticle({
      pageNum: pagination.value.current,
      pageSize: pagination.value.pageSize,
    })
    dataSource.value = res.data.records || []
    pagination.value.total = res.data.totalRow || 0
  } catch (error: any) {
    message.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 表格变化
const handleTableChange = (pag: any) => {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  loadData()
}

// 查看文章
const viewArticle = (record: ArticleVO) => {
  router.push(`/article/${record.taskId}`)
}

// 删除文章
const deleteArticle = async (record: ArticleVO) => {
  try {
    await deleteArticleApi(record.id)
    message.success('删除成功')
    loadData()
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

// 跳转创作页面
const goToCreate = () => {
  router.push('/create')
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
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
  loadData()
})
</script>

<style scoped lang="scss">
.article-list-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;

  .container {
    max-width: 1400px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h1 {
      font-size: 24px;
      font-weight: 600;
      margin: 0;
    }
  }

  .title-cell {
    .main-title {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 4px;
      color: #1a1a1a;
    }

    .sub-title {
      font-size: 12px;
      color: #999;
    }
  }
}
</style>
