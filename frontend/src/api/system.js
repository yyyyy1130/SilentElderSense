import request from './index'

// 获取系统状态
export function getSystemStatus() {
  return request({
    url: '/system/status',
    method: 'get'
  })
}