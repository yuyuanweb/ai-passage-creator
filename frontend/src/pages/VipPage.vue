<template>
  <div class="vip-page">
    <div class="vip-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-badge">
          <CrownOutlined />
          <span>会员专属</span>
        </div>
        <h1 class="page-title">升级永久会员</h1>
        <p class="page-subtitle">解锁全部高级功能，无限创作配额，终身有效</p>
      </div>

      <!-- 主内容区：左右布局 -->
      <div class="main-section">
        <!-- 左侧：价格卡片 -->
        <div class="pricing-card">
          <div class="pricing-badge">限时优惠</div>
          <div class="pricing-header">
            <div class="plan-icon">
              <CrownOutlined />
            </div>
            <h2 class="plan-name">永久会员</h2>
            <div class="price-display">
              <span class="currency">$</span>
              <span class="price">199</span>
              <span class="period">/永久</span>
            </div>
            <div class="original-price">
              <span class="original-label">原价</span>
              <span class="original-value">$299</span>
            </div>
          </div>

          <div class="pricing-divider"></div>

          <div class="pricing-features">
            <div v-for="(item, index) in pricingFeatures" :key="index" class="pricing-feature">
              <CheckCircleOutlined class="feature-check" />
              <span>{{ item }}</span>
            </div>
          </div>

          <a-button
            type="primary"
            size="large"
            :loading="purchasing"
            :disabled="isVip"
            @click="handlePurchase"
            class="purchase-btn"
          >
            <template #icon>
              <ThunderboltOutlined />
            </template>
            {{ isVip ? '您已是永久会员' : '立即升级' }}
          </a-button>

          <div class="security-notice">
            <SafetyOutlined />
            <span>安全支付 · 7天无理由退款</span>
          </div>
        </div>

        <!-- 右侧：会员特权 -->
        <div class="features-section">
          <h3 class="features-title">
            <GiftOutlined />
            会员特权
          </h3>
          <div class="features-grid">
            <div v-for="(feature, index) in features" :key="index" class="feature-card">
              <div class="feature-icon-wrapper">
                <component :is="feature.icon" class="feature-icon" />
              </div>
              <div class="feature-content">
                <h4 class="feature-title">{{ feature.title }}</h4>
                <p class="feature-desc">{{ feature.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 常见问题 -->
      <div class="faq-section">
        <div class="section-header">
          <QuestionCircleOutlined class="section-icon" />
          <h2 class="section-title">常见问题</h2>
        </div>
        <div class="faq-grid">
          <div v-for="(faq, index) in faqs" :key="index" class="faq-card">
            <h4 class="faq-question">{{ faq.question }}</h4>
            <p class="faq-answer">{{ faq.answer }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  CheckCircleOutlined,
  CrownOutlined,
  SafetyOutlined,
  ThunderboltOutlined,
  RocketOutlined,
  PictureOutlined,
  AppstoreOutlined,
  EditOutlined,
  StarOutlined,
  GiftOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons-vue'
import { useLoginUserStore } from '@/stores/loginUser'
import { createVipPaymentSession } from '@/api/paymentController'
import { isVip as checkIsVip } from '@/utils/permission'

const router = useRouter()
const route = useRoute()
const loginUserStore = useLoginUserStore()
const purchasing = ref(false)

// 是否是 VIP（管理员也视为 VIP）
const isVip = computed(() => checkIsVip(loginUserStore.loginUser))

// 会员特权列表
const features = [
  {
    icon: RocketOutlined,
    title: '无限创作配额',
    desc: '无限次使用文章创作功能，告别配额限制'
  },
  {
    icon: PictureOutlined,
    title: 'AI 智能生图',
    desc: '使用 Nano Banana AI 生成独特配图'
  },
  {
    icon: AppstoreOutlined,
    title: 'SVG 图表生成',
    desc: '自动生成精美的概念示意图和思维导图'
  },
  {
    icon: EditOutlined,
    title: 'AI 大纲编辑',
    desc: '使用 AI 助手快速优化文章大纲'
  },
  {
    icon: StarOutlined,
    title: '优先队列',
    desc: '享受更快的生成速度和优先服务'
  },
  {
    icon: GiftOutlined,
    title: '终身有效',
    desc: '一次购买，永久使用，无需续费'
  }
]

// 价格卡片特性
const pricingFeatures = [
  '无限创作配额',
  '全部高级配图功能',
  'AI 大纲智能编辑',
  '优先生成队列',
  '终身有效'
]

// FAQ 列表
const faqs = [
  {
    question: '支付后多久生效？',
    answer: '支付成功后立即生效，您将立即获得永久会员权限，刷新页面即可看到变化。'
  },
  {
    question: '如何申请退款？',
    answer: '购买后 7 天内，如不满意可申请退款，退款后会员权限将被取消。'
  },
  {
    question: '会员是否需要续费？',
    answer: '不需要。永久会员一次购买，终身有效，无需任何续费。'
  },
  {
    question: '支付安全吗？',
    answer: '我们使用 Stripe 国际支付平台，全程加密传输，安全可靠。'
  }
]

// 检查支付结果
onMounted(async () => {
  const success = route.query.success
  const cancelled = route.query.cancelled

  if (success === 'true') {
    await loginUserStore.fetchLoginUser()
    Modal.success({
      title: '支付成功！',
      content: '恭喜您成为永久会员，已解锁全部高级功能！',
      okText: '开始创作',
      onOk: () => {
        router.push('/create')
      }
    })
    router.replace('/vip')
  } else if (cancelled === 'true') {
    message.info('支付已取消')
    router.replace('/vip')
  }
})

// 购买处理
const handlePurchase = async () => {
  if (!loginUserStore.loginUser.id) {
    message.warning('请先登录')
    router.push('/user/login')
    return
  }

  if (isVip.value) {
    message.info('您已经是永久会员')
    return
  }

  purchasing.value = true
  try {
    const res = await createVipPaymentSession()
    if (res.data.code === 0 && res.data.data) {
      window.location.href = res.data.data
    } else {
      message.error(res.data.message || '创建支付失败')
    }
  } catch (error) {
    console.error('创建支付失败:', error)
    message.error('创建支付失败，请稀后重试')
  } finally {
    purchasing.value = false
  }
}
</script>

<style scoped lang="scss">
.vip-page {
  min-height: calc(100vh - 64px);
  background: var(--gradient-hero);
  padding: 48px 24px 80px;
}

.vip-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  color: var(--color-primary-dark);
  margin-bottom: 20px;

  .anticon {
    font-size: 14px;
  }
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 12px;
  color: var(--color-text);
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 主内容区 */
.main-section {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 32px;
  margin-bottom: 56px;
}

/* 价格卡片 */
.pricing-card {
  background: white;
  border-radius: var(--radius-xl);
  padding: 36px 32px;
  box-shadow: var(--shadow-xl);
  border: 2px solid var(--color-primary);
  position: relative;
  height: fit-content;
  position: sticky;
  top: 88px;
}

.pricing-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--gradient-primary);
  color: white;
  padding: 6px 20px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  box-shadow: var(--shadow-green);
}

.pricing-header {
  text-align: center;
  padding-bottom: 20px;
}

.plan-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(34, 197, 94, 0.1);
  border-radius: var(--radius-lg);

  .anticon {
    font-size: 26px;
    color: var(--color-primary);
  }
}

.plan-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 14px;
  color: var(--color-text);
}

.price-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 6px;
}

.currency {
  font-size: 18px;
  color: var(--color-text-secondary);
  margin-right: 2px;
  font-weight: 500;
}

.price {
  font-size: 52px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.period {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-left: 4px;
}

.original-price {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
}

.original-label {
  color: var(--color-text-muted);
}

.original-value {
  color: var(--color-text-muted);
  text-decoration: line-through;
}

.pricing-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 20px 0;
}

.pricing-features {
  margin-bottom: 24px;
}

.pricing-feature {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 14px;
  color: var(--color-text);

  .feature-check {
    color: var(--color-primary);
    font-size: 15px;
    flex-shrink: 0;
  }
}

.purchase-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  background: var(--gradient-primary) !important;
  border: none !important;
  box-shadow: var(--shadow-green) !important;
  border-radius: var(--radius-md) !important;

  &:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-1px);
  }

  &:disabled {
    background: var(--color-background-tertiary) !important;
    color: var(--color-text-secondary) !important;
    box-shadow: none !important;
  }
}

.security-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
  font-size: 12px;
  color: var(--color-text-secondary);

  .anticon {
    color: var(--color-primary);
    font-size: 13px;
  }
}

/* 会员特权 */
.features-section {
  background: white;
  border-radius: var(--radius-xl);
  padding: 32px;
  border: 1px solid var(--color-border);
}

.features-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 24px;
  color: var(--color-text);

  .anticon {
    color: var(--color-primary);
    font-size: 20px;
  }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: var(--color-background-secondary);
  border-radius: var(--radius-lg);
  transition: all var(--transition-normal);

  &:hover {
    background: rgba(34, 197, 94, 0.06);
  }
}

.feature-icon-wrapper {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(34, 197, 94, 0.1);
  border-radius: var(--radius-md);
}

.feature-icon {
  font-size: 18px;
  color: var(--color-primary);
}

.feature-content {
  flex: 1;
  min-width: 0;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--color-text);
}

.feature-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* FAQ 部分 */
.faq-section {
  background: white;
  border-radius: var(--radius-xl);
  padding: 32px;
  border: 1px solid var(--color-border);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}

.section-icon {
  font-size: 20px;
  color: var(--color-primary);
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.faq-card {
  padding: 20px;
  background: var(--color-background-secondary);
  border-radius: var(--radius-lg);
}

.faq-question {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.faq-answer {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 992px) {
  .main-section {
    grid-template-columns: 1fr;
  }

  .pricing-card {
    position: static;
    max-width: 400px;
    margin: 0 auto;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .faq-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .vip-page {
    padding: 32px 16px 60px;
  }

  .page-title {
    font-size: 28px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .pricing-card {
    padding: 28px 24px;
  }

  .price {
    font-size: 44px;
  }

  .features-section,
  .faq-section {
    padding: 24px;
  }
}
</style>
