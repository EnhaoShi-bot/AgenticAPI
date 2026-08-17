"""监控面板相关请求 Schema"""

from pydantic import BaseModel, Field


class ThresholdUpdateSchema(BaseModel):
    """更新对话记录长度阈值（输入+输出 token 上限）"""

    value: int = Field(gt=0, le=1_000_000, description="输入+输出 token 上限，超过该值的调用不记录对话内容")
