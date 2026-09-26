// 用量窗口：resetAt 为配额重置时间（后端已格式化为 "YYYY-MM-DD HH:MM"），上游未返回时为 null，前端不展示
interface usageWindow {
    used: number; quota: number; resetAt?: string | null
}

// 火山方舟渠道的用量数据
export interface volUsageData {
    status: string;
    fiveHour: usageWindow
    weekly: usageWindow
    monthly: usageWindow
}

// 阶跃星辰渠道的用量数据
export interface stepfunUsageData {
    status: string;
    fiveHour: usageWindow
    weekly: usageWindow
    monthly: usageWindow
}

// 智谱渠道的用量数据（仅 5 小时 / 7 天两个窗口，无月度限额）
export interface zaiUsageData {
    status: string;
    fiveHour: usageWindow
    weekly: usageWindow
    monthly: usageWindow
}

// 智谱渠道（账号二，v2 套餐）的用量数据：上游仅返回已用百分比，used/total 为 百分比/100
export interface zai2UsageData {
    status: string;
    fiveHour: usageWindow
    weekly: usageWindow
    monthly: usageWindow
}

// CommandCode 渠道的用量数据：月度总额度上游不返回，由后端按 GOAT 套餐 70 写死并换算已用量
export interface commandcodeUsageData {
    status: string;
    fiveHour: usageWindow
    weekly: usageWindow
    monthly: usageWindow
}

// Antigravity（Google Gemini PRO）的限额数据：上游为「每模型剩余百分比 + 5 小时窗口重置」，
// 文本模型额度共享，后端只取主力模型 gemini-3.8-flash（上游缺失该模型时回落 recommended / 剩余最低，
// model 字段回显实际采用的模型名）
export interface antigravityUsageData {
    status: string;
    email: string
    source: 'live' | 'cache'   // live=实时拉取（容器经 VPN 查 Google），cache=容器缓存回落
    model: string
    used: number
    resetAt?: string | null
}

// 数据接口定义，向后端发送cookie等信息
// 注：智谱凭证已迁移到后端 .env（ZAI_API_KEY / ZAI_API_KEY_2），不再经由前端上传
export interface cookieSettings {
    brmToken: string
    instanceId: string
    stepToken: string
    stepWebid: string
}
