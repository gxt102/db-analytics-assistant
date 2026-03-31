from certifi.__main__ import args
from fastapi import APIRouter
from app.api.schema.EmailArgs import EmailArgs
from app.ai.agent.email_agent import speak_email
import redis
import random


#创建一个redis服务链接
redis_client=redis.StrictRedis(host='localhost', port=6379, db=0)

#定义一个路由对象
login_router = APIRouter()
#定义一个发送验证码接口
@login_router.post("/sendCode")
def send_code(args: EmailArgs):
    print(f"请求邮箱: {args.email}")

    # 调用智能体
    rs = speak_email(f"邮箱是：{args.email}")
    print(f"智能体返回: {rs}")

    # 从返回结果中提取验证码
    import re
    match = re.search(r'\d{4}', rs)

    if "邮箱不存在，请注册" in rs:
        return {"code": 500, "msg": rs}
    elif match:
        code = match.group()
        print(f"验证码已发送: {code}")

        # 存储到Redis
        redis_client.set(args.email, code, ex=60)
        return {"code": 200, "msg": "验证码发送成功", "data": code}
    else:
        # 如果没提取到验证码，直接使用智能体返回的验证码部分
        if "验证码已发送：" in rs:
            # 假设格式是 "验证码已发送：1234"
            code_part = rs.split("验证码已发送：")[1].strip()
            # 提取数字
            code_match = re.search(r'\d{4}', code_part)
            if code_match:
                code = code_match.group()
                redis_client.set(args.email, code, ex=60)
                return {"code": 200, "msg": "验证码发送成功", "data": code}

        print(f"无法处理智能体返回: {rs}")
        return {"code": 500, "msg": "验证码发送失败"}

@login_router.post("/login")
def login(request: EmailArgs):
    #获取存入到redis的验证码
    code=redis_client.get(request.email)
    print("code",code)
    # 判断验证码是否失效
    if code is None:
        return {"code":500,"msg":"error"}
    elif code.decode()==request.code:
        return {"code":200,"msg":"success"}
    else:
        return {"code":500,"msg":"error"}

