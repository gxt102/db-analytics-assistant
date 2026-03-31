from pydantic import BaseModel, Field
from langchain.tools import tool
from email.mime.text import MIMEText
import smtplib
import os


# 创建一个邮件发送的参数类
class EmailArgs(BaseModel):
    to_email: str = Field(..., description="收件人邮箱")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容")


# 定义一个邮件发送的函数
@tool(args_schema=EmailArgs)
def send_email_tool(to_email: str, subject: str, content: str) -> str:
    """
    发送邮件
    """
    # 定义一个邮件对象
    msg = MIMEText(content)
    # 定义收件人
    msg["To"] = to_email
    # 定义发件人
    msg["From"] = "3182983345@qq.com"
    # 定义邮件主题
    msg["Subject"] = subject

    # 登录邮件服务器
    smtp = smtplib.SMTP_SSL(os.getenv("email_host"), port=465)
    smtp.login(user="3182983345@qq.com", password=os.getenv("email_password"))
    # 发送邮件
    smtp.sendmail(from_addr="3182983345@qq.com", to_addrs=to_email, msg=msg.as_string())

    return "发送成功"



send_email = send_email_tool