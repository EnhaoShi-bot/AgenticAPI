"""AgenticAPI 应用入口"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.router.router import router as api_router
from app.core.config import server_setting
from app.core.database import init_database
from app.utils.exception import register_exception_handlers
from app.utils.response import success_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("应用启动中...")
    # 项目启动时初始化数据库表
    # - 自动扫描 app/models/ 下所有继承 BaseModel 的表定义
    # - 只创建不存在的表，已存在的表会被跳过（安全幂等操作）
    await init_database()
    print("应用启动完成！")
    yield
    # 关闭时执行（如果需要清理资源）
    print("应用关闭中...")


# 初始化 FastAPI 应用，并注册 lifespan
app = FastAPI(title="AgenticAPI", version="1.0.0", lifespan=lifespan)

app.include_router(api_router)

# 注册异常处理函数
register_exception_handlers(app)


@app.get("/")
def read_root():
    """
    测试接口
    :return: 测试消息
    """
    return success_response(message="Hello World")


if __name__ == "__main__":
    # 监听地址与端口从 backend/.env 读取（SERVER_HOST / SERVER_PORT）
    uvicorn.run("app.main:app", host=server_setting.SERVER_HOST, port=server_setting.SERVER_PORT)
