// 获取的模型接口数据（公开，不含渠道信息）
export interface modelInfoSchema {
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
    channels: string[];
    description: string;
    icon: string;
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

// 渠道配置数据（对应后端 ChannelSchema，字段使用驼峰别名）
export interface channelInfoSchema {
    channelName: string;
    baseUrl: string;
    apiKey: string;
    supportModels: string[];
    status: boolean;
    timeout: number;
    usedRatio: number;
    description: string | null;
}