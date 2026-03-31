from pydantic import BaseModel
#定义一个post请求需要的参数类
class ChatArgs(BaseModel):
    question:str
    userName:str
    title:str