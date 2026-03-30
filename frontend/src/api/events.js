import request from './index'

// 获取事件列表
export function getEvents(params) {
  return request({
    url: '/events',
    method: 'get',
    params
  })
}

// 创建事件（记录事件）
export function createEvent(data) {
  return request({
    url: '/events',
    method: 'post',
    data
  })
}

// 获取事件详情
export function getEventDetail(id) {
  return request({
    url: `/events/${id}`,
    method: 'get'
  })
}

// 更新事件状态
export function updateEvent(id, data) {
  return request({
    url: `/events/${id}`,
    method: 'put',
    data
  })
}

// 获取事件统计
export function getEventStats(params) {
  return request({
    url: '/events/stats',
    method: 'get',
    params
  })
}

// 获取小时级事件趋势
export function getHourlyTrend(params) {
  return request({
    url: '/events/hourly',
    method: 'get',
    params
  })
}

// 获取每日事件趋势
export function getDailyTrend(params) {
  return request({
    url: '/events/daily',
    method: 'get',
    params
  })
}

// 导出事件数据
export function exportEvents(params) {
  return request({
    url: '/events/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
