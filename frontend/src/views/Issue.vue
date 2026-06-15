<template>
  <div class="issue-page">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" @submit.prevent>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" style="width: 140px">
            <el-option label="可发放" value="available" />
            <el-option label="恢复可用" value="restored" />
            <el-option label="已发放" value="issued" />
          </el-select>
        </el-form-item>
        <el-form-item label="批次">
          <el-input v-model="filterForm.batch_code" placeholder="批次编号" clearable style="width: 140px" />
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

    <el-card>
      <template #header>
        <div class="card-header">
          <span>可发放引导牌</span>
          <el-tag type="success">可发放：{{ availableCount }} 张</el-tag>
        </div>
      </template>
      <el-table :data="signList" v-loading="loading" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" :selectable="checkSelectable" />
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
      </el-table>
    </el-card>

    <el-drawer v-model="issueDrawerVisible" title="批量发放" size="420px" direction="rtl">
      <el-form :model="issueForm" :rules="issueRules" ref="issueFormRef" label-width="90px">
        <el-form-item label="选中数量">
          <el-tag type="success" size="large">{{ selectedSigns.length }} 张</el-tag>
        </el-form-item>
        <el-form-item label="适用场次" prop="session">
          <el-input v-model="issueForm.session" placeholder="如：2024春季班试听" />
        </el-form-item>
        <el-form-item label="领用人" prop="receiver">
          <el-input v-model="issueForm.receiver" placeholder="请输入领用人" />
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="issueForm.operator" placeholder="请输入操作人" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="issueForm.remark" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="issueDrawerVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchIssue" :loading="submitLoading">
          确认发放
        </el-button>
      </template>
    </el-drawer>

    <div class="issue-action-bar" v-if="selectedSigns.length > 0">
      <span>已选择 {{ selectedSigns.length }} 张可发放引导牌</span>
      <el-button type="primary" size="large" @click="issueDrawerVisible = true">
        <el-icon><Promotion /></el-icon>批量发放
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Promotion } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { getStatusLabel, getStatusType } from '@/utils/statusMap'

const loading = ref(false)
const submitLoading = ref(false)
const signList = ref([])
const selectedSigns = ref([])

const filterForm = reactive({
  status: 'available',
  batch_code: '',
  keyword: ''
})

const availableCount = computed(() => {
  return signList.value.filter(s => s.status === 'available' || s.status === 'restored').length
})

const issueDrawerVisible = ref(false)
const issueFormRef = ref(null)
const issueForm = reactive({
  session: '',
  receiver: '',
  operator: '',
  remark: ''
})
const issueRules = {
  session: [{ required: true, message: '请输入适用场次', trigger: 'blur' }],
  receiver: [{ required: true, message: '请输入领用人', trigger: 'blur' }],
  operator: [{ required: true, message: '请输入操作人', trigger: 'blur' }]
}

function checkSelectable(row) {
  return row.status === 'available' || row.status === 'restored'
}

function handleSelectionChange(selection) {
  selectedSigns.value = selection.filter(s => checkSelectable(s))
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
  filterForm.status = 'available'
  filterForm.batch_code = ''
  filterForm.keyword = ''
  fetchList()
}

async function handleBatchIssue() {
  try {
    await issueFormRef.value.validate()
    if (selectedSigns.value.length === 0) {
      ElMessage.warning('请选择要发放的引导牌')
      return
    }
    
    submitLoading.value = true
    let successCount = 0
    let failCount = 0
    
    for (const sign of selectedSigns.value) {
      try {
        await request.post(`/signs/${sign.id}/issue`, {
          receiver: issueForm.receiver,
          session: issueForm.session,
          operator: issueForm.operator,
          remark: issueForm.remark
        })
        successCount++
      } catch (e) {
        failCount++
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`成功发放 ${successCount} 张引导牌${failCount > 0 ? `，失败 ${failCount} 张` : ''}`)
    } else {
      ElMessage.error('发放失败')
    }
    
    issueDrawerVisible.value = false
    fetchList()
  } catch (e) {
    if (e?.message) ElMessage.error(e.message)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.issue-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 80px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.issue-action-bar {
  position: fixed;
  bottom: 20px;
  right: 40px;
  background: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 100;
}

.issue-action-bar span {
  color: #606266;
  font-size: 14px;
}
</style>
