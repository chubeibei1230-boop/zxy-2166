<template>
  <div class="sign-list">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" @submit.prevent>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option v-for="(item, key) in STATUS_MAP" :key="key" :label="item.label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="批次">
          <el-input v-model="filterForm.batch_code" placeholder="批次编号" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="适用场次">
          <el-input v-model="filterForm.applicable_session" placeholder="场次" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="责任人">
          <el-input v-model="filterForm.responsible_person" placeholder="责任人" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="编号/区域" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchList">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>引导牌列表</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>新增引导牌
          </el-button>
        </div>
      </template>
      <el-table :data="signList" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="sign_number" label="引导牌编号" width="140" />
        <el-table-column prop="batch_code" label="批次编号" width="120" />
        <el-table-column prop="applicable_session" label="适用场次" width="140" />
        <el-table-column prop="current_area" label="摆放区域" width="140" />
        <el-table-column prop="responsible_person" label="责任人" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="360" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetailDialog(row)">详情</el-button>
            <el-button link type="primary" @click="openAdjustDialog(row)" :disabled="['deactivated'].includes(row.status)">
              位置调整
            </el-button>
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              v-if="row.status === 'pending_production'"
              link
              type="success"
              @click="handleMarkAvailable(row)"
            >
              标记可发放
            </el-button>
            <el-popconfirm title="确定删除此引导牌？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" title="新增引导牌" width="500px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="引导牌编号" prop="sign_number">
          <el-input v-model="createForm.sign_number" placeholder="请输入编号" />
        </el-form-item>
        <el-form-item label="批次编号" prop="batch_code">
          <el-input v-model="createForm.batch_code" placeholder="请输入批次编号" />
        </el-form-item>
        <el-form-item label="适用场次" prop="applicable_session">
          <el-input v-model="createForm.applicable_session" placeholder="如：2024春季班" />
        </el-form-item>
        <el-form-item label="摆放区域" prop="current_area">
          <el-input v-model="createForm.current_area" placeholder="如：A区第1排" />
        </el-form-item>
        <el-form-item label="责任人" prop="responsible_person">
          <el-input v-model="createForm.responsible_person" placeholder="请输入责任人" />
        </el-form-item>
        <el-form-item label="初始状态" prop="status">
          <el-select v-model="createForm.status" style="width: 100%">
            <el-option label="待制作" value="pending_production" />
            <el-option label="可发放" value="available" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="createForm.remark" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="引导牌详情" width="700px">
      <el-descriptions :column="2" border v-if="currentSign">
        <el-descriptions-item label="引导牌编号">{{ currentSign.sign_number }}</el-descriptions-item>
        <el-descriptions-item label="批次编号">{{ currentSign.batch_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="适用场次">{{ currentSign.applicable_session }}</el-descriptions-item>
        <el-descriptions-item label="当前区域">{{ currentSign.current_area }}</el-descriptions-item>
        <el-descriptions-item label="责任人">{{ currentSign.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentSign.status)">{{ getStatusLabel(currentSign.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentSign.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-tabs v-model="activeTab" class="detail-tabs" v-if="currentSign">
        <el-tab-pane label="位置调整记录" name="position">
          <el-table :data="currentSign.position_records || []" size="small">
            <el-table-column prop="from_area" label="原区域" width="180" />
            <el-table-column prop="to_area" label="新区域" width="180" />
            <el-table-column prop="operator" label="操作人" width="120" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="发放/回收记录" name="issue">
          <el-table :data="currentSign.issue_records || []" size="small">
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.issue_type === 'issue' ? 'success' : 'info'">
                  {{ row.issue_type === 'issue' ? '发放' : '回收' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="session" label="场次" width="140" />
            <el-table-column prop="operator" label="操作人" width="120" />
            <el-table-column prop="receiver" label="领用人" width="120" />
            <el-table-column prop="remark" label="备注" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="复核记录" name="review">
          <el-table :data="currentSign.review_records || []" size="small">
            <el-table-column label="结论" width="120">
              <template #default="{ row }">
                <el-tag :type="row.conclusion === 'deactivate' ? 'danger' : 'success'">
                  {{ { restore: '恢复可用', deactivate: '停用', reissue: '重新发放' }[row.conclusion] || row.conclusion }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reviewer" label="复核人" width="120" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="adjustDialogVisible" title="位置调整" width="450px">
      <el-form :model="adjustForm" :rules="adjustRules" ref="adjustFormRef" label-width="100px">
        <el-form-item label="当前区域">
          <el-input :value="currentSign?.current_area" disabled />
        </el-form-item>
        <el-form-item label="调整到" prop="to_area">
          <el-input v-model="adjustForm.to_area" placeholder="请输入新区域" />
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="adjustForm.operator" placeholder="请输入操作人" />
        </el-form-item>
        <el-form-item label="调整原因" prop="reason">
          <el-input v-model="adjustForm.reason" type="textarea" :rows="2" placeholder="请输入原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdjust" :loading="submitLoading">确认调整</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑引导牌" width="500px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="引导牌编号">
          <el-input v-model="editForm.sign_number" disabled />
        </el-form-item>
        <el-form-item label="批次编号">
          <el-input v-model="editForm.batch_code" />
        </el-form-item>
        <el-form-item label="适用场次" prop="applicable_session">
          <el-input v-model="editForm.applicable_session" />
        </el-form-item>
        <el-form-item label="摆放区域" prop="current_area">
          <el-input v-model="editForm.current_area" />
        </el-form-item>
        <el-form-item label="责任人" prop="responsible_person">
          <el-input v-model="editForm.responsible_person" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEdit" :loading="submitLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { STATUS_MAP, getStatusLabel, getStatusType } from '@/utils/statusMap'

const loading = ref(false)
const submitLoading = ref(false)
const signList = ref([])
const currentSign = ref(null)

const filterForm = reactive({
  status: '',
  batch_code: '',
  applicable_session: '',
  responsible_person: '',
  keyword: ''
})

const createDialogVisible = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  sign_number: '',
  batch_code: '',
  applicable_session: '',
  current_area: '',
  responsible_person: '',
  status: 'pending_production',
  remark: ''
})
const createRules = {
  sign_number: [{ required: true, message: '请输入引导牌编号', trigger: 'blur' }],
  applicable_session: [{ required: true, message: '请输入适用场次', trigger: 'blur' }],
  current_area: [{ required: true, message: '请输入摆放区域', trigger: 'blur' }],
  responsible_person: [{ required: true, message: '请输入责任人', trigger: 'blur' }]
}

const detailDialogVisible = ref(false)
const activeTab = ref('position')

const adjustDialogVisible = ref(false)
const adjustFormRef = ref(null)
const adjustForm = reactive({
  to_area: '',
  operator: '',
  reason: ''
})
const adjustRules = {
  to_area: [{ required: true, message: '请输入新区域', trigger: 'blur' }],
  operator: [{ required: true, message: '请输入操作人', trigger: 'blur' }]
}

const editDialogVisible = ref(false)
const editFormRef = ref(null)
const editForm = reactive({
  id: null,
  sign_number: '',
  batch_code: '',
  applicable_session: '',
  current_area: '',
  responsible_person: '',
  remark: ''
})
const editRules = {
  applicable_session: [{ required: true, message: '请输入适用场次', trigger: 'blur' }],
  current_area: [{ required: true, message: '请输入摆放区域', trigger: 'blur' }],
  responsible_person: [{ required: true, message: '请输入责任人', trigger: 'blur' }]
}

async function fetchList() {
  loading.value = true
  try {
    const params = {}
    Object.keys(filterForm).forEach(key => {
      if (filterForm[key]) params[key] = filterForm[key]
    })
    signList.value = await request.get('/signs', { params })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  filterForm.status = ''
  filterForm.batch_code = ''
  filterForm.applicable_session = ''
  filterForm.responsible_person = ''
  filterForm.keyword = ''
  fetchList()
}

function openCreateDialog() {
  createDialogVisible.value = true
  Object.assign(createForm, {
    sign_number: '',
    batch_code: '',
    applicable_session: '',
    current_area: '',
    responsible_person: '',
    status: 'pending_production',
    remark: ''
  })
}

async function handleCreate() {
  try {
    await createFormRef.value.validate()
    submitLoading.value = true
    await request.post('/signs', createForm)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    fetchList()
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  } finally {
    submitLoading.value = false
  }
}

async function openDetailDialog(row) {
  currentSign.value = await request.get(`/signs/${row.id}`)
  detailDialogVisible.value = true
}

function openAdjustDialog(row) {
  currentSign.value = { ...row }
  adjustDialogVisible.value = true
  adjustForm.to_area = ''
  adjustForm.operator = ''
  adjustForm.reason = ''
}

async function handleAdjust() {
  try {
    await adjustFormRef.value.validate()
    submitLoading.value = true
    await request.post(`/signs/${currentSign.value.id}/adjust-position`, adjustForm)
    ElMessage.success('位置调整成功')
    adjustDialogVisible.value = false
    fetchList()
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  } finally {
    submitLoading.value = false
  }
}

function openEditDialog(row) {
  editForm.id = row.id
  editForm.sign_number = row.sign_number
  editForm.batch_code = row.batch_code
  editForm.applicable_session = row.applicable_session
  editForm.current_area = row.current_area
  editForm.responsible_person = row.responsible_person
  editForm.remark = row.remark
  editDialogVisible.value = true
}

async function handleEdit() {
  try {
    await editFormRef.value.validate()
    submitLoading.value = true
    await request.put(`/signs/${editForm.id}`, {
      batch_code: editForm.batch_code,
      applicable_session: editForm.applicable_session,
      current_area: editForm.current_area,
      responsible_person: editForm.responsible_person,
      remark: editForm.remark
    })
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    fetchList()
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await request.delete(`/signs/${row.id}`)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  }
}

async function handleMarkAvailable(row) {
  try {
    await request.post(`/signs/${row.id}/status/available`)
    ElMessage.success('已标记为可发放')
    fetchList()
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.sign-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.detail-tabs {
  margin-top: 20px;
}
</style>
