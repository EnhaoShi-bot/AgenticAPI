// 火山方舟渠道的用量数据
export interface volUsageData {
    status: string;
    fiveHour: { used: number; quota: number }
    weekly: { used: number; quota: number }
    monthly: { used: number; quota: number }
}

// 深势科技渠道的用量数据
export interface bohrUsageData {
    status: string;
    fiveHour: { used: number; quota: number }
    weekly: { used: number; quota: number }
    monthly: { used: number; quota: number }
}

// 阶跃星辰渠道的用量数据
export interface stepfunUsageData {
    status: string;
    fiveHour: { used: number; quota: number }
    weekly: { used: number; quota: number }
    monthly: { used: number; quota: number }
}

// 数据接口定义，向后端发送cookie等信息
export interface cookieSettings {
    brmToken: string
    instanceId: string
    stepToken: string
    stepWebid: string
}
