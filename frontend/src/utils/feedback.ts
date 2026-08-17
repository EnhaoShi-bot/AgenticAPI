/* 全局反馈工具：把 Arco 的 Modal.confirm 封装成 Promise，替代原 ElMessageBox.confirm 的用法 */
import { Modal } from '@arco-design/web-vue'

/** 确认弹窗，resolve(true) 表示用户点击了确认 */
export function confirmDialog(
  content: string,
  title = '操作确认',
  okText = '确定',
  danger = false,
): Promise<boolean> {
  return new Promise((resolve) => {
    Modal.confirm({
      title,
      content,
      okText,
      cancelText: '取消',
      okButtonProps: danger ? { status: 'danger' } : undefined,
      onOk: () => resolve(true),
      onCancel: () => resolve(false),
    })
  })
}
