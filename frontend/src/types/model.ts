// 获取的模型接口数据（公开，不含渠道信息）
export interface modelInfoSchema {
    name: string;
    upstreamName?: string;
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

// 模型广场排序维度：名称或三个价格维度之一，方向升降序
export type modelSortField = 'name' | 'inputPrice' | 'outputPrice' | 'cachePrice';
export type modelSortOrder = 'asc' | 'desc';

