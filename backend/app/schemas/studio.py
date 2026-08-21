"""模型工坊相关请求 Schema

工坊对话接口走 OpenAI 风格报文（snake_case + SSE 流式），与 /v1 中转接口保持一致，
不套用站内管理接口的驼峰别名规范；ASR 接口为普通 JSON 接口（字段为单词，无别名差异）。
"""

from typing import Union

from pydantic import BaseModel, Field


class StudioMessageSchema(BaseModel):
    """单条消息：content 为纯文本字符串，或 OpenAI 多模态 parts 数组（图片 + 文本）"""

    role: str = Field(description="user / assistant / system")
    content: Union[str, list] = Field(description="文本或多模态内容数组")


class StudioChatSchema(BaseModel):
    """工坊对话请求体"""

    model: str = Field(description="模型名")
    messages: list[StudioMessageSchema] = Field(description="本轮之前的对话历史（不含 system）")
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, ge=0, le=1)
    max_tokens: int | None = Field(default=None, ge=1)
    system_prompt: str = Field(default="", description="系统提示词，由后端拼到消息头")
    enable_search: bool = Field(default=False, description="联网搜索开关")


class StudioAsrSchema(BaseModel):
    """语音转文本请求体"""

    audio: str = Field(description="base64 编码的录音数据")
    format: str = Field(default="mp3", description="音频格式：mp3 / ogg 等")


class StudioTitleSchema(BaseModel):
    """会话标题生成请求体"""

    content: str = Field(description="首条用户消息文本", max_length=8000)