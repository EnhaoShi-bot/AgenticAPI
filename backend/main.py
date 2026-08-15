from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from apis import channels_api, operations_api, models_api
from backend.db.session import init_database  # 【数据库初始化】导入建表函数，启动时自动创建所有数据表

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("应用启动中...")
    # 【关键步骤】项目启动时初始化数据库表
    # - 自动扫描 mysql_tables.py 中所有继承 BaseModel 的表定义
    # - 只创建不存在的表，已存在的表会被跳过（安全幂等操作）
    await init_database()
    print("应用启动完成！")
    yield
    # 关闭时执行（如果需要清理资源）
    print("应用关闭中...")

# 初始化FastAPI应用，并注册 lifespan
app = FastAPI(title="AgenticAPI", version="1.0.0", lifespan=lifespan)

app.include_router(models_api.router) # 和模型列表相关接口
app.include_router(channels_api.router) # 和渠道列表相关接口
app.include_router(operations_api.router) # 和上游渠道运维相关接口

@app.get("/hello")
def read_root():
    """
    测试接口
    :return: 测试消息
    """
    return {"Message": "Hello World123"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=2027)