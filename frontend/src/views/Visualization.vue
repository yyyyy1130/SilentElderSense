<template>
  <div class="dashboard">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-noise"></div>
    </div>

    <!-- 顶部导航 -->
    <header class="dashboard-header">
      <div class="header-left">
        <div class="logo-area" @click="goToDashboard" title="返回事件看板">
          <div class="logo-icon">
            <svg viewBox="0 0 40 40" fill="none">
              <circle cx="20" cy="20" r="18" stroke="url(#logoGrad)" stroke-width="2"/>
              <circle cx="20" cy="20" r="6" fill="url(#logoGrad)"/>
              <path d="M20 8C13.373 8 8 13.373 8 20" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round"/>
              <defs>
                <linearGradient id="logoGrad" x1="8" y1="8" x2="32" y2="32">
                  <stop stop-color="#fb923c"/>
                  <stop offset="1" stop-color="#f97316"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="logo-text">
            <h1 class="system-name">SilentElder<span class="accent">Sense</span></h1>
            <p class="system-desc">独居老人智能监护系统</p>
          </div>
        </div>
      </div>

      <div class="header-center">
        <div class="status-indicator">
          <span class="pulse-dot"></span>
          <span class="status-label">系统运行正常</span>
        </div>
      </div>

      <div class="header-right">
        <div class="datetime-display">
          <span class="time">{{ currentTime }}</span>
          <span class="date">{{ currentDate }}</span>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="dashboard-content">
      <!-- 左侧面板 -->
      <aside class="panel panel-left">
        <!-- 统计卡片组 -->
        <div class="stats-grid">
          <div class="stat-card" v-for="(stat, index) in statsData" :key="stat.label">
            <div class="stat-icon" :class="stat.type">
              <component :is="stat.icon" />
            </div>
            <div class="stat-info">
              <span class="stat-value" :class="{ 'animate-value': stat.animate }">
                {{ stat.value }}
              </span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
            <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'" v-if="stat.trend">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path :d="stat.trend > 0 ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'"/>
              </svg>
              <span>{{ Math.abs(stat.trend) }}%</span>
            </div>
          </div>
        </div>

        <!-- 事件类型分布 -->
        <div class="card chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
                  <path d="M22 12A10 10 0 0 0 12 2v10z"/>
                </svg>
              </span>
              事件类型分布
            </h3>
          </div>
          <div class="card-body">
            <div ref="typeChartRef" class="chart"></div>
          </div>
        </div>
      </aside>

      <!-- 中间主区域 -->
      <section class="panel panel-center">
        <!-- 实时监控 / 视频检测 -->
        <div class="card monitor-card">
          <div class="card-header">
            <button class="mode-toggle-btn" @click="switchMonitorMode">
              <span class="title-icon live" v-if="monitorMode === 'camera'">
                <span class="live-dot"></span>
              </span>
              <span class="title-icon" v-else>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="23 7 16 12 23 17 23 7"/>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                </svg>
              </span>
              <span class="mode-label">{{ monitorMode === 'camera' ? '实时监控' : '视频检测' }}</span>
              <svg class="mode-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8 3v14l-3-3"/>
                <path d="M16 21V7l3 3"/>
              </svg>
            </button>
            <div class="monitor-status">
              <span class="status-badge" :class="isAnyConnected ? 'online' : 'offline'">
                <span class="badge-dot"></span>
                {{ monitorStatusText }}
              </span>
            </div>
          </div>
          <div class="card-body monitor-body">
            <div class="camera-view">
              <!-- ========== 实时监控模式 ========== -->
              <template v-if="monitorMode === 'camera'">
                <div v-show="!isCameraConnected" class="camera-placeholder">
                  <div class="placeholder-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M23 7l-7 5 7 5V7z"/>
                      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                    </svg>
                  </div>
                  <p class="placeholder-title">摄像头实时画面</p>
                  <p class="placeholder-subtitle">隐私保护模式已启用</p>
                  <div class="privacy-badge">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    <span>隐私加密</span>
                  </div>
                </div>
                <canvas ref="cameraCanvasRef" class="camera-canvas" v-show="isCameraConnected"></canvas>
              </template>

              <!-- ========== 视频检测模式 ========== -->
              <template v-else>
                <div v-show="!isVideoProcessing && !isVideoCompleted" class="camera-placeholder">
                  <div class="placeholder-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <polygon points="23 7 16 12 23 17 23 7"/>
                      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                    </svg>
                  </div>
                  <p class="placeholder-title">{{ videoSelectedFile ? videoSelectedFile.name : '点击左上角上传视频' }}</p>
                  <p class="placeholder-subtitle" v-if="videoSelectedFile">已选择视频，点击左上角开始检测</p>
                  <p class="placeholder-subtitle" v-else>支持 MP4、AVI、MOV 等格式</p>
                </div>
                <canvas ref="cameraCanvasRef" class="camera-canvas" v-show="isVideoProcessing || isVideoCompleted"></canvas>
                <!-- 视频进度条 -->
                <div v-if="isVideoProcessing || isVideoCompleted" class="video-progress-overlay">
                  <div class="video-progress-bar">
                    <div class="video-progress-fill" :style="{ width: videoProgress + '%' }"></div>
                  </div>
                  <span class="video-progress-text">{{ videoStatusText }}</span>
                </div>
              </template>

              <!-- 左上角 overlay（两种模式共用） -->
              <div class="camera-overlay">
                <div class="overlay-info">
                  <div class="camera-name-row">
                    <!-- 实时监控模式：设备名 + 切换按钮 -->
                    <template v-if="monitorMode === 'camera'">
                      <span class="camera-name">{{ selectedCamera?.label || '未选择设备' }}</span>
                      <button class="camera-switch-btn" @click="toggleDevicePanel" title="切换设备">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <polyline points="1 4 1 10 7 10"/>
                          <polyline points="23 20 23 14 17 14"/>
                          <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
                        </svg>
                      </button>
                    </template>
                    <!-- 视频检测模式：上传/开始检测按钮 -->
                    <template v-else>
                      <button v-if="!isVideoProcessing && !isVideoCompleted && !videoSelectedFile" class="camera-switch-btn video-upload-btn" @click="triggerVideoUpload" title="上传视频">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                          <polyline points="17 8 12 3 7 8"/>
                          <line x1="12" y1="3" x2="12" y2="15"/>
                        </svg>
                      </button>
                      <span class="camera-name" v-if="!videoSelectedFile">上传视频</span>
                      <button v-if="videoSelectedFile && !isVideoProcessing && !isVideoCompleted" class="camera-switch-btn" @click="startVideoProcessing" title="开始检测">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polygon points="5 3 19 12 5 21 5 3"/>
                        </svg>
                      </button>
                      <span class="camera-name" v-if="videoSelectedFile && !isVideoProcessing && !isVideoCompleted">{{ videoSelectedFile.name }}</span>
                      <button v-if="isVideoProcessing" class="camera-switch-btn" @click="stopVideoProcessing" title="停止检测">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <rect x="6" y="6" width="12" height="12"/>
                        </svg>
                      </button>
                      <span class="camera-name" v-if="isVideoProcessing">检测中...</span>
                      <button v-if="isVideoCompleted" class="camera-switch-btn" @click="resetVideoState" title="重新选择">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="1 4 1 10 7 10"/>
                          <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                        </svg>
                      </button>
                      <span class="camera-name" v-if="isVideoCompleted">已完成</span>
                    </template>
                  </div>
                  <span class="camera-time">{{ currentTime }}</span>
                </div>
                <div class="overlay-badges">
                  <span class="badge" :class="isAnyConnected ? 'badge-success' : 'badge-warning'">{{ overlayBadgeText }}</span>
                </div>
              </div>
              <!-- 设备选择面板 -->
              <transition name="fade">
                <div v-if="showDevicePanel" class="device-panel">
                  <div class="device-panel-header">
                    <span>选择摄像头设备</span>
                    <button class="device-panel-close" @click="showDevicePanel = false">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </div>
                  <div class="device-list">
                    <div v-if="cameraDevices.length === 0" class="device-empty">
                      <p>未检测到摄像头设备</p>
                      <button class="device-refresh-btn" @click="loadCameraDevices">刷新设备列表</button>
                    </div>
                    <button
                      v-for="(device, index) in cameraDevices"
                      :key="device.deviceId"
                      class="device-item"
                      :class="{ active: selectedCamera?.deviceId === device.deviceId }"
                      @click="selectCamera(device)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M23 7l-7 5 7 5V7z"/>
                        <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                      </svg>
                      <span>{{ device.label || `摄像头 ${index + 1}` }}</span>
                    </button>
                  </div>
                </div>
              </transition>
              <div class="scan-line"></div>
            </div>
          </div>
        </div>

        <!-- 最新事件 -->
        <div class="card events-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
              </span>
              最新事件
            </h3>
            <router-link to="/analysis" class="view-all">
              查看全部
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </router-link>
          </div>
          <div class="card-body events-body">
            <TransitionGroup name="event-list" tag="div" class="events-list">
              <div
                v-for="event in recentEvents"
                :key="event.id"
                class="event-item"
                :class="`risk-${event.riskLevel}`"
              >
                <div class="event-icon" :class="`icon-${event.type}`">
                  <svg v-if="event.type === 'fall'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <svg v-else-if="event.type === 'stillness'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                  </svg>
                </div>
                <div class="event-content">
                  <div class="event-header">
                    <span class="event-type">{{ event.typeName }}</span>
                    <span class="event-time">{{ formatTime(event.time) }}</span>
                  </div>
                  <div class="event-meta">
                    <span class="event-location">客厅区域</span>
                    <span class="event-duration" v-if="event.duration">持续 {{ event.duration }}</span>
                  </div>
                </div>
                <div class="event-risk">
                  <span class="risk-tag" :class="`tag-${event.riskLevel}`">
                    {{ getRiskLabel(event.riskLevel) }}
                  </span>
                </div>
              </div>
            </TransitionGroup>
            <div v-if="recentEvents.length === 0" class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12l2 2 4-4"/>
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <p>暂无事件记录</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 右侧面板 -->
      <aside class="panel panel-right">
        <!-- 24小时趋势 -->
        <div class="card chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </span>
              24小时风险趋势
            </h3>
          </div>
          <div class="card-body">
            <div ref="trendChartRef" class="chart"></div>
          </div>
        </div>

        <!-- 系统状态 - 扩展版 -->
        <div class="card status-card expanded">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                  <line x1="8" y1="21" x2="16" y2="21"/>
                  <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
              </span>
              系统状态
            </h3>
            <span class="update-time">{{ lastUpdateTime }}</span>
          </div>
          <div class="card-body">
            <!-- 资源使用情况 -->
            <div class="resources-section">
              <h4 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
                资源使用
              </h4>
              <div class="resource-grid">
                <!-- CPU -->
                <div class="resource-item">
                  <div class="resource-header">
                    <span class="resource-name">CPU</span>
                    <span class="resource-value" :class="getResourceClass(systemResources.cpuPercent)">
                      {{ systemResources.cpuPercent }}%
                    </span>
                  </div>
                  <div class="progress-bar">
                    <div
                      class="progress-fill cpu"
                      :style="{ width: `${systemResources.cpuPercent}%` }"
                    ></div>
                  </div>
                </div>
                <!-- 内存 -->
                <div class="resource-item">
                  <div class="resource-header">
                    <span class="resource-name">内存</span>
                    <span class="resource-value" :class="getResourceClass(systemResources.memoryPercent)">
                      {{ systemResources.memoryPercent }}%
                    </span>
                  </div>
                  <div class="progress-bar">
                    <div
                      class="progress-fill memory"
                      :style="{ width: `${systemResources.memoryPercent}%` }"
                    ></div>
                  </div>
                  <div class="resource-detail">
                    {{ systemResources.memoryUsedGb }} / {{ systemResources.memoryTotalGb }} GB
                  </div>
                </div>
              </div>
            </div>

            <!-- 服务状态 -->
            <div class="services-section">
              <h4 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1 1.51z"/>
                </svg>
                服务状态
              </h4>
              <div class="status-list">
                <div class="status-item" v-for="service in systemServices" :key="service.name">
                  <div class="status-info">
                    <span class="status-name">{{ service.name }}</span>
                    <span class="status-desc">{{ service.desc }}</span>
                  </div>
                  <div class="status-indicator" :class="service.status">
                    <span class="indicator-dot"></span>
                    <span class="indicator-text">{{ service.statusText }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getEvents, getEventStats, getHourlyTrend } from '@/api/events'
import { getSystemStatus } from '@/api/system'
import { getCameraDevices, createSession, closeSession, stopStream, uploadVideo } from '@/api/monitor'

const router = useRouter()

// 时间显示
const currentTime = ref('')
const currentDate = ref('')
const lastUpdateTime = ref('')

// 统计数据
const totalEvents = ref(0)
const highRiskEvents = ref(0)
const todayEvents = ref(0)
const confirmationRate = ref(null)
const trends = ref({ total: null, by_type: {}, by_risk: {} })

// 图表引用
const typeChartRef = ref(null)
const trendChartRef = ref(null)

let typeChart = null
let trendChart = null
let timeInterval = null
let statusRefreshInterval = null

// 事件数据
const recentEvents = ref([])
const hourlyTrendData = ref({ hours: [], by_type: {} })

// 事件统计
const eventStats = ref({
  by_type: {},
  by_risk: {},
  by_status: {}
})

// 系统资源数据
const systemResources = ref({
  cpuPercent: 0,
  memoryPercent: 0,
  memoryUsedGb: 0,
  memoryTotalGb: 0
})

// 系统服务状态
const systemServices = ref([])

// 模式切换
const monitorMode = ref('camera') // 'camera' | 'video'

// 摄像头设备
const cameraDevices = ref([])
const selectedCamera = ref(null)
const showDevicePanel = ref(false)
const isCameraConnected = ref(false)
const cameraCanvasRef = ref(null)

// 摄像头内部变量
let cameraWs = null
let cameraStream = null
let cameraVideoElement = null
let cameraSendCanvas = null
let cameraSendCtx = null
let cameraVideoId = ''
let canSendCameraFrame = true

// 视频检测状态
const videoSelectedFile = ref(null)
const isVideoProcessing = ref(false)
const isVideoCompleted = ref(false)
const videoProgress = ref(0)
const videoStatusText = ref('')
let videoWs = null
let videoUploadId = ''

// 计算属性
const isAnyConnected = computed(() => {
  if (monitorMode.value === 'camera') return isCameraConnected.value
  return isVideoProcessing.value
})

const monitorStatusText = computed(() => {
  if (monitorMode.value === 'camera') {
    if (isCameraConnected.value) return '检测中'
    return selectedCamera.value ? '就绪' : '未选择'
  } else {
    if (isVideoProcessing.value) return '检测中'
    if (isVideoCompleted.value) return '已完成'
    return videoSelectedFile.value ? '待检测' : '未选择'
  }
})

const overlayBadgeText = computed(() => {
  if (monitorMode.value === 'camera') {
    if (isCameraConnected.value) return '检测中'
    return selectedCamera.value ? '就绪' : '未连接'
  } else {
    if (isVideoProcessing.value) return '检测中'
    if (isVideoCompleted.value) return '已完成'
    return videoSelectedFile.value ? '待检测' : '未选择'
  }
})

// 统计卡片数据
const statsData = computed(() => [
  {
    label: '总事件数',
    value: totalEvents.value,
    type: 'primary',
    trend: trends.value.total,
    animate: true,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M22 12h-4l-3 9L9 3l-3 9H2' })
    ])
  },
  {
    label: '高风险',
    value: highRiskEvents.value,
    type: 'danger',
    trend: trends.value.by_risk?.HIGH,
    animate: true,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
      h('line', { x1: '12', y1: '9', x2: '12', y2: '13' }),
      h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' })
    ])
  },
  {
    label: '今日事件',
    value: todayEvents.value,
    type: 'info',
    animate: true,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('rect', { x: '3', y: '4', width: '18', height: '18', rx: '2', ry: '2' }),
      h('line', { x1: '16', y1: '2', x2: '16', y2: '6' }),
      h('line', { x1: '8', y1: '2', x2: '8', y2: '6' }),
      h('line', { x1: '3', y1: '10', x2: '21', y2: '10' })
    ])
  },
  {
    label: '确认率',
    value: confirmationRate.value !== null ? `${confirmationRate.value}%` : '-',
    type: 'success',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14' }),
      h('polyline', { points: '22 4 12 14.01 9 11.01' })
    ])
  }
])

// 工具函数
const getRiskLabel = (level) => {
  const map = { HIGH: '高风险', high: '高风险', MEDIUM: '中风险', medium: '中风险', LOW: '低风险', low: '低风险' }
  return map[level] || level
}

const getTypeLabel = (type) => {
  const map = {
    FALLEN: '跌倒检测',
    STILLNESS: '长时间静止',
    NIGHT_ABNORMAL: '夜间异常活动'
  }
  return map[type] || type
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const goToDashboard = () => {
  router.push('/dashboard')
}

// 资源使用等级判断
const getResourceClass = (percent) => {
  if (percent >= 80) return 'danger'
  if (percent >= 60) return 'warning'
  return 'normal'
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN')
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'long'
  })
}

// 模式切换
const switchMonitorMode = async () => {
  // 断开当前会话
  if (monitorMode.value === 'camera') {
    await stopCameraDetection()
    monitorMode.value = 'video'
  } else {
    stopVideoProcessing()
    resetVideoState()
    monitorMode.value = 'camera'
  }
}

// 视频上传文件选择
const triggerVideoUpload = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'video/*'
  input.onchange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      videoSelectedFile.value = file
      videoProgress.value = 0
      videoStatusText.value = ''
      isVideoCompleted.value = false
    }
  }
  input.click()
}

// 视频检测逻辑
const startVideoProcessing = async () => {
  if (!videoSelectedFile.value) return
  videoStatusText.value = '正在上传视频...'
  isVideoProcessing.value = true
  videoProgress.value = 0

  try {
    const res = await uploadVideo(videoSelectedFile.value)
    videoUploadId = res.video_id
    videoStatusText.value = '上传完成，开始检测...'
    connectVideoWs()
  } catch (error) {
    isVideoProcessing.value = false
    videoStatusText.value = '上传失败'
    console.error('上传失败:', error)
  }
}

const connectVideoWs = () => {
  videoWs = new WebSocket(`ws://localhost:8000/ws/video/${videoUploadId}`)

  videoWs.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      switch (data.type) {
        case 'progress':
          videoProgress.value = data.progress
          videoStatusText.value = `处理中... ${data.processed} 帧`
          break
        case 'frame':
          renderCameraFrame(data)
          break
        case 'complete':
          videoProgress.value = 100
          videoStatusText.value = `完成! 共处理 ${data.processed_frames} 帧`
          isVideoProcessing.value = false
          isVideoCompleted.value = true
          break
        case 'error':
          videoStatusText.value = '检测错误'
          isVideoProcessing.value = false
          break
      }
    } catch (e) {
      console.error('[视频检测] 解析失败:', e)
    }
  }

  videoWs.onerror = () => {
    isVideoProcessing.value = false
    videoStatusText.value = '连接错误'
  }
}

const stopVideoProcessing = () => {
  if (videoWs) {
    videoWs.close()
    videoWs = null
  }
  isVideoProcessing.value = false
}

const resetVideoState = () => {
  stopVideoProcessing()
  videoSelectedFile.value = null
  videoProgress.value = 0
  videoStatusText.value = ''
  isVideoCompleted.value = false
  videoUploadId = ''
}

// 摄像头设备管理
const loadCameraDevices = async () => {
  try {
    const devices = await getCameraDevices()
    cameraDevices.value = devices.map((d, i) => ({
      deviceId: d.deviceId,
      label: d.label || `摄像头 ${i + 1}`
    }))
  } catch (error) {
    console.error('获取摄像头设备失败:', error)
  }
}

const selectCamera = async (device) => {
  // 如果正在检测，先停止
  if (isCameraConnected.value) {
    await stopCameraDetection()
  }
  selectedCamera.value = device
  showDevicePanel.value = false
  // 自动启动新设备
  startCameraDetection()
}

const toggleDevicePanel = () => {
  showDevicePanel.value = !showDevicePanel.value
  if (showDevicePanel.value) {
    loadCameraDevices()
  }
}

// ========== 摄像头实时检测（复用 Monitor 逻辑） ==========
const startCameraDetection = async () => {
  if (!selectedCamera.value) return

  try {
    // 获取摄像头流
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        deviceId: { exact: selectedCamera.value.deviceId },
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    })
    cameraStream = stream

    // 创建隐藏的 video 元素
    cameraVideoElement = document.createElement('video')
    cameraVideoElement.srcObject = stream
    cameraVideoElement.muted = true
    cameraVideoElement.playsInline = true
    await cameraVideoElement.play()

    // 创建检测会话
    const response = await createSession()
    cameraVideoId = response.video_id

    // 连接 WebSocket
    cameraWs = new WebSocket(`ws://localhost:8000/ws/detect/${cameraVideoId}`)

    cameraWs.onopen = () => {
      isCameraConnected.value = true
      canSendCameraFrame = true
      startCameraFrameSending()
    }

    cameraWs.onmessage = (event) => {
      canSendCameraFrame = true
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'frame') {
          renderCameraFrame(data)
        }
      } catch (e) {
        console.error('[大屏监控] 解析失败:', e)
      }
    }

    cameraWs.onerror = () => {
      console.error('[大屏监控] WebSocket 错误')
      stopCameraDetection()
    }

    cameraWs.onclose = () => {
      isCameraConnected.value = false
    }
  } catch (error) {
    console.error('[大屏监控] 启动摄像头失败:', error)
  }
}

const startCameraFrameSending = () => {
  cameraSendCanvas = document.createElement('canvas')
  cameraSendCanvas.width = 640
  cameraSendCanvas.height = 480
  cameraSendCtx = cameraSendCanvas.getContext('2d')

  const sendFrame = () => {
    if (!isCameraConnected.value || !cameraVideoElement) return

    if (!canSendCameraFrame) {
      requestAnimationFrame(sendFrame)
      return
    }

    cameraSendCtx.drawImage(cameraVideoElement, 0, 0, 640, 480)
    cameraSendCanvas.toBlob((blob) => {
      if (blob && cameraWs && cameraWs.readyState === WebSocket.OPEN) {
        canSendCameraFrame = false
        blob.arrayBuffer().then(buffer => {
          cameraWs.send(buffer)
        })
      }
    }, 'image/jpeg', 0.7)

    requestAnimationFrame(sendFrame)
  }

  requestAnimationFrame(sendFrame)
}

const renderCameraFrame = (data) => {
  if (!data.image || !cameraCanvasRef.value) return

  const canvas = cameraCanvasRef.value
  const ctx = canvas.getContext('2d')

  const hex = data.image
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16)
  }

  const blob = new Blob([bytes], { type: 'image/jpeg' })
  const img = new Image()
  img.onload = () => {
    // 使用容器尺寸，不用图片原始尺寸，避免撑大布局
    const rect = canvas.parentElement.getBoundingClientRect()
    canvas.width = rect.width
    canvas.height = rect.height
    // 按比例居中绘制
    const scale = Math.min(rect.width / img.width, rect.height / img.height)
    const w = img.width * scale
    const h = img.height * scale
    const x = (rect.width - w) / 2
    const y = (rect.height - h) / 2
    ctx.clearRect(0, 0, rect.width, rect.height)
    ctx.drawImage(img, x, y, w, h)
    URL.revokeObjectURL(img.src)
  }
  img.src = URL.createObjectURL(blob)
}

const stopCameraDetection = async () => {
  if (cameraStream) {
    stopStream(cameraStream)
    cameraStream = null
  }
  if (cameraVideoElement) {
    cameraVideoElement.srcObject = null
    cameraVideoElement = null
  }
  cameraSendCanvas = null
  cameraSendCtx = null

  if (cameraWs) {
    cameraWs.close()
    cameraWs = null
  }
  if (cameraVideoId) {
    try {
      await closeSession(cameraVideoId)
    } catch (e) {
      console.error('[大屏监控] 关闭会话失败:', e)
    }
    cameraVideoId = ''
  }
  isCameraConnected.value = false
}

// 加载事件数据
const loadEventData = async () => {
  try {
    const [eventsRes, statsRes, hourlyRes] = await Promise.all([
      getEvents({ per_page: 5 }),
      getEventStats({ days: 7 }),
      getHourlyTrend()
    ])

    recentEvents.value = (eventsRes.events || []).map(e => ({
      id: e.id,
      type: (e.event_type || '').toLowerCase(),
      typeName: getTypeLabel(e.event_type),
      time: e.start_time || e.created_at,
      riskLevel: (e.risk_level || '').toLowerCase(),
      duration: e.duration ? `${Math.floor(e.duration / 60)}分` : null
    }))

    eventStats.value = statsRes
    totalEvents.value = statsRes.total || 0
    highRiskEvents.value = statsRes.by_risk?.HIGH || 0
    todayEvents.value = statsRes.by_status?.pending || 0
    confirmationRate.value = statsRes.confirmation_rate
    trends.value = statsRes.trends || { total: null, by_type: {}, by_risk: {} }

    hourlyTrendData.value = hourlyRes
    updateCharts()
  } catch (error) {
    console.error('加载事件数据失败:', error)
  }
}

// 加载系统状态
const loadSystemStatus = async () => {
  try {
    const statusRes = await getSystemStatus()

    // 更新资源数据
    if (statusRes.resources) {
      systemResources.value = {
        cpuPercent: Math.round(statusRes.resources.cpu_percent || 0),
        memoryPercent: Math.round(statusRes.resources.memory_percent || 0),
        memoryUsedGb: statusRes.resources.memory_used_gb || 0,
        memoryTotalGb: statusRes.resources.memory_total_gb || 0
      }
    }

    // 更新服务状态
    if (statusRes.services) {
      systemServices.value = statusRes.services.map(s => ({
        name: s.name,
        desc: s.desc,
        status: s.status,
        statusText: s.statusText
      }))
    }

    lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    console.error('加载系统状态失败:', error)
  }
}

// 图表配置
const chartTheme = {
  backgroundColor: 'transparent',
  textStyle: { color: 'rgba(255,255,255,0.6)' }
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  typeChart = echarts.init(typeChartRef.value)
  updateTypeChart()
}

const updateTypeChart = () => {
  if (!typeChart) return
  const stats = eventStats.value
  typeChart.setOption({
    ...chartTheme,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      left: 'center',
      itemWidth: 12,
      itemHeight: 12,
      itemGap: 16,
      textStyle: { color: 'rgba(255,255,255,0.6)', fontSize: 11 },
      data: ['跌倒', '静止', '夜间异常']
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: 'rgba(26,26,36,0.8)',
        borderWidth: 2
      },
      label: {
        show: true,
        position: 'inside',
        color: '#fff',
        fontSize: 12,
        fontWeight: 600,
        formatter: '{d}%'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(0,0,0,0.5)'
        }
      },
      data: [
        { value: stats.by_type?.FALLEN || 0, name: '跌倒', itemStyle: { color: '#f97316' } },
        { value: stats.by_type?.STILLNESS || 0, name: '静止', itemStyle: { color: '#eab308' } },
        { value: stats.by_type?.NIGHT_ABNORMAL || 0, name: '夜间异常', itemStyle: { color: '#3b82f6' } }
      ]
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  updateTrendChart()
}

const updateTrendChart = () => {
  if (!trendChart) return
  const data = hourlyTrendData.value
  const hours = data.hours || Array.from({ length: 24 }, (_, i) => `${i}:00`)

  trendChart.setOption({
    ...chartTheme,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' }
    },
    legend: {
      data: ['跌倒检测', '长时间静止', '夜间异常活动'],
      textStyle: { color: 'rgba(255,255,255,0.6)' },
      top: 0,
      right: 0
    },
    grid: {
      top: 40,
      left: 40,
      right: 20,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: hours,
      boundaryGap: false,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 10, interval: 3 }
    },
    yAxis: {
      type: 'value',
      name: '事件数',
      nameTextStyle: { color: 'rgba(255,255,255,0.4)', fontSize: 10 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 10 }
    },
    series: [
      {
        name: '跌倒检测',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: data.by_type?.FALLEN || [],
        lineStyle: { width: 2, color: '#f97316' },
        itemStyle: { color: '#f97316' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(249, 115, 22, 0.3)' },
            { offset: 1, color: 'rgba(249, 115, 22, 0)' }
          ])
        }
      },
      {
        name: '长时间静止',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: data.by_type?.STILLNESS || [],
        lineStyle: { width: 2, color: '#eab308' },
        itemStyle: { color: '#eab308' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(234, 179, 8, 0.3)' },
            { offset: 1, color: 'rgba(234, 179, 8, 0)' }
          ])
        }
      },
      {
        name: '夜间异常活动',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: data.by_type?.NIGHT_ABNORMAL || [],
        lineStyle: { width: 2, color: '#3b82f6' },
        itemStyle: { color: '#3b82f6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0)' }
          ])
        }
      }
    ]
  })
}

const updateCharts = () => {
  updateTypeChart()
  updateTrendChart()
}

const handleResize = () => {
  typeChart?.resize()
  trendChart?.resize()
}

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  // 加载初始数据
  await loadEventData()
  await loadSystemStatus()
  loadCameraDevices()

  nextTick(() => {
    initTypeChart()
    initTrendChart()
    window.addEventListener('resize', handleResize)
  })

  // 每5秒刷新系统状态
  statusRefreshInterval = setInterval(loadSystemStatus, 5000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  if (statusRefreshInterval) {
    clearInterval(statusRefreshInterval)
  }
  stopCameraDetection()
  stopVideoProcessing()
  window.removeEventListener('resize', handleResize)
  typeChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
/* ============================================
   可视化大屏 - 温暖科技感设计
   ============================================ */

.dashboard {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d12 100%);
  color: var(--neutral-700);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(249, 115, 22, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse 60% 40% at 100% 100%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}

.bg-noise {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

/* 顶部导航 */
.dashboard-header {
  height: 72px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: opacity var(--transition-base);
}

.logo-area:hover {
  opacity: 0.8;
}

.logo-icon {
  width: 40px;
  height: 40px;
  animation: pulse 3s ease-in-out infinite;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.system-name {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--neutral-800);
  line-height: 1.2;
}

.system-name .accent {
  font-weight: 300;
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.system-desc {
  font-size: 12px;
  color: var(--neutral-400);
  letter-spacing: 0.05em;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-full);
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--success-400);
  border-radius: 50%;
  animation: pulseDot 2s ease-in-out infinite;
}

@keyframes pulseDot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.status-label {
  font-size: 13px;
  color: var(--success-400);
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border: none;
  border-radius: var(--radius-lg);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
}

.datetime-display {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.datetime-display .time {
  font-family: var(--font-mono);
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.datetime-display .date {
  font-size: 12px;
  color: var(--neutral-400);
  margin-top: 4px;
}

/* 主内容区 */
.dashboard-content {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 20px;
  padding: 20px;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

/* 面板通用样式 */
.panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.stat-icon svg {
  width: 20px;
  height: 20px;
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.stat-icon.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.stat-icon.info {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--neutral-800);
  line-height: 1;
}

.stat-value.animate-value {
  animation: countUp 0.5s ease-out;
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-label {
  font-size: 12px;
  color: var(--neutral-400);
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend svg {
  width: 14px;
  height: 14px;
}

.stat-trend.up {
  color: var(--success-400);
}

.stat-trend.down {
  color: var(--danger-400);
}

/* 卡片通用样式 */
.card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0;
}

.title-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-400);
}

.title-icon svg {
  width: 18px;
  height: 18px;
}

.title-icon.live {
  background: var(--danger-500);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
}

.title-icon.success {
  color: var(--success-400);
}

.title-icon.warning {
  color: var(--warning-400);
}

.card-body {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 图表卡片 */
.chart-card {
  flex: 1;
  min-height: 200px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 180px;
}

/* 监控卡片 */
.monitor-card {
  flex: 1.2;
}

/* 模式切换按钮 */
.mode-toggle-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-md, 8px);
  transition: all 0.2s ease;
  color: var(--neutral-700, rgba(255,255,255,0.85));
  font-size: 14px;
  font-weight: 600;
}

.mode-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

.mode-label {
  font-size: 14px;
  font-weight: 600;
}

.mode-arrow {
  width: 16px;
  height: 16px;
  opacity: 0.4;
  transition: transform 0.2s;
}

.mode-toggle-btn:hover .mode-arrow {
  opacity: 0.7;
  transform: rotate(180deg);
}

/* 视频上传按钮 */
.video-upload-btn {
  background: rgba(249, 115, 22, 0.2) !important;
  border-color: rgba(249, 115, 22, 0.4) !important;
}

/* 视频进度条覆盖层 */
.video-progress-overlay {
  position: absolute;
  bottom: 12px;
  left: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 5;
}

.video-progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.video-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-500, #f97316), var(--primary-400, #fb923c));
  border-radius: 2px;
  transition: width 0.3s ease;
}

.video-progress-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
}

.monitor-body {
  padding: 0;
}

.camera-view {
  width: 100%;
  height: 100%;
  min-height: 300px;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0.2) 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.camera-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: block;
}

.camera-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--neutral-400);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  opacity: 0.5;
}

.placeholder-icon svg {
  width: 100%;
  height: 100%;
}

.placeholder-title {
  font-size: 16px;
  font-weight: 500;
}

.placeholder-subtitle {
  font-size: 13px;
  color: var(--neutral-400);
}

.privacy-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-full);
  color: var(--success-400);
  font-size: 12px;
  font-weight: 500;
}

.privacy-badge svg {
  width: 14px;
  height: 14px;
}

.camera-overlay {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.overlay-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
}

.camera-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.camera-name {
  font-size: 13px;
  font-weight: 500;
  color: white;
}

.camera-switch-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.camera-switch-btn svg {
  width: 14px;
  height: 14px;
}

.camera-switch-btn:hover {
  background: rgba(249, 115, 22, 0.3);
  border-color: var(--primary-400);
  color: var(--primary-400);
  transform: rotate(30deg);
}

.camera-time {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--neutral-400);
}

.overlay-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background: rgba(16, 185, 129, 0.2);
  color: var(--success-400);
}

.badge-warning {
  background: rgba(234, 179, 8, 0.2);
  color: var(--warning-400, #eab308);
}

/* 设备选择面板 */
.device-panel {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 320px;
  max-height: 280px;
  background: rgba(26, 26, 36, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-xl, 16px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  z-index: 20;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.device-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.device-panel-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s;
}

.device-panel-close svg {
  width: 16px;
  height: 16px;
}

.device-panel-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.device-list {
  padding: 8px;
  overflow-y: auto;
  flex: 1;
}

.device-empty {
  padding: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

.device-refresh-btn {
  margin-top: 12px;
  padding: 8px 20px;
  background: rgba(249, 115, 22, 0.15);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: var(--radius-md, 8px);
  color: var(--primary-400, #fb923c);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.device-refresh-btn:hover {
  background: rgba(249, 115, 22, 0.25);
}

.device-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md, 8px);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.device-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.device-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.device-item.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.3);
  color: var(--primary-400, #fb923c);
}

/* 面板过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.95);
}

.status-badge.offline .badge-dot {
  background: var(--warning-400, #eab308);
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-400), transparent);
  animation: scanLine 3s linear infinite;
}

@keyframes scanLine {
  0% {
    top: 0;
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    top: 100%;
    opacity: 0;
  }
}

/* 事件卡片 */
.events-card {
  flex: 0.8;
  max-height: 320px;
}

.view-all {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--primary-400);
  text-decoration: none;
  transition: color var(--transition-base);
}

.view-all svg {
  width: 14px;
  height: 14px;
  transition: transform var(--transition-base);
}

.view-all:hover {
  color: var(--primary-300);
}

.view-all:hover svg {
  transform: translateX(2px);
}

.events-body {
  overflow: hidden;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  max-height: 200px;
}

.events-list::-webkit-scrollbar {
  width: 4px;
}

.events-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  border-left: 3px solid;
  transition: all var(--transition-base);
}

.event-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.event-item.risk-high {
  border-left-color: var(--danger-400);
}

.event-item.risk-medium {
  border-left-color: var(--warning-400);
}

.event-item.risk-low {
  border-left-color: var(--info-400);
}

.event-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.event-icon svg {
  width: 20px;
  height: 20px;
}

.event-icon.icon-fall {
  color: var(--danger-400);
}

.event-icon.icon-stillness {
  color: var(--warning-400);
}

.event-icon.icon-night_activity {
  color: var(--info-400);
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.event-type {
  font-size: 14px;
  font-weight: 500;
  color: var(--neutral-700);
}

.event-time {
  font-size: 12px;
  color: var(--neutral-400);
  font-family: var(--font-mono);
}

.event-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--neutral-400);
}

.risk-tag {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
}

.risk-tag.tag-high {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.risk-tag.tag-medium {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning-400);
}

.risk-tag.tag-low {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--neutral-400);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state.small {
  padding: 20px;
}

.empty-state.small svg {
  width: 32px;
  height: 32px;
}

/* 状态卡片 - 扩展版 */
.status-card.expanded {
  flex: 1.5;
}

.status-card.expanded .card-body {
  padding: 20px;
  gap: 16px;
}

.update-time {
  font-size: 11px;
  color: var(--neutral-400);
  font-family: var(--font-mono);
}

/* 资源区域 */
.resources-section {
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--neutral-600);
  margin-bottom: 12px;
}

.section-title svg {
  width: 16px;
  height: 16px;
  color: var(--primary-400);
}

.resource-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.resource-item {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.resource-name {
  font-size: 13px;
  color: var(--neutral-500);
  font-weight: 500;
}

.resource-value {
  font-size: 18px;
  font-weight: 700;
  font-family: var(--font-mono);
}

.resource-value.normal {
  color: var(--success-400);
}

.resource-value.warning {
  color: var(--warning-400);
}

.resource-value.danger {
  color: var(--danger-400);
}

.progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease-out;
}

.progress-fill.cpu {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.progress-fill.memory {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

.resource-detail {
  font-size: 11px;
  color: var(--neutral-400);
  margin-top: 6px;
  font-family: var(--font-mono);
}

/* 服务区域 */
.services-section {
  flex: 1;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  transition: background var(--transition-base);
}

.status-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--neutral-700);
}

.status-desc {
  font-size: 11px;
  color: var(--neutral-400);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator.online {
  color: var(--success-400);
}

.status-indicator.offline {
  color: var(--danger-400);
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulseDot 2s ease-in-out infinite;
}

.status-indicator.online .indicator-dot {
  background: var(--success-400);
}

.status-indicator.offline .indicator-dot {
  background: var(--danger-400);
  animation: none;
}

.indicator-text {
  font-size: 12px;
  font-weight: 500;
}

/* 列表过渡动画 */
.event-list-enter-active,
.event-list-leave-active {
  transition: all var(--transition-slow);
}

.event-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.event-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .dashboard-content {
    grid-template-columns: 240px 1fr 240px;
    gap: 16px;
    padding: 16px;
  }
}

@media (max-width: 1200px) {
  .dashboard-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }

  .panel {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .stats-grid {
    width: 100%;
  }

  .chart-card {
    flex: 1;
    min-width: 300px;
  }

  .monitor-card {
    flex: 1;
    min-width: 100%;
    min-height: 400px;
  }

  .events-card {
    flex: 1;
    min-width: 300px;
  }
}
</style>
