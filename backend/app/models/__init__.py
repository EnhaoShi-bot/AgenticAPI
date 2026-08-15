"""ORM 模型统一入口

导入此包即触发所有表定义注册到 BaseModel.metadata，
init_database() 依赖此机制自动建表。
新增表时：在 app/models/ 下新建模块，并在此处导入。
"""

from app.models.base import BaseModel
from app.models.llm_model import ModelsTable
from app.models.llm_channel import ChannelsTable

__all__ = ["BaseModel", "ModelsTable", "ChannelsTable"]
