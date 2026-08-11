from fastapi import FastAPI
import uvicorn
from apis import models_api, operations_api

# 初始化FastAPI应用
app = FastAPI(title="AgenticAPI", version="1.0.0")

app.include_router(models_api.router)
app.include_router(operations_api.router)

if __name__ == "__main__":
    # print("此处打印的MySQL URL为：" + setting.MYSQL_URL)
    uvicorn.run("main:app", host="127.0.0.1", port=2027, reload=True)
