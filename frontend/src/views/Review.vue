<template>
  <div class="review-page">
    <el-card class="stats-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">待复核</div>
            <div class="stat-value danger">{{ stats.pending_review || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">已恢复可用</div>
            <div class="stat-value success">{{ stats.restored || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">已停用</div>
            <div class="stat-value info">{{ stats.deactivated || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总引导牌数</div>
            <div class="stat-value">{{ stats.total_signs || 0 }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>待复核列表</span>
          <el-button type="primary" @click="fetchList">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
        </div>
      </template>
      <el-table :data="reviewList" v-loading="loading" stripe>
        <el-table-column prop="sign_number" label="引导牌编号" width="140" />
        <el-table-column prop="batch_code" label="批次编号" width="120" />
        <el-table-column prop="applicable_session" label="适用场次" width="140" />
        <el-table-column prop="current_area" label="摆放区域" width="140" />
        <el-table-column prop="responsible_person" label="责任人" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="danger">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openReviewDialog(row)">复核</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="reviewDialogVisible" title="复核引导牌" width="500px">
      <el-descriptions :column="1" border size="small" v-if="currentSign">
        <el-descriptions-item label="引导牌编号">{{ currentSign.sign_number }}</el-descriptions-item>
        <el-descriptions-item label="当前区域">{{ currentSign.current_area }}</el-descriptions-item>
        <el-descriptions-item label="责任人">{{ currentSign.responsible_person }}</el-descriptions-item>
      </el-descriptions>
      
      <el-divider />
      
      <el-form :model="reviewForm" :rules="reviewRules" ref="reviewFormRef" label-width="90px">
        <el-form-item label="复核人" prop="reviewer">
          <el-input v-model="reviewForm.reviewer" placeholder="请输入复核人姓名" />
        </el-form-item>
        <el-form-item label="复核结论" prop="conclusion">
          <el-radio-group v-model="reviewForm.conclusion">
            <el-radio value="restore">恢复可用</el-radio>
            <el-radio value="reissue">重新发放</el-radio>
            <el-radio value="deactivate">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="复核原因" prop="reason">
          <el-input v-model="reviewForm.reason" type="textarea" :rows="3" placeholder="请输入复核原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleReview" :loading="submitLoading">确认复核</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { getStatusLabel } from '@/utils/statusMap'

const loading = ref(false)
const submitLoading = ref(false)
const reviewList = ref([])
const currentSign = ref(null)
const stats = reactive({
  total_signs: 0,
  pending_review: 0,
  restored: 0,
  deactivated: 0
})

const reviewDialogVisible = ref(false)
const reviewFormRef = ref(null)
const reviewForm = reactive({
  reviewer: '',
  conclusion: 'restore',
  reason: ''
})
const reviewRules = {
  reviewer: [{ required: true, message: '请输入复核人', trigger: 'blur' }],
  conclusion: [{ required: true, message: '请选择复核结论', trigger: 'change' }],
  reason: [{ required: true, message: '请输入复核原因', trigger: 'blur' }]
}

async function fetchList() {
  loading.value = true
  try {
    const data = await request.get('/stats/overview')
    reviewList.value = data.pending_review_list || []
    stats.total_signs = data.total_signs
    stats.pending_review = data.pending_review
    stats.restored = data.restored
    stats.deactivated = data.deactivated
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openReviewDialog(row) {
  currentSign.value = { ...row }
  reviewDialogVisible.value = true
  reviewForm.reviewer = ''
  reviewForm.conclusion = 'restore'
  reviewForm.reason = ''
}

async function handleReview() {
  try {
    await reviewFormRef.value.validate()
    submitLoading.value = true
    await request.post(`/signs/${currentSign.value.id}/review`, reviewForm)
    ElMessage.success('复核完成')
    reviewDialogVisible.value = false
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
.review-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-card .stat-item {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.danger {
  color: #f56c6c;
}

.stat-value.info {
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
</style>
