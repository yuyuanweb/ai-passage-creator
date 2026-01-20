<template>
  <div class="title-selecting-stage">
    <div class="stage-header">
      <h2 class="stage-title">选择标题方案</h2>
      <p class="stage-subtitle">AI 为您生成了以下标题，请选择一个或自定义</p>
    </div>
    
    <a-radio-group v-model:value="selectedIndex" class="title-options">
      <div v-for="(option, index) in titleOptions" :key="index" class="title-option">
        <a-radio :value="index">
          <div class="title-content">
            <div class="title-main">{{ option.mainTitle }}</div>
            <div class="title-sub">{{ option.subTitle }}</div>
          </div>
        </a-radio>
      </div>
      <div class="title-option custom">
        <a-radio :value="-1">
          <div class="title-content">
            <div class="title-main">自定义标题</div>
          </div>
        </a-radio>
        <div v-if="selectedIndex === -1" class="custom-inputs">
          <a-input 
            v-model:value="customMainTitle" 
            placeholder="输入主标题" 
            class="custom-input"
          />
          <a-input 
            v-model:value="customSubTitle" 
            placeholder="输入副标题" 
            class="custom-input"
          />
        </div>
      </div>
    </a-radio-group>
    
    <div class="description-section">
      <label class="section-label">补充描述（可选）</label>
      <p class="section-tip">补充您对文章的期望、重点强调的内容等</p>
      <a-textarea 
        v-model:value="userDescription" 
        placeholder="例如：请重点强调技术原理，用通俗的语言讲解..."
        :rows="4"
        :maxlength="500"
        show-count
        class="description-textarea"
      />
    </div>
    
    <div class="actions">
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
        确认并生成大纲
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CheckOutlined } from '@ant-design/icons-vue'

interface TitleOption {
  mainTitle: string
  subTitle: string
}

interface Props {
  titleOptions: TitleOption[]
  loading?: boolean
}

interface Emits {
  (e: 'confirm', data: {
    mainTitle: string
    subTitle: string
    userDescription: string
  }): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

const selectedIndex = ref<number>(0)
const customMainTitle = ref('')
const customSubTitle = ref('')
const userDescription = ref('')

const canConfirm = computed(() => {
  if (selectedIndex.value === -1) {
    return customMainTitle.value.trim() && customSubTitle.value.trim()
  }
  return selectedIndex.value >= 0 && selectedIndex.value < props.titleOptions.length
})

const handleConfirm = () => {
  let mainTitle = ''
  let subTitle = ''
  
  if (selectedIndex.value === -1) {
    mainTitle = customMainTitle.value
    subTitle = customSubTitle.value
  } else {
    const selected = props.titleOptions[selectedIndex.value]
    mainTitle = selected.mainTitle
    subTitle = selected.subTitle
  }
  
  emit('confirm', {
    mainTitle,
    subTitle,
    userDescription: userDescription.value
  })
}
</script>

<style scoped lang="scss">
.title-selecting-stage {
  max-width: 900px;
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

.title-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
  width: 100%;
}

.title-option {
  padding: 20px;
  background: var(--color-background-secondary);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all 0.2s;

  &:hover {
    border-color: var(--color-primary);
    background: rgba(34, 197, 94, 0.04);
  }

  :deep(.ant-radio-wrapper) {
    width: 100%;
    align-items: flex-start;
  }

  :deep(.ant-radio) {
    margin-top: 4px;
  }
}

.title-content {
  flex: 1;
  margin-left: 12px;
}

.title-main {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
  line-height: 1.4;
}

.title-sub {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.custom-inputs {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-left: 32px;
}

.custom-input {
  font-size: 15px;
  padding: 12px 16px;
}

.description-section {
  margin-bottom: 32px;
}

.section-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 6px;
}

.section-tip {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 12px;
}

.description-textarea {
  font-size: 15px;
  line-height: 1.6;
  border-radius: var(--radius-md);
}

.actions {
  display: flex;
  justify-content: center;
}

.confirm-btn {
  height: 48px;
  padding: 0 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius-lg);
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
