<template>
  <div class="system-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统设置</h1>
        <p class="page-subtitle">配置告警通知与系统参数</p>
      </div>
    </header>

    <!-- 标签页导航 -->
    <div class="tabs-wrapper">
      <div class="tabs-nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon">
            <component :is="tab.icon" />
          </span>
          <span class="tab-label">{{ tab.label }}</span>
          <span class="tab-indicator"></span>
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <main class="page-content">
      <!-- 告警配置 -->
      <section v-show="activeTab === 'alert'" class="content-section">
        <div class="settings-grid">
          <!-- 紧急联系人 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon contact">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>紧急联系人</h3>
                <p>接收告警通知的紧急联系人信息</p>
              </div>
            </div>
            <div class="card-body">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">联系人姓名</label>
                  <input
                    v-model="alertConfig.emergency_contact"
                    type="text"
                    class="form-input"
                    placeholder="请输入联系人姓名"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">联系电话</label>
                  <input
                    v-model="alertConfig.emergency_phone"
                    type="tel"
                    class="form-input"
                    placeholder="请输入联系电话"
                  />
                </div>
                <div class="form-group full-width">
                  <label class="form-label">通知邮箱</label>
                  <input
                    v-model="alertConfig.email"
                    type="email"
                    class="form-input"
                    placeholder="请输入邮箱地址"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 告警方式 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon bell">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>告警方式</h3>
                <p>配置不同风险等级的通知方式</p>
              </div>
            </div>
            <div class="card-body">
              <div class="alert-levels">
                <div class="alert-level high">
                  <div class="level-header">
                    <span class="level-badge">高风险</span>
                    <span class="level-desc">需要立即处理的紧急事件</span>
                  </div>
                  <div class="level-options">
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.high_alert_methods" value="sms" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">短信通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.high_alert_methods" value="email" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">邮件通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.high_alert_methods" value="app" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">APP推送</span>
                    </label>
                  </div>
                </div>

                <div class="alert-level medium">
                  <div class="level-header">
                    <span class="level-badge">中风险</span>
                    <span class="level-desc">需要关注的潜在问题</span>
                  </div>
                  <div class="level-options">
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.medium_alert_methods" value="sms" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">短信通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.medium_alert_methods" value="email" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">邮件通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.medium_alert_methods" value="app" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">APP推送</span>
                    </label>
                  </div>
                </div>

                <div class="alert-level low">
                  <div class="level-header">
                    <span class="level-badge">低风险</span>
                    <span class="level-desc">一般性提示信息</span>
                  </div>
                  <div class="level-options">
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.low_alert_methods" value="sms" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">短信通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.low_alert_methods" value="email" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">邮件通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.low_alert_methods" value="app" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">APP推送</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 免打扰时段 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon moon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>免打扰时段</h3>
                <p>设置静默时段，减少打扰</p>
              </div>
            </div>
            <div class="card-body">
              <div class="quiet-hours">
                <div class="time-range">
                  <div class="time-input">
                    <label class="form-label">开始时间</label>
                    <input
                      v-model="quietHoursStart"
                      type="time"
                      class="form-input"
                    />
                  </div>
                  <span class="time-separator">至</span>
                  <div class="time-input">
                    <label class="form-label">结束时间</label>
                    <input
                      v-model="quietHoursEnd"
                      type="time"
                      class="form-input"
                    />
                  </div>
                </div>
                <div class="quiet-option">
                  <label class="toggle-item">
                    <input type="checkbox" v-model="alertConfig.bypass_quiet_hours" />
                    <span class="toggle-switch"></span>
                    <div class="toggle-text">
                      <span class="toggle-label">高风险免打扰</span>
                      <span class="toggle-desc">开启后，高风险事件在免打扰时段仍会通知</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="actions-bar">
          <button class="btn-secondary" @click="resetConfig">重置</button>
          <button class="btn-primary" :disabled="saving" @click="saveConfig">
            <svg v-if="saving" class="spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="10"/>
            </svg>
            <span>{{ saving ? '保存中...' : '保存配置' }}</span>
          </button>
        </div>
      </section>

      <!-- 检测配置 -->
      <section v-show="activeTab === 'detect'" class="content-section">
        <div class="settings-grid">
          <!-- 跌倒检测参数 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon warning">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>跌倒检测</h3>
                <p>跌倒事件的判定参数</p>
              </div>
            </div>
            <div class="card-body">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">确认帧数</label>
                  <input
                    v-model.number="detectConfig.fallen_confirm_frames"
                    type="number"
                    min="1"
                    max="30"
                    class="form-input"
                    placeholder="连续跌倒帧数阈值"
                  />
                  <span class="form-hint">连续检测到跌倒的帧数阈值</span>
                </div>
                <div class="form-group">
                  <label class="form-label">升级时间（秒）</label>
                  <input
                    v-model.number="detectConfig.fallen_escalate_secs"
                    type="number"
                    min="0.5"
                    max="10"
                    step="0.5"
                    class="form-input"
                    placeholder="跌倒升级时间"
                  />
                  <span class="form-hint">跌倒持续多久后升级为高风险</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 静止检测参数 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>静止检测</h3>
                <p>长时间静止的判定参数</p>
              </div>
            </div>
            <div class="card-body">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">判定窗口（秒）</label>
                  <input
                    v-model.number="detectConfig.stillness_window_secs"
                    type="number"
                    min="10"
                    max="120"
                    class="form-input"
                    placeholder="静止判定窗口时长"
                  />
                  <span class="form-hint">静止判定的时间窗口</span>
                </div>
                <div class="form-group">
                  <label class="form-label">移动阈值（像素）</label>
                  <input
                    v-model.number="detectConfig.stillness_movement_threshold"
                    type="number"
                    min="1"
                    max="50"
                    class="form-input"
                    placeholder="静止判定阈值"
                  />
                  <span class="form-hint">移动距离小于此值认为静止</span>
                </div>
                <div class="form-group">
                  <label class="form-label">升级时间（秒）</label>
                  <input
                    v-model.number="detectConfig.stillness_escalate_secs"
                    type="number"
                    min="30"
                    max="300"
                    class="form-input"
                    placeholder="静止升级时间"
                  />
                  <span class="form-hint">静止持续多久后升级为中风险</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 夜间时段与追踪参数 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon moon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>时段与追踪</h3>
                <p>夜间时段与人员追踪参数</p>
              </div>
            </div>
            <div class="card-body">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">夜间开始（时）</label>
                  <input
                    v-model.number="detectConfig.night_start_hour"
                    type="number"
                    min="0"
                    max="23"
                    class="form-input"
                    placeholder="22"
                  />
                  <span class="form-hint">夜间时段开始小时</span>
                </div>
                <div class="form-group">
                  <label class="form-label">夜间结束（时）</label>
                  <input
                    v-model.number="detectConfig.night_end_hour"
                    type="number"
                    min="0"
                    max="23"
                    class="form-input"
                    placeholder="7"
                  />
                  <span class="form-hint">夜间时段结束小时</span>
                </div>
                <div class="form-group">
                  <label class="form-label">宽限期（秒）</label>
                  <input
                    v-model.number="detectConfig.lost_grace_secs"
                    type="number"
                    min="0.5"
                    max="10"
                    step="0.5"
                    class="form-input"
                    placeholder="人员消失宽限期"
                  />
                  <span class="form-hint">人员消失后的判定宽限时间</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 人脸模糊参数 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon privacy">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>人脸模糊</h3>
                <p>隐私保护的人脸检测与模糊参数</p>
              </div>
            </div>
            <div class="card-body">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">检测置信度</label>
                  <input
                    v-model.number="detectConfig.face_detection_confidence"
                    type="number"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    class="form-input"
                    placeholder="0.5"
                  />
                  <span class="form-hint">人脸检测的最小置信度阈值（0.1-1.0）</span>
                </div>
                <div class="form-group">
                  <label class="form-label">模糊强度</label>
                  <input
                    v-model.number="detectConfig.face_blur_strength"
                    type="number"
                    min="15"
                    max="99"
                    step="2"
                    class="form-input"
                    placeholder="51"
                  />
                  <span class="form-hint">模糊核大小，值越大越模糊（15-99，需为奇数）</span>
                </div>
                <div class="form-group">
                  <label class="form-label">扩展比例</label>
                  <input
                    v-model.number="detectConfig.face_blur_expand_ratio"
                    type="number"
                    min="0"
                    max="1.0"
                    step="0.1"
                    class="form-input"
                    placeholder="0.5"
                  />
                  <span class="form-hint">模糊区域相对于人脸框的扩展比例</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="actions-bar">
          <button class="btn-secondary" @click="resetDetectConfig">重置</button>
          <button class="btn-primary" :disabled="detectSaving" @click="saveDetectConfig">
            <svg v-if="detectSaving" class="spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="10"/>
            </svg>
            <span>{{ detectSaving ? '保存中...' : '保存配置' }}</span>
          </button>
        </div>
      </section>

      <!-- 社区组选择（仅普通用户） -->
      <section v-show="activeTab === 'community'" class="content-section">
        <div class="settings-card">
          <div class="card-header">
            <div class="header-text">
              <h3>社区组选择</h3>
              <p>选择您所属的社区组，可随时切换</p>
            </div>
          </div>
          <div class="card-body">
            <div class="form-group">
              <label class="form-label">当前社区组</label>
              <div v-if="currentCommunity" class="current-community">
                <span class="community-name">{{ currentCommunity.name }}</span>
                <span class="community-org">{{ currentCommunity.org_name }}</span>
                <button class="btn-unbind" @click="unbindCommunity">取消绑定</button>
              </div>
              <div v-else class="no-community">未选择社区组</div>
            </div>
            <div class="form-group">
              <label class="form-label">选择社区组</label>
              <input v-model="communitySearch" placeholder="搜索社区组..." class="form-input" @input="searchCommunities" />
              <div class="community-list" v-if="availableGroups.length > 0">
                <div
                  v-for="g in availableGroups"
                  :key="g.id"
                  class="community-item"
                  :class="{ selected: currentCommunity?.id === g.id }"
                  @click="selectCommunity(g)"
                >
                  <div class="community-info">
                    <span class="community-name">{{ g.name }}</span>
                    <span class="community-meta">{{ g.org_name }} · {{ g.member_count }} 人</span>
                  </div>
                  <span v-if="currentCommunity?.id === g.id" class="check-mark">✓</span>
                </div>
              </div>
              <div v-else class="no-results">暂无可选社区组</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import {
  getAlertConfig,
  updateAlertConfig,
  acknowledgeAlert as ackAlert,
  resendAlert as resendAlertApi
} from '@/api/alerts'
import {
  getDetectConfig,
  updateDetectConfig
} from '@/api/detect'
import { getAvailableGroups, getUserCommunity, setUserCommunity } from '@/api/platform'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

// 标签页配置
const authStore = useAuthStore()
const isUser = computed(() => authStore.user?.role === 'user')

const tabs = computed(() => {
  const items = [
    {
      key: 'alert',
      label: '告警配置',
      icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('path', { d: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9' }),
        h('path', { d: 'M13.73 21a2 2 0 0 1-3.46 0' })
      ])
    },
    {
      key: 'detect',
      label: '检测配置',
      icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('circle', { cx: '12', cy: '12', r: '3' }),
        h('path', { d: 'M12 1v6m0 6v10' }),
        h('path', { d: 'M4.22 4.22l4.24 4.24m7.08 7.08l4.24 4.24' }),
        h('path', { d: 'M1 12h6m6 0h10' }),
        h('path', { d: 'M4.22 19.78l4.24-4.24m7.08-7.08l4.24-4.24' })
      ])
    },
  ]
  if (isUser.value) {
    items.push({
      key: 'community',
      label: '社区组',
      icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('path', { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
        h('circle', { cx: '9', cy: '7', r: '4' }),
        h('path', { d: 'M23 21v-2a4 4 0 0 0-3-3.87' }),
        h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' })
      ])
    })
  }
  return items
})

const activeTab = ref('alert')
const saving = ref(false)

// 告警配置
const alertConfig = ref({
  emergency_contact: '',
  emergency_phone: '',
  email: '',
  high_alert_methods: ['sms', 'email', 'app'],
  medium_alert_methods: ['email', 'app'],
  low_alert_methods: ['app'],
  quiet_hours_start: '22:00',
  quiet_hours_end: '07:00',
  bypass_quiet_hours: true
})

const quietHoursStart = ref('22:00')
const quietHoursEnd = ref('07:00')

// 检测配置
const detectConfig = ref({
  fallen_confirm_frames: 5,
  fallen_escalate_secs: 1.0,
  stillness_window_secs: 30.0,
  stillness_movement_threshold: 5.0,
  stillness_escalate_secs: 60.0,
  night_start_hour: 22,
  night_end_hour: 7,
  lost_grace_secs: 1.0,
  face_detection_confidence: 0.5,
  face_blur_strength: 51,
  face_blur_expand_ratio: 0.5
})
const detectSaving = ref(false)

// 工具函数
const getEventTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常' }
  return map[type] || type
}

const getRiskLabel = (level) => {
  const map = { HIGH: '高风险', MEDIUM: '中风险', LOW: '低风险' }
  return map[level] || level
}

const getRiskClass = (level) => {
  const map = { HIGH: 'risk-high', MEDIUM: 'risk-medium', LOW: 'risk-low' }
  return map[level] || ''
}

const getStatusLabel = (status) => {
  const map = { pending: '待发送', sent: '已发送', failed: '失败', acknowledged: '已确认' }
  return map[status] || status
}

const getStatusClass = (status) => {
  const map = { pending: 'status-pending', sent: 'status-sent', failed: 'status-failed', acknowledged: 'status-confirmed' }
  return map[status] || ''
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载配置
const loadConfig = async () => {
  try {
    const config = await getAlertConfig()
    if (config) {
      alertConfig.value = {
        ...alertConfig.value,
        ...config,
        high_alert_methods: config.high_alert_methods?.split(',') || ['sms', 'email', 'app'],
        medium_alert_methods: config.medium_alert_methods?.split(',') || ['email', 'app'],
        low_alert_methods: config.low_alert_methods?.split(',') || ['app']
      }
      quietHoursStart.value = config.quiet_hours_start || '22:00'
      quietHoursEnd.value = config.quiet_hours_end || '07:00'
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  try {
    await updateAlertConfig({
      ...alertConfig.value,
      quiet_hours_start: quietHoursStart.value || alertConfig.value.quiet_hours_start,
      quiet_hours_end: quietHoursEnd.value || alertConfig.value.quiet_hours_end
    })
    ElMessage({
      message: '配置保存成功',
      type: 'success'
    })
  } catch (error) {
    ElMessage({
      message: '保存失败: ' + error.message,
      type: 'error'
    })
  } finally {
    saving.value = false
  }
}

// 重置配置
const resetConfig = () => {
  loadConfig()
}

// 加载检测配置
const loadDetectConfig = async () => {
  try {
    const config = await getDetectConfig()
    if (config) {
      detectConfig.value = { ...detectConfig.value, ...config }
    }
  } catch (error) {
    console.error('加载检测配置失败:', error)
  }
}

// 保存检测配置
const saveDetectConfig = async () => {
  detectSaving.value = true
  try {
    await updateDetectConfig(detectConfig.value)
    ElMessage({
      message: '检测配置保存成功',
      type: 'success'
    })
  } catch (error) {
    ElMessage({
      message: '保存失败: ' + error.message,
      type: 'error'
    })
  } finally {
    detectSaving.value = false
  }
}

// 重置检测配置
const resetDetectConfig = () => {
  loadDetectConfig()
}

// 确认告警
const acknowledgeAlert = async (alertId) => {
  try {
    await ackAlert(alertId)
    ElMessage({
      message: '告警已确认',
      type: 'success'
    })
  } catch (error) {
    ElMessage({
      message: '确认失败',
      type: 'error'
    })
  }
}

// 重发告警
const resendAlert = async (alertId) => {
  try {
    await resendAlertApi(alertId)
    ElMessage({
      message: '告警已重发',
      type: 'success'
    })
  } catch (error) {
    ElMessage({
      message: '重发失败',
      type: 'error'
    })
  }
}

// 社区组
const communitySearch = ref('')
const availableGroups = ref([])
const currentCommunity = ref(null)

async function loadUserCommunity() {
  try {
    const res = await getUserCommunity()
    currentCommunity.value = res.community
  } catch (e) { console.error(e) }
}

async function searchCommunities() {
  try {
    const res = await getAvailableGroups(communitySearch.value)
    availableGroups.value = Array.isArray(res.data) ? res.data : res
  } catch (e) { console.error(e) }
}

async function selectCommunity(group) {
  try {
    const res = await setUserCommunity(group.id)
    currentCommunity.value = res.community
    ElMessage.success('社区组已更新')
  } catch (e) {
    ElMessage.error('切换失败')
  }
}

async function unbindCommunity() {
  try {
    await setUserCommunity(null)
    currentCommunity.value = null
    ElMessage.success('已取消绑定')
  } catch (e) {
    ElMessage.error('取消绑定失败')
  }
}

onMounted(() => {
  loadConfig()
  loadDetectConfig()
  if (isUser.value) {
    loadUserCommunity()
    searchCommunities()
  }
})
</script>

<style scoped>
/* ============================================
   系统设置页面 - 温暖科技感设计
   ============================================ */

.system-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d12 100%);
  color: var(--neutral-700);
  position: relative;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 40% at 0% 0%, rgba(249, 115, 22, 0.08) 0%, transparent 50%),
              radial-gradient(ellipse 50% 30% at 100% 100%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* 页面头部 */
.page-header {
  position: relative;
  z-index: 1;
  padding: 32px 40px 24px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--neutral-800);
  margin: 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--neutral-400);
  margin: 0;
}

/* 标签页导航 */
.tabs-wrapper {
  position: relative;
  z-index: 1;
  padding: 0 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.tabs-nav {
  display: flex;
  position: relative;
  gap: 8px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  background: transparent;
  border: none;
  color: var(--neutral-400);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: color var(--transition-base);
}

.tab-btn:hover {
  color: var(--neutral-600);
}

.tab-btn.active {
  color: var(--primary-400);
}

.tab-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-icon svg {
  width: 100%;
  height: 100%;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 8px;
  right: 8px;
  height: 2px;
  background: linear-gradient(90deg, var(--primary-400), var(--primary-500));
  border-radius: 2px 2px 0 0;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.tab-btn.active .tab-indicator {
  opacity: 1;
}

/* 内容区域 */
.page-content {
  position: relative;
  z-index: 1;
  padding: 24px 40px 40px;
}

.content-section {
  animation: fadeIn 0.3s ease-out;
}

/* 设置卡片网格 */
.settings-grid {
  display: grid;
  gap: 24px;
}

.settings-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.settings-card .card-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.header-icon svg {
  width: 24px;
  height: 24px;
}

.header-icon.contact {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.header-icon.bell {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.header-icon.moon {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
}

.header-icon.warning {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.header-icon.info {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.header-text h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--neutral-800);
  margin: 0 0 4px 0;
}

.header-text p {
  font-size: 14px;
  color: var(--neutral-400);
  margin: 0;
}

.settings-card .card-body {
  padding: 24px;
}

/* 表单 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--neutral-500);
}

.form-input {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-700);
  font-size: 14px;
  transition: all var(--transition-base);
}

.form-input:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
}

.form-input::placeholder {
  color: var(--neutral-400);
}

.form-hint {
  font-size: 12px;
  color: var(--neutral-400);
  margin-top: 4px;
}

/* 告警等级 */
.alert-levels {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.alert-level {
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-lg);
  border-left: 3px solid;
}

.alert-level.high {
  border-left-color: var(--danger-400);
}

.alert-level.medium {
  border-left-color: var(--warning-400);
}

.alert-level.low {
  border-left-color: var(--info-400);
}

.level-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.level-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.alert-level.high .level-badge {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.alert-level.medium .level-badge {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.alert-level.low .level-badge {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.level-desc {
  font-size: 13px;
  color: var(--neutral-400);
}

.level-options {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

/* 复选框 */
.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-item input {
  display: none;
}

.checkbox-box {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-sm);
  position: relative;
  transition: all var(--transition-base);
}

.checkbox-item input:checked + .checkbox-box {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border-color: var(--primary-500);
}

.checkbox-item input:checked + .checkbox-box::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 6px;
  width: 5px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label {
  font-size: 14px;
  color: var(--neutral-600);
}

/* 免打扰 */
.quiet-hours {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.time-range {
  display: flex;
  align-items: flex-end;
  gap: 16px;
}

.time-input {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-separator {
  padding-bottom: 12px;
  color: var(--neutral-400);
  font-size: 14px;
}

.quiet-option {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* 开关 */
.toggle-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
}

.toggle-item input {
  display: none;
}

.toggle-switch {
  width: 48px;
  height: 26px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 13px;
  position: relative;
  flex-shrink: 0;
  transition: background var(--transition-base);
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-base);
}

.toggle-item input:checked + .toggle-switch {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
}

.toggle-item input:checked + .toggle-switch::after {
  transform: translateX(22px);
}

.toggle-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toggle-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--neutral-700);
}

.toggle-desc {
  font-size: 12px;
  color: var(--neutral-400);
}

/* 操作栏 */
.actions-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: var(--radius-lg);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border: none;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--neutral-600);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 表格卡片 */
.table-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.table-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-card .card-body {
  padding: 0;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-600);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh svg {
  width: 16px;
  height: 16px;
}

.btn-refresh svg.spinning {
  animation: spin 1s linear infinite;
}

/* 表格 */
.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 16px 24px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--neutral-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-table td {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.table-row {
  transition: background var(--transition-base);
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.cell-id {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--neutral-400);
}

.type-badge {
  display: inline-flex;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
  color: var(--neutral-600);
}

.risk-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.risk-badge.risk-high {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.risk-badge.risk-medium {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.risk-badge.risk-low {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.cell-method {
  font-size: 13px;
  color: var(--neutral-500);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.status-pending {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.status-badge.status-pending .status-dot {
  background: var(--warning-400);
}

.status-badge.status-sent {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.status-badge.status-sent .status-dot {
  background: var(--success-400);
}

.status-badge.status-failed {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.status-badge.status-failed .status-dot {
  background: var(--danger-400);
}

.status-badge.status-confirmed {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.status-badge.status-confirmed .status-dot {
  background: var(--info-400);
}

.cell-time {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--neutral-500);
}

.action-btns {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 14px;
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  border: none;
}

.action-btn.confirm {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.action-btn.confirm:hover {
  background: rgba(16, 185, 129, 0.25);
}

.action-btn.retry {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.action-btn.retry:hover {
  background: rgba(234, 179, 8, 0.25);
}

.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--neutral-400);
}

.empty-table svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.pagination-info {
  font-size: 14px;
  color: var(--neutral-400);
}

.pagination-info strong {
  color: var(--neutral-600);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-500);
  cursor: pointer;
  transition: all var(--transition-base);
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-btn svg {
  width: 18px;
  height: 18px;
}

.page-info {
  font-size: 14px;
  color: var(--neutral-500);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
}

.stat-icon svg {
  width: 28px;
  height: 28px;
}

.stat-icon.total {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.stat-icon.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.stat-icon.percent {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--neutral-800);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--neutral-400);
  margin-top: 4px;
}

/* 图表区域 */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.chart-card .card-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.chart-card .card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0;
}

.chart-card .card-body {
  padding: 24px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--neutral-400);
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
}

.chart-placeholder svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .page-header,
  .tabs-wrapper,
  .page-content {
    padding-left: 24px;
    padding-right: 24px;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-group.full-width {
    grid-column: span 1;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .level-options {
    flex-direction: column;
    gap: 12px;
  }

  .time-range {
    flex-direction: column;
    align-items: stretch;
  }
}

/* 社区组选择样式 */
.current-community {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 10px;
}

.current-community .community-name {
  font-size: 15px;
  font-weight: 600;
  color: #f0f0f5;
}

.current-community .community-org {
  font-size: 13px;
  color: #888;
}

.btn-unbind {
  margin-left: auto;
  padding: 4px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #f87171;
  font-size: 12px;
  cursor: pointer;
}

.no-community {
  color: #888;
  font-size: 14px;
}

.community-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.community-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.community-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.community-item.selected {
  border-color: rgba(249, 115, 22, 0.3);
  background: rgba(249, 115, 22, 0.05);
}

.community-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.community-info .community-name {
  font-size: 14px;
  font-weight: 500;
  color: #ddd;
}

.community-meta {
  font-size: 12px;
  color: #888;
}

.check-mark {
  color: #f97316;
  font-size: 16px;
  font-weight: 700;
}

.no-results {
  color: #666;
  font-size: 14px;
  padding: 16px;
  text-align: center;
}
</style>
