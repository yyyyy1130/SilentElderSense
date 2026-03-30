<template>
  <div class="video-detect">
    <!-- 上传 / 状态 合并区域 -->
    <el-card class="upload-card">
      <!-- 未选择文件：显示拖拽上传 -->
      <template v-if="!selectedFile && !isProcessing && !isCompleted">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="false"
          accept="video/*"
          :on-change="handleVideoSelect"
          drag
        >
          <el-icon class="upload-icon"><Upload /></el-icon>
          <div class="el-upload__text">
            将视频文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">支持 MP4、AVI、MOV、MKV 等常见格式</div>
          </template>
        </el-upload>
      </template>

      <!-- 已选择文件：显示文件信息和操作 -->
      <template v-else>
        <div class="selected-file-area">
          <!-- 文件信息行 -->
          <div class="file-info-row">
            <div class="file-info">
              <el-icon class="file-icon"><VideoCamera /></el-icon>
              <div class="file-detail">
                <span class="file-name">{{ selectedFile?.name }}</span>
                <span class="file-size">{{ formatSize(selectedFile?.size || 0) }}</span>
              </div>
            </div>

            <div class="file-actions">
              <!-- 持久化开关 -->
              <div class="persist-switch" v-if="!isProcessing && !isCompleted">
                <el-switch v-model="enablePersist" />
                <span class="switch-label">持久化</span>
              </div>

              <el-button
                v-if="!isProcessing && !isCompleted"
                type="primary"
                @click="startProcessing"
                :loading="isUploading"
              >
                开始检测
              </el-button>

              <el-button
                v-if="!isProcessing && !isCompleted"
                @click="reset"
              >
                重新选择
              </el-button>

              <el-button
                v-if="isProcessing"
                type="danger"
                @click="stopProcessing"
              >
                取消检测
              </el-button>

              <el-button
                v-if="isCompleted"
                type="info"
                @click="reset"
              >
                重新选择
              </el-button>
            </div>
          </div>

          <!-- 进度条 -->
          <div v-if="isProcessing || isCompleted" class="progress-section">
            <el-progress
              :percentage="progress"
              :stroke-width="16"
              :color="progressColor"
            />
            <div class="progress-text">
              {{ statusText }}
            </div>
          </div>
        </div>
      </template>
    </el-card>

    <!-- 帧展示区域 -->
    <el-card v-if="isProcessing || isCompleted" class="frame-card">
      <template #header>
        <div class="frame-header">
          <span>实时检测</span>
          <el-tag v-if="isProcessing" type="warning">处理中</el-tag>
          <el-tag v-else type="success">完成</el-tag>
        </div>
      </template>

      <div class="frame-wrapper">
        <!-- 占位 -->
        <div v-show="!currentFrameImage" class="placeholder">
          <el-icon class="placeholder-icon"><VideoCamera /></el-icon>
          <p>等待帧数据...</p>
        </div>

        <!-- 帧画布 -->
        <canvas
          ref="canvasRef"
          class="frame-canvas"
          v-show="currentFrameImage"
        ></canvas>

        <!-- 叠加信息 -->
        <div class="overlay-info">
          <div class="info-item">
            <span class="label">时间：</span>
            <span class="value">{{ formatTime(currentFrameTime) }}</span>
          </div>
          <div class="info-item">
            <span class="label">风险人数：</span>
            <span class="value">{{ riskyPersonCount }}</span>
          </div>
          <div class="info-item">
            <span class="label">已处理：</span>
            <span class="value">{{ processedCount }} 帧</span>
          </div>
        </div>
      </div>

      <!-- 当前帧检测结果 -->
      <div v-if="currentResult.persons?.length" class="detection-result">
        <h4>风险状态</h4>
        <div class="person-tags">
          <el-tag
            v-for="person in currentResult.persons"
            :key="person.person_id"
            :type="getRiskTagType(person.risk_level)"
          >
            {{ getRiskLabel(person.risk_level, person.risk_reason) }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { Upload, VideoCamera } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadVideo, createVideoProcessWebSocket } from '@/api/monitor'
import { getRiskTagType, getRiskLabel } from '@/utils/risk'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 状态
const uploadRef = ref(null)
const selectedFile = ref(null)
const canvasRef = ref(null)

const isUploading = ref(false)
const isProcessing = ref(false)
const isCompleted = ref(false)
const progress = ref(0)
const statusText = ref('')
const videoId = ref('')
const enablePersist = ref(false)  // 持久化开关

// 帧显示
const currentFrameImage = ref(null)
const currentFrameTime = ref(0)
const currentResult = ref({ persons: [] })
const processedCount = ref(0)

// 计算属性：避免模板中重复过滤
const riskyPersonCount = computed(() => {
  return (currentResult.value.persons || []).filter(p => p.risk_level !== 'NORMAL').length
})

let ws = null

// 工具函数
const progressColor = (percentage) => {
  if (percentage < 30) return '#909399'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatTime = (seconds) => {
  const s = Math.floor(seconds)
  const m = Math.floor(s / 60)
  return `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
}

// 选择视频
const handleVideoSelect = (file) => {
  if (!file || !file.raw) return
  selectedFile.value = file.raw
  resetState()
}

// 开始处理
const startProcessing = async () => {
  if (!selectedFile.value) return

  isUploading.value = true
  statusText.value = '正在上传视频...'

  try {
    const res = await uploadVideo(selectedFile.value)
    videoId.value = res.video_id
    isUploading.value = false
    isProcessing.value = true
    statusText.value = '上传完成，开始检测...'
    processedCount.value = 0
    currentFrameImage.value = null

    connectWebSocket()
  } catch (error) {
    isUploading.value = false
    ElMessage.error('上传失败: ' + (error.message || '未知错误'))
  }
}

// WebSocket
const connectWebSocket = () => {
  // 持久化模式需要用户登录
  if (enablePersist.value) {
    if (!authStore.isAuthenticated) {
      ElMessage.error('持久化模式需要登录，请先登录')
      resetState()
      return
    }
    const userId = authStore.user?.id
    ws = new WebSocket(`ws://localhost:8000/ws/video/${videoId.value}?persist=true&user_id=${userId}`)
  } else {
    ws = new WebSocket(`ws://localhost:8000/ws/video/${videoId.value}`)
  }

  ws.onopen = () => console.log('[WS] 连接已建立')

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleMessage(data)
    } catch (e) {
      console.error('[WS] 解析失败:', e)
    }
  }

  ws.onerror = () => {
    ElMessage.error('WebSocket 连接错误')
    stopProcessing()
  }

  ws.onclose = () => console.log('[WS] 关闭')
}

// 处理消息
const handleMessage = (data) => {
  switch (data.type) {
    case 'info':
      statusText.value = `视频: ${data.total_frames} 帧, ${data.fps?.toFixed(1)} FPS`
      break

    case 'progress':
      progress.value = data.progress
      statusText.value = `处理中... 已完成 ${data.processed} 帧`
      break

    case 'frame':
      processedCount.value++
      renderFrame(data)
      break

    case 'complete':
      progress.value = 100
      statusText.value = `完成! 共处理 ${data.processed_frames} 帧`
      ElMessage.success('视频检测完成')
      isProcessing.value = false
      isCompleted.value = true
      break

    case 'error':
      ElMessage.error('错误: ' + data.message)
      stopProcessing()
      break
  }
}

// 渲染帧
const renderFrame = (data) => {
  currentFrameTime.value = data.frame_id
  currentResult.value = { persons: data.persons || [] }

  if (!data.image || !canvasRef.value) return

  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')

  // 解码 hex 为 bytes
  const hex = data.image
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16)
  }

  // 创建图像并直接显示（检测框已在后端绘制）
  const blob = new Blob([bytes], { type: 'image/jpeg' })
  const img = new Image()
  img.onload = () => {
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)
    currentFrameImage.value = true
    URL.revokeObjectURL(img.src)
  }
  img.onerror = (e) => {
    console.error('[渲染] 图片加载失败:', e)
  }
  img.src = URL.createObjectURL(blob)
}

// 停止
const stopProcessing = () => {
  if (ws) {
    ws.close()
    ws = null
  }
  isProcessing.value = false
}

// 重置状态
const resetState = () => {
  progress.value = 0
  statusText.value = ''
  currentFrameImage.value = null
  currentFrameTime.value = 0
  currentResult.value = { persons: [] }
  processedCount.value = 0
  isCompleted.value = false
}

// 重新选择
const reset = () => {
  selectedFile.value = null
  resetState()
}

onUnmounted(() => {
  stopProcessing()
})
</script>

<style scoped>
.video-detect {
  max-width: 1000px;
  margin: 0 auto;
}

/* ========== 暗色卡片通用样式 ========== */
.upload-card,
.status-card,
.frame-card {
  margin-bottom: 20px;
}

:deep(.el-card) {
  background: rgba(26, 26, 36, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl, 16px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
  color: rgba(255, 255, 255, 0.85);
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
}

:deep(.el-card__body) {
  color: rgba(255, 255, 255, 0.85);
}

/* ========== 上传区域暗色适配 ========== */
.upload-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 16px;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  padding: 40px;
  background: rgba(255, 255, 255, 0.03);
  border: 2px dashed rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-lg, 12px);
  transition: all 0.3s ease;
}

:deep(.el-upload-dragger:hover) {
  border-color: var(--primary-500, #f97316);
  background: rgba(249, 115, 22, 0.05);
}

:deep(.el-upload-dragger .el-icon) {
  color: rgba(255, 255, 255, 0.3);
}

:deep(.el-upload__text) {
  color: rgba(255, 255, 255, 0.5);
}

:deep(.el-upload__text em) {
  color: var(--primary-400, #fb923c);
}

:deep(.el-upload__tip) {
  color: rgba(255, 255, 255, 0.35);
}

/* ========== 已选文件区域 ========== */
.selected-file-area {
  padding: 8px 0;
}

.file-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.85);
  min-width: 0;
}

.file-icon {
  font-size: 28px;
  color: var(--primary-400, #fb923c);
  flex-shrink: 0;
}

.file-detail {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.file-name {
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  margin-top: 2px;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.persist-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.persist-switch .switch-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.progress-section {
  margin-top: 16px;
}

.progress-text {
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

/* ========== 帧展示 ========== */
.frame-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: rgba(255, 255, 255, 0.85);
}

.frame-wrapper {
  position: relative;
  width: 100%;
  background: rgba(10, 10, 15, 0.6);
  border-radius: 8px;
  overflow: hidden;
  min-height: 360px;
}

.placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 360px;
  color: rgba(255, 255, 255, 0.3);
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.frame-canvas {
  width: 100%;
  display: block;
}

.overlay-info {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.65);
  padding: 10px 14px;
  border-radius: 6px;
  color: #fff;
}

.overlay-info .info-item {
  font-size: 14px;
  margin-bottom: 4px;
}

.overlay-info .info-item:last-child {
  margin-bottom: 0;
}

/* ========== 检测结果 ========== */
.detection-result {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.detection-result h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.person-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>