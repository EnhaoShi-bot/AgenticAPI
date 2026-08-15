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
