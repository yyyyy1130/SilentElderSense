<template>
  <div class="admin-platform">
    <!-- 标签页 -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: activeTab === 'orgs' }" @click="activeTab = 'orgs'">平台组织</button>
      <button class="tab-btn" :class="{ active: activeTab === 'groups' }" @click="activeTab = 'groups'">社区组</button>
      <button class="tab-btn" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">平台用户</button>
    </div>

    <!-- 平台组织 -->
    <section v-if="activeTab === 'orgs'">
      <div class="section-header">
        <h3>平台组织管理</h3>
        <button class="btn-primary" @click="showCreateOrg = true">创建组织</button>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>联系人</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="org in orgs" :key="org.id">
              <td>{{ org.id }}</td>
              <td>{{ org.name }}</td>
              <td>{{ org.contact_name || '-' }}</td>
              <td>
                <span class="status-badge" :class="org.status === 'active' ? 'active' : 'suspended'">
                  <span class="status-dot"></span>
                  {{ org.status === 'active' ? '运营中' : '已挂起' }}
                </span>
              </td>
              <td>{{ formatDate(org.created_at) }}</td>
              <td>
                <div class="action-btns">
                  <button class="action-btn secondary" @click="editOrg(org)">编辑</button>
                  <button class="action-btn danger" @click="handleSuspendOrg(org)">
                    {{ org.status === 'active' ? '挂起' : '恢复' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="orgs.length === 0" class="empty-state">暂无平台组织</div>
      </div>
    </section>

    <!-- 社区组 -->
    <section v-if="activeTab === 'groups'">
      <div class="section-header">
        <h3>社区组管理</h3>
        <div class="filter-group">
          <select v-model="selectedOrgId" @change="loadGroups" class="filter-select">
            <option value="">选择平台组织</option>
            <option v-for="org in orgs" :key="org.id" :value="org.id">{{ org.name }}</option>
          </select>
          <button class="btn-primary" :disabled="!selectedOrgId" @click="showCreateGroup = true">创建社区组</button>
        </div>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>地址</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in groups" :key="g.id">
              <td>{{ g.id }}</td>
              <td>{{ g.name }}</td>
              <td>{{ g.address || '-' }}</td>
              <td>
                <span class="status-badge" :class="g.status === 'active' ? 'active' : 'suspended'">
                  <span class="status-dot"></span>
                  {{ g.status === 'active' ? '运营中' : '已挂起' }}
                </span>
              </td>
              <td>
                <div class="action-btns">
                  <button class="action-btn secondary" @click="editGroup(g)">编辑</button>
                  <button class="action-btn danger" @click="handleSuspendGroup(g)">
                    {{ g.status === 'active' ? '挂起' : '恢复' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="groups.length === 0 && selectedOrgId" class="empty-state">该组织下暂无社区组</div>
        <div v-if="!selectedOrgId" class="empty-state">请先选择平台组织</div>
      </div>
    </section>

    <!-- 平台用户 -->
    <section v-if="activeTab === 'users'">
      <div class="section-header">
        <h3>创建平台用户</h3>
      </div>
      <div class="form-card">
        <div class="form-grid">
          <div class="form-item">
            <label>用户名</label>
            <input v-model="newUser.username" placeholder="输入用户名" class="form-input" />
          </div>
          <div class="form-item">
            <label>密码</label>
            <input v-model="newUser.password" type="password" placeholder="输入密码" class="form-input" />
          </div>
          <div class="form-item">
            <label>邮箱</label>
            <input v-model="newUser.email" placeholder="输入邮箱（可选）" class="form-input" />
          </div>
          <div class="form-item">
            <label>所属组织</label>
            <select v-model="newUser.platform_org_id" class="filter-select">
              <option value="">选择组织</option>
              <option v-for="org in orgs" :key="org.id" :value="org.id">{{ org.name }}</option>
            </select>
          </div>
        </div>
        <button class="btn-primary" @click="createPlatformUser" :disabled="!newUser.username || !newUser.password || !newUser.platform_org_id">
          创建平台用户
        </button>
      </div>
    </section>

    <!-- 创建组织弹窗 -->
    <div v-if="showCreateOrg" class="modal-overlay" @click.self="showCreateOrg = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingOrg ? '编辑组织' : '创建平台组织' }}</h3>
          <button class="modal-close" @click="showCreateOrg = false; editingOrg = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>组织名称</label>
            <input v-model="orgForm.name" placeholder="输入组织名称" class="form-input" />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="orgForm.description" placeholder="输入描述" class="form-input" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>联系人</label>
            <input v-model="orgForm.contact_name" placeholder="输入联系人" class="form-input" />
          </div>
          <div class="form-item">
            <label>联系电话</label>
            <input v-model="orgForm.contact_phone" placeholder="输入联系电话" class="form-input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreateOrg = false; editingOrg = null">取消</button>
          <button class="btn-primary" @click="saveOrg">保存</button>
        </div>
      </div>
    </div>

    <!-- 创建社区组弹窗 -->
    <div v-if="showCreateGroup" class="modal-overlay" @click.self="showCreateGroup = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingGroup ? '编辑社区组' : '创建社区组' }}</h3>
          <button class="modal-close" @click="showCreateGroup = false; editingGroup = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>社区组名称</label>
            <input v-model="groupForm.name" placeholder="输入社区组名称" class="form-input" />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="groupForm.description" placeholder="输入描述" class="form-input" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>地址</label>
            <input v-model="groupForm.address" placeholder="输入地址" class="form-input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreateGroup = false; editingGroup = null">取消</button>
          <button class="btn-primary" @click="saveGroup">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  listOrgs, createOrg, updateOrg, suspendOrg,
  listGroups, createGroup, updateGroup, suspendGroup,
} from '@/api/platform'
import { createPlatformUser as createPlatformUserApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

const activeTab = ref('orgs')

// 组织
const orgs = ref([])
const showCreateOrg = ref(false)
const editingOrg = ref(null)
const orgForm = ref({ name: '', description: '', contact_name: '', contact_phone: '' })

// 社区组
const groups = ref([])
const selectedOrgId = ref('')
const showCreateGroup = ref(false)
const editingGroup = ref(null)
const groupForm = ref({ name: '', description: '', address: '' })

// 用户
const newUser = ref({ username: '', password: '', email: '', platform_org_id: '' })

async function loadOrgs() {
  try {
    const res = await listOrgs()
    orgs.value = Array.isArray(res.data) ? res.data : res
  } catch (e) { console.error(e) }
}

async function saveOrg() {
  try {
    if (editingOrg.value) {
      await updateOrg(editingOrg.value.id, orgForm.value)
      ElMessage.success('更新成功')
    } else {
      await createOrg(orgForm.value)
      ElMessage.success('创建成功')
    }
    showCreateOrg.value = false
    editingOrg.value = null
    orgForm.value = { name: '', description: '', contact_name: '', contact_phone: '' }
    loadOrgs()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

function editOrg(org) {
  editingOrg.value = org
  orgForm.value = { name: org.name, description: org.description || '', contact_name: org.contact_name || '', contact_phone: org.contact_phone || '' }
  showCreateOrg.value = true
}

async function handleSuspendOrg(org) {
  try {
    if (org.status === 'active') {
      await suspendOrg(org.id)
      ElMessage.success('已挂起')
    } else {
      await updateOrg(org.id, { status: 'active' })
      ElMessage.success('已恢复')
    }
    loadOrgs()
  } catch (e) { ElMessage.error('操作失败') }
}

async function loadGroups() {
  if (!selectedOrgId.value) { groups.value = []; return }
  try {
    const res = await listGroups(selectedOrgId.value)
    groups.value = Array.isArray(res.data) ? res.data : res
  } catch (e) { console.error(e) }
}

async function saveGroup() {
  try {
    if (editingGroup.value) {
      await updateGroup(editingGroup.value.id, groupForm.value)
      ElMessage.success('更新成功')
    } else {
      await createGroup(selectedOrgId.value, groupForm.value)
      ElMessage.success('创建成功')
    }
    showCreateGroup.value = false
    editingGroup.value = null
    groupForm.value = { name: '', description: '', address: '' }
    loadGroups()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

function editGroup(g) {
  editingGroup.value = g
  groupForm.value = { name: g.name, description: g.description || '', address: g.address || '' }
  showCreateGroup.value = true
}

async function handleSuspendGroup(g) {
  try {
    if (g.status === 'active') {
      await suspendGroup(g.id)
      ElMessage.success('已挂起')
    } else {
      await updateGroup(g.id, { status: 'active' })
      ElMessage.success('已恢复')
    }
    loadGroups()
  } catch (e) { ElMessage.error('操作失败') }
}

async function createPlatformUser() {
  try {
    await createPlatformUserApi(newUser.value)
    ElMessage.success('平台用户创建成功')
    newUser.value = { username: '', password: '', email: '', platform_org_id: '' }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '创建失败')
  }
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('zh-CN')
}

onMounted(() => { loadOrgs() })
</script>

<style scoped>
.admin-platform {
  max-width: 1200px;
  margin: 0 auto;
}

.tab-bar {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: rgba(26, 26, 36, 0.6);
  border-radius: 12px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #888;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
}

.tab-btn:hover:not(.active) {
  color: #ccc;
  background: rgba(255, 255, 255, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h3 {
  color: #f0f0f5;
  font-size: 16px;
  margin: 0;
}

.btn-primary {
  padding: 8px 20px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #ccc;
  font-size: 14px;
  cursor: pointer;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-select {
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ccc;
  font-size: 13px;
  outline: none;
}

.table-wrapper {
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 12px;
  color: #888;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #ddd;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
}

.status-badge.active { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.status-badge.suspended { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.action-btns { display: flex; gap: 6px; }

.action-btn {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  border: none;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #aaa;
}

.action-btn.danger {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.form-card {
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item label {
  font-size: 13px;
  color: #888;
}

.form-input {
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ddd;
  font-size: 14px;
  outline: none;
  resize: vertical;
}

.form-input:focus {
  border-color: rgba(249, 115, 22, 0.5);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: #1e1e2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  width: 480px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-header h3 {
  color: #f0f0f5;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: #888;
  font-size: 18px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
