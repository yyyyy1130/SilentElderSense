import api from './index'

// ── 管理员：平台组织 ──

export const createOrg = (data) => api.post('/platform/orgs', data)
export const listOrgs = () => api.get('/platform/orgs')
export const getOrg = (orgId) => api.get(`/platform/orgs/${orgId}`)
export const updateOrg = (orgId, data) => api.put(`/platform/orgs/${orgId}`, data)
export const suspendOrg = (orgId) => api.delete(`/platform/orgs/${orgId}`)

// ── 管理员：社区组 ──

export const createGroup = (orgId, data) => api.post(`/platform/orgs/${orgId}/groups`, data)
export const listGroups = (orgId) => api.get(`/platform/orgs/${orgId}/groups`)
export const updateGroup = (groupId, data) => api.put(`/platform/groups/${groupId}`, data)
export const suspendGroup = (groupId) => api.delete(`/platform/groups/${groupId}`)

// ── 平台用户 ──

export const getMyOrg = () => api.get('/platform/org')
export const getMyCommunities = () => api.get('/platform/communities')
export const getPlatformStats = (days = 7) => api.get('/platform/stats', { params: { days } })
export const getPlatformDailyTrend = (days = 7) => api.get('/platform/stats/daily', { params: { days } })

// ── 普通用户：社区组选择 ──

export const getAvailableGroups = (search = '') => api.get('/community/groups', { params: { search } })
export const getUserCommunity = () => api.get('/user/community')
export const setUserCommunity = (communityGroupId) => api.put('/user/community', { community_group_id: communityGroupId })
