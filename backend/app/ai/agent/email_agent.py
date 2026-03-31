from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from app.ai.tool.email_tool import send_email_tool
from app.ai.tool.mysql_tool import mysql_tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
import random


def speak_email(text):
    # 第一步：加载配置
    load_dotenv()
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"))

    # 第二步: 创建工具
    tool = [send_email_tool, mysql_tool]

    # 第三步: 生成验证码
    code = str(random.randint(1000, 9999))
    print(f"生成的验证码: {code}")

    # 第四步: 创建一个提示词（明确告诉智能体使用这个验证码）
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            你是一个邮件发送智能助手, 你有两个工具: send_email_tool, mysql_tool
            数据库模式：
            employer 员工表 列名emp_id,emp_name,email

            请严格按照以下步骤执行：

            步骤1：使用mysql_tool查询邮箱是否存在
                SQL示例：SELECT * FROM employer WHERE email = '用户邮箱'

            步骤2：如果邮箱存在：
                - 使用send_email_tool发送邮件
                - 邮件主题必须是：验证码
                - 邮件内容必须是：{code} （使用我提供的这个验证码）
                - 返回：验证码已发送：{code}

            步骤3：如果邮箱不存在：
                - 不要发送邮件
                - 返回：邮箱不存在，请注册

            重要：邮件内容必须完全使用我提供的验证码：{code}，不要自己生成任何验证码！
        """),
        ("human", "{input}"),  # 用户输入（包含邮箱）
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 第五步: 创建代理
    agent = create_tool_calling_agent(llm=llm, tools=tool, prompt=prompt)
    agent_executer = AgentExecutor(agent=agent, tools=tool, verbose=True)

    # 第六步: 执行，传入验证码
    rs = agent_executer.invoke({
        "input": text,  # 比如："邮箱是：3182983345@qq.com"
        "code": code  # 传入生成的验证码
    })

    # 返回结果
    return rs["output"]
if __name__ == "__main__":
    print(speak_email("邮箱是：3182983345@qq.com"))