<template>
  <div class="outline-editing-stage">
    <div class="stage-header">
      <h2 class="stage-title">编辑文章大纲</h2>
      <p class="stage-subtitle">您可以编辑、调整章节顺序，或添加新章节</p>
    </div>

    <div class="outline-list" ref="outlineListRef">
      <div
        v-for="(section, index) in outlineSections"
        :key="section.section"
        class="outline-section"
        :data-section-id="section.section"
      >
        <div class="section-header">
          <span class="drag-handle" title="拖动排序">⋮⋮</span>
          <span class="section-number">{{ index + 1 }}</span>
          <a-input
            v-model:value="section.title"
            placeholder="章节标题"
            class="section-title-input"
          />
          <a-button
            type="text"
            danger
            @click="deleteSection(index)"
            class="delete-btn"
          >
            <template #icon>
              <DeleteOutlined />
            </template>
          </a-button>
        </div>

        <div class="section-points">
          <div v-for="(point, pointIdx) in section.points" :key="pointIdx" class="point-item">
            <span class="point-bullet">•</span>
            <a-input
              v-model:value="section.points[pointIdx]"
              placeholder="要点内容"
              class="point-input"
            />
            <a-button
              type="text"
              size="small"
              @click="deletePoint(index, pointIdx)"
              class="delete-point-btn"
            >
              ×
            </a-button>
          </div>
          <a-button
            type="dashed"
            @click="addPoint(index)"
            class="add-point-btn"
          >
            <template #icon>
              <PlusOutlined />
            </template>
            添加要点
          </a-button>
        </div>
      </div>
    </div>

    <div class="ai-chat-section" :class="{ 'vip-only': !isVip }">
      <div class="chat-header">
        <RobotOutlined />
        <span>AI 助手修改大纲</span>
        <span v-if="!isVip" class="vip-badge-small">
          <CrownOutlined />
          VIP
        </span>
      </div>
      <div v-if="isVip" class="chat-input-wrapper">
        <a-textarea
          v-model:value="modifySuggestion"
          placeholder="告诉 AI 如何修改大纲，例如：请在第二章节后增加一个关于实践案例的章节"
          :rows="3"
          :maxlength="500"
          show-count
          class="chat-textarea"
        />
        <a-button
          type="primary"
          :loading="aiModifying"
          :disabled="!modifySuggestion.trim()"
          @click="handleAiModify"
          class="ai-modify-btn"
        >
          <template #icon>
            <RobotOutlined />
          </template>
          AI 修改大纲
        </a-button>
      </div>
      <div v-else class="vip-upgrade-notice">
        <CrownOutlined class="vip-icon" />
        <p>AI 修改大纲功能仅限 VIP 会员使用</p>
        <RouterLink to="/vip" class="upgrade-btn">
          立即升级 VIP
        </RouterLink>
      </div>
    </div>

    <div class="actions">
      <a-button
        size="large"
        @click="addSection"
        class="add-section-btn"
      >
        <template #icon>
          <PlusOutlined />
        </template>
        添加章节
      </a-button>

      <a-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!canConfirm"
        @click="handleConfirm"
        class="confirm-btn"
      >
        <template #icon>
          <CheckOutlined />
        </template>
        确认并生成正文
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { CheckOutlined, DeleteOutlined, PlusOutlined, RobotOutlined, CrownOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import Sortable from 'sortablejs'
import { aiModifyOutline } from '@/api/articleController'
import { useLoginUserStore } from '@/stores/loginUser'
import { isVip as checkIsVip } from '@/utils/permission'

interface OutlineSection {
  section: number
  title: string
  points: string[]
}

interface Props {
  outline: API.OutlineSection[]
  taskId: string
  loading?: boolean
}

interface Emits {
  (e: 'confirm', outline: OutlineSection[]): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

const loginUserStore = useLoginUserStore()

// 判断是否为 VIP（管理员也视为 VIP）
const isVip = computed(() => checkIsVip(loginUserStore.loginUser))

// 转换 API 类型为内部类型
const outlineSections = ref<OutlineSection[]>(
  props.outline.map((item, index) => ({
    section: item.section ?? index + 1,
    title: item.title ?? '',
    points: item.points ?? []
  }))
)
const outlineListRef = ref<HTMLElement | null>(null)
const modifySuggestion = ref('')
const aiModifying = ref(false)

const canConfirm = computed(() => {
  return outlineSections.value.length > 0 &&
         outlineSections.value.every(section =>
           section.title.trim() &&
           section.points.length > 0 &&
           section.points.every(point => point.trim())
         )
})

onMounted(() => {
  nextTick(() => {
    if (outlineListRef.value) {
      Sortable.create(outlineListRef.value, {
        animation: 150,
        handle: '.drag-handle',
        onEnd: (evt) => {
          const { oldIndex, newIndex } = evt
          if (oldIndex !== undefined && newIndex !== undefined) {
            const item = outlineSections.value.splice(oldIndex, 1)[0]
            outlineSections.value.splice(newIndex, 0, item)
            // 更新 section 序号
            outlineSections.value.forEach((sec, idx) => {
              sec.section = idx + 1
            })
          }
        }
      })
    }
  })
})

const addSection = () => {
  const newSection: OutlineSection = {
    section: outlineSections.value.length + 1,
    title: '',
    points: ['']
  }
  outlineSections.value.push(newSection)
}

const deleteSection = (index: number) => {
  outlineSections.value.splice(index, 1)
  // 更新 section 序号
  outlineSections.value.forEach((sec, idx) => {
    sec.section = idx + 1
  })
}

const addPoint = (sectionIndex: number) => {
  outlineSections.value[sectionIndex].points.push('')
}

const deletePoint = (sectionIndex: number, pointIndex: number) => {
  const section = outlineSections.value[sectionIndex]
  if (section.points.length > 1) {
    section.points.splice(pointIndex, 1)
  }
}

const handleConfirm = () => {
  emit('confirm', outlineSections.value)
}

const handleAiModify = async () => {
  if (!modifySuggestion.value.trim()) {
    message.warning('请输入修改建议')
    return
  }

  aiModifying.value = true
  try {
    const res = await aiModifyOutline({
      taskId: props.taskId,
      modifySuggestion: modifySuggestion.value
    })

    if (res.data.data) {
      outlineSections.value = res.data.data.map((item, index) => ({
        section: item.section ?? index + 1,
        title: item.title ?? '',
        points: item.points ?? []
      }))
      modifySuggestion.value = ''
      message.success('AI 已根据您的建议修改大纲')
    }
  } catch (error) {
    const err = error as Error
    message.error(err.message || 'AI 修改失败')
  } finally {
    aiModifying.value = false
  }
}
</script>

<style scoped lang="scss">
.outline-editing-stage {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

.stage-header {
  text-align: center;
  margin-bottom: 40px;
}

.stage-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px;
  color: var(--color-text);
}

.stage-subtitle {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
}

.outline-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 32px;
}

.outline-section {
  background: var(--color-background-secondary);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  transition: all 0.2s;

  &:hover {
    border-color: var(--color-primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.drag-handle {
  cursor: grab;
  font-size: 20px;
  color: var(--color-text-muted);
  user-select: none;
  line-height: 1;

  &:active {
    cursor: grabbing;
  }

  &:hover {
    color: var(--color-primary);
  }
}

.section-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.section-title-input {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
}

.delete-btn {
  flex-shrink: 0;
}

.section-points {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-left: 44px;
}

.point-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.point-bullet {
  color: var(--color-primary);
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}

.point-input {
  flex: 1;
  font-size: 14px;
}

.delete-point-btn {
  font-size: 18px;
  color: var(--color-text-muted);
  padding: 0;
  width: 24px;
  height: 24px;
  flex-shrink: 0;

  &:hover {
    color: #ff4d4f;
  }
}

.add-point-btn {
  align-self: flex-start;
}

.ai-chat-section {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05) 0%, rgba(34, 197, 94, 0.02) 100%);
  border: 2px dashed var(--color-primary);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 32px;

  &.vip-only {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.05) 0%, rgba(22, 163, 74, 0.02) 100%);
    border-color: var(--color-primary);
  }
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 16px;

  .anticon {
    font-size: 18px;
  }

  .vip-badge-small {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: var(--radius-full);
    font-size: 11px;
    font-weight: 600;
    background: var(--gradient-primary);
    color: white;
    margin-left: auto;
  }
}

.vip-upgrade-notice {
  text-align: center;
  padding: 20px;

  .vip-icon {
    font-size: 48px;
    color: var(--color-primary);
    margin-bottom: 12px;
  }

  p {
    margin: 0 0 16px;
    color: var(--color-text-secondary);
    font-size: 14px;
  }

  .upgrade-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 10px 24px;
    border-radius: var(--radius-md);
    font-size: 14px;
    font-weight: 600;
    background: var(--gradient-primary);
    color: white;
    text-decoration: none;
    transition: all 0.3s;
    box-shadow: var(--shadow-green);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(34, 197, 94, 0.35);
      color: white;
    }
  }
}

.chat-input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.chat-textarea {
  flex: 1;
  font-size: 14px;
  line-height: 1.6;
}

.ai-modify-btn {
  height: 40px;
  padding: 0 20px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.add-section-btn,
.confirm-btn {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius-lg);
}

.confirm-btn {
  background: var(--gradient-primary) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 4px 14px rgba(34, 197, 94, 0.3) !important;

  &:hover:not(:disabled) {
    opacity: 0.92;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4) !important;
  }

  &:disabled {
    background: var(--color-border) !important;
    box-shadow: none !important;
    opacity: 0.6;
  }
}
</style>
