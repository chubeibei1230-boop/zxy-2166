export const STATUS_MAP = {
  pending_production: { label: '待制作', type: 'info' },
  available: { label: '可发放', type: 'success' },
  issued: { label: '已发放', type: 'warning' },
  pending_recycle: { label: '待回收', type: 'warning' },
  pending_review: { label: '待复核', type: 'danger' },
  restored: { label: '恢复可用', type: 'success' },
  deactivated: { label: '停用', type: 'info' }
}

export function getStatusLabel(status) {
  return STATUS_MAP[status]?.label || status
}

export function getStatusType(status) {
  return STATUS_MAP[status]?.type || 'info'
}
