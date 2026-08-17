// 监控面板相关类型

/** 全站累计用量（对话数据页顶部卡片） */
export interface siteSummarySchema {
    calls: number
    promptTokens: number
    completionTokens: number
    cacheTokens: number
}

/** 一条对话记录（监控面板-对话数据） */
export interface chatRecordSchema {
    id: number
    userId: number
    username: string
    modelName: string
    channelName: string | null
    /** 调用时的 messages 数组：[{role, content}]，content 一般是字符串 */
    inputContent: { role: string; content: unknown }[] | null
    reasoningContent: string | null
    outputContent: string | null
    promptTokens: number
    completionTokens: number
    cacheTokens: number
    cost: number
    durationMs: number | null
    createTime: string | null
}

/** 一条系统日志（监控面板-调用日志） */
export interface logItemSchema {
    id: number
    /** api / login / admin / user */
    type: string
    userId: number | null
    username: string | null
    action: string
    detail: string | null
    modelName: string | null
    channelName: string | null
    promptTokens: number
    completionTokens: number
    cacheTokens: number
    cost: number
    durationMs: number | null
    createTime: string | null
}

/** 分页结果（与后端 {list, total} 约定一致） */
export interface pagedResult<T> {
    list: T[]
    total: number
}

/** 一个用量桶：某模型在某时间桶内的累计值（数据看板） */
export interface usageBucketSchema {
    time: string
    modelName: string
    calls: number
    promptTokens: number
    completionTokens: number
    cacheTokens: number
}

/** 用量统计响应：范围累计 + 每桶每模型序列 */
export interface userStatsSchema {
    totals: { calls: number; promptTokens: number; completionTokens: number; cacheTokens: number }
    buckets: usageBucketSchema[]
}

/** 折线图的一条曲线 */
export interface lineSeriesSchema {
    name: string
    data: number[]
}
