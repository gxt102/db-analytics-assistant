from pydantic import BaseModel
#定义一个登陆需要的接口参数类
class EmailArgs(BaseModel):
    email: str
    code:str