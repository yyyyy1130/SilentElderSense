import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getEvents, getEventDetail, updateEvent, getEventStats, createEvent } from '@/api/events'

export const useEventsStore = defineStore('events', () => {
  const events = ref([])
  const statistics = ref({
    total: 0,
    by_type: {},
    by_risk: {},
    by_status: {}
  })
  const loading = ref(false)
  const pagination = ref({
    total: 0,
    page: 1,
    per_page: 20
  })

  const fetchEvents = async (params = {}) => {
    loading.value = true
    try {
      const response = await getEvents(params)
      events.value = (response.events || []).map(formatEvent)
      pagination.value = {
        total: response.total || 0,
        page: response.page || 1,
        per_page: response.per_page || 20
      }
      return response
    } catch (error) {
      console.error('获取事件列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchEventDetail = async (id) => {
    try {
      const response = await getEventDetail(id)
      return formatEvent(response.event)
    } catch (error) {
      console.error('获取事件详情失败:', error)
      throw error
    }
  }

  const updateEventStatus = async (id, data) => {
    try {
      const response = await updateEvent(id, data)
      const index = events.value.findIndex(e => e.id === id)
      if (index !== -1) {
        events.value[index] = formatEvent(response.event)
      }
      return response
    } catch (error) {
      console.error('更新事件状态失败:', error)
      throw error
    }
  }

  const fetchStats = async (params = {}) => {
    try {
      const response = await getEventStats(params)
      statistics.value = response
      updateStatsFormatted()
      return response
    } catch (error) {
      console.error('获取事件统计失败:', error)
      throw error
    }
  }

  const addEvent = async (eventData) => {
    try {
      const response = await createEvent(eventData)
      events.value.unshift(formatEvent(response.event))
      return response
    } catch (error) {
      console.error('创建事件失败:', error)
      throw error
    }
  }

  const formatEvent = (event) => {
    return {
      id: event.id,
      type: event.event_type?.toLowerCase() || event.type,
      typeName: getTypeName(event.event_type || event.type),
      riskLevel: (event.risk_level || event.riskLevel)?.toUpperCase(),
      riskLevelName: getRiskName(event.risk_level || event.riskLevel),
      start_time: event.start_time || event.time,
      end_time: event.end_time,
      time: event.start_time || event.time,
      duration: event.duration || 0,
      status: event.status || 'pending',
      statusName: getStatusName(event.status),
      description: event.notes || event.description || '',
      notes: event.notes || '',
      location: event.video_id || '',
      confidence: event.confidence || 0.9,
      frame_count: event.frame_count || 0,
      user_id: event.user_id,
      video_id: event.video_id,
      person_id: event.person_id
    }
  }

  const getTypeName = (type) => {
    const map = {
      'FALL': '跌倒检测',
      'STILLNESS': '长时间静止',
      'NIGHT_ACTIVITY': '夜间异常活动',
      'STATIC': '长时间静止',
      'fall': '跌倒检测',
      'stillness': '长时间静止',
      'night_activity': '夜间异常活动',
      'static': '长时间静止'
    }
    return map[type] || type
  }

  const getRiskName = (level) => {
    const map = {
      'HIGH': '高风险',
      'MEDIUM': '中风险',
      'LOW': '低风险',
      'high': '高风险',
      'medium': '中风险',
      'low': '低风险'
    }
    return map[level] || level
  }

  const getStatusName = (status) => {
    const map = {
      'pending': '待处理',
      'confirmed': '已确认',
      'false_alarm': '误报',
      'handled': '已处理'
    }
    return map[status] || status
  }

  const statsFormatted = ref({
    total: 0,
    today: 0,
    fall: 0,
    stillness: 0,
    nightActivity: 0,
    handled: 0,
    pending: 0,
    accuracy: 94.5
  })

  // 低频阈值隐藏辅助函数
  const maskLowFreq = (value) => {
    const num = Number(value)
    if (isNaN(num)) return value
    return (num > 0 && num < 5) ? '<5' : num
  }

  const updateStatsFormatted = () => {
    const stats = statistics.value
    const d = stats.display || {}
    const rawConfirmed = stats.by_status?.confirmed || 0
    const rawFalseAlarm = stats.by_status?.false_alarm || 0
    const handledNum = rawConfirmed + rawFalseAlarm

    statsFormatted.value = {
      total: d.total ?? stats.total ?? 0,
      today: d.by_status?.pending ?? stats.by_status?.pending ?? 0,
      fall: d.by_type?.FALLEN ?? stats.by_type?.FALLEN ?? 0,
      stillness: d.by_type?.STILLNESS ?? stats.by_type?.STILLNESS ?? 0,
      nightActivity: d.by_type?.NIGHT_ABNORMAL ?? stats.by_type?.NIGHT_ABNORMAL ?? 0,
      handled: maskLowFreq(handledNum),
      pending: d.by_status?.pending ?? stats.by_status?.pending ?? 0,
      accuracy: 94.5
    }
  }

  return {
    events,
    statistics,
    statsFormatted,
    loading,
    pagination,
    fetchEvents,
    fetchEventDetail,
    updateEventStatus,
    fetchStats,
    addEvent,
    updateStatsFormatted,
    getTypeName,
    getRiskName,
    getStatusName
  }
})
