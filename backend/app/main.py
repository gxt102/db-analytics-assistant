from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from api.chat.chat_router import chat_router
from api.system.login_router import login_router
#创建一个app对象
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 前端应用地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#配置静态资源访问
app.mount("/static",StaticFiles(directory="static"),name="static")

#把chat_router注册到app中
app.include_router(chat_router)
app.include_router(login_router)

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)