export const STATUS_MAP = {
  pending_production: { label: '待制作', type: 'info' },
  available: { label: '可发放', type: 'success' },
  issued: { label: '已发放', type: 'warning' },
  pending_recycle: { label: '待回收', type: 'warning' },
  pending_review: { label: '待复核', type: 'danger' },
  restored: { label: '恢复可用', type: 'success' },
  deactivated: { label: '停用', type: 'info' }
}

export const ANOMALY_STATUS_MAP = {
  pending: { label: '待处理', type: 'danger' },
  processing: { label: '处理中', type: 'warning' },
  pending_confirm: { label: '待确认', type: 'warning' },
  closed: { label: '已关闭', type: 'success' }
}

export const ANOMALY_TYPE_MAP = {
  lost: { label: '丢失', type: 'danger' },
  damaged: { label: '损坏', type: 'warning' },
  wrong_issue: { label: '错发', type: 'warning' },
  overdue: { label: '逾期未还', type: 'warning' },
  other: { label: '其他', type: 'info' }
}

export const ANOMALY_LEVEL_MAP = {
  low: { label: '低', type: 'info' },
  normal: { label: '一般', type: 'warning' },
  high: { label: '高', type: 'danger' },
  critical: { label: '严重', type: 'danger' }
}

export const ANOMALY_ACTION_MAP = {
  register: '异常登记',
  start_process: '开始处理',
  submit_confirm: '提交确认',
  confirm_close: '确认关闭',
  reject: '驳回到处理',
  reopen: '重新打开',
  add_remark: '添加备注'
}

export function getStatusLabel(status) {
  return STATUS_MAP[status]?.label || status
}

export function getStatusType(status) {
  return STATUS_MAP[status]?.type || 'info'
}

export function getAnomalyStatusLabel(status) {
  return ANOMALY_STATUS_MAP[status]?.label || status
}

export function getAnomalyStatusType(status) {
  return ANOMALY_STATUS_MAP[status]?.type || 'info'
}

export function getAnomalyTypeLabel(type) {
  return ANOMALY_TYPE_MAP[type]?.label || type
}

export function getAnomalyTypeType(type) {
  return ANOMALY_TYPE_MAP[type]?.type || 'info'
}

export function getAnomalyLevelLabel(level) {
  return ANOMALY_LEVEL_MAP[level]?.label || level
}

export function getAnomalyLevelType(level) {
  return ANOMALY_LEVEL_MAP[level]?.type || 'info'
}

export function getAnomalyActionLabel(action) {
  return ANOMALY_ACTION_MAP[action] || action
}
