// 模型广场共用的领域小工具：标签拆分、分组标签配色/文案、表单默认值
import type {modelInfoSchema} from '@/types'

/** 标签字段按逗号拆分（"旗舰,对话" → ["旗舰","对话"]，兼容中文逗号） */
export function splitLabel(label: string | null | undefined): string[] {
    return (label || '').split(/[,，]/).map(s => s.trim()).filter(Boolean)
}

/** 分组标签配色：免费绿色、VIP 橙红，其余主色 */
export function groupTagColor(group: string): string {
    if (group === 'free') return 'green'
    if (group === 'vip') return 'orangered'
    return 'arcoblue'
}

/** 分组标签文案：free / vip 显示业务语义，其他分组显示原始名称 */
export function groupTagName(group: string): string {
    if (group === 'free') return '免费使用'
    if (group === 'vip') return '会员专用'
    return group
}

/** 新建模型表单的初始值（添加抽屉与配置表单共用的默认态） */
export function createEmptyModelForm(): modelInfoSchema {
    return {
        name: '',
        upstreamName: '',
        label: '',
        modelGroup: '',
        isRequestMode: false,
        perRequestPrice: 0,
        inputPrice: 0,
        cachePrice: 0,
        outputPrice: 0,
        isPin: false,
        isLog: false,
        contextLength: 128,
        maxTokens: 4196,
        supportVision: false,
        status: false,
        channels: [],
        description: '',
        icon: '',
    }
}
