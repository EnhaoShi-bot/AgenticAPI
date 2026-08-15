"""AgenticAPI 应用入口"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.database import init_database


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


@app.get("/hello")
def read_root():
    """
    测试接口
    :return: 测试消息
    """
    return {"Message": "Hello World123"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=2027)
