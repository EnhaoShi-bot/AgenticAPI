// 获取的模型接口数据（公开，不含渠道信息）
export interface modelInfoSchema {
    id: number | string;
    name: string;
    label: string;
    modelGroup: string;
    isRequestMode: boolean;
    perRequestPrice: number;
    inputPrice: number;
    cachePrice: number;
    outputPrice: number;
    isPin: boolean;
    isLog: boolean;
    contextLength: number;
    maxTokens: number;
    supportVision: boolean;
    status: boolean;
}
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
// 阿里云渠道的用量数据
export interface aliUsageData {
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
    aliyunCookie: string
}