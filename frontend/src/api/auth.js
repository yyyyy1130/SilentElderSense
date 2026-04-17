import request from './index'

// 登录
export function login(data) {
  return request({
    url: '/login',
    method: 'post',
    data
  })
}

// 注册
export function register(data) {
  return request({
    url: '/register',
    method: 'post',
    data
  })
}

// 创建平台用户（管理员）
export function createPlatformUser(data) {
  return request({
    url: '/users/platform',
    method: 'post',
    data
  })
}
