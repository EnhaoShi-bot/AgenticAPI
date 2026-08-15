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
