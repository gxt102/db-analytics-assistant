from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import json
import re

from app.ai.tool.mysql_tool import mysql_tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor


def speak_echarts(text):
    # 第一步：创建一个大模型
    # 加载配置
    load_dotenv()
    # 创建一个聊天模型
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"))

    # 第二步: 创建工具
    tool = [mysql_tool]

    # 第三步: 创建一个提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
你是一个echarts图表生成助手, 你有一个工具:mysql_tool
数据库模式：
orders 订单表 列名有order_id(订单id),user_id,order_date,product_id,quantity,total_amount,payment_method,order_status
users 用户表 列名有user_id，username，registration_date，country，age，gender，total_spent，order_count
products 产品表 列名有product_id，product_name，category，price，stock，sales_volume，average_rating
user_behavior 用户行为表 列名有user_id，product_id，action，action_date，device
sales 销售记录表 列名有year，total_sales，total_orders，total_quantity_sold，category，average_order_value

请严格按照下面格式回答问题：
1. 分析用户问题，理解需要什么数据
2. 使用mysql_tool工具执行SQL查询获取数据
3. 将查询结果转换为echarts图表配置
4. 返回的数据必须是一个可执行的JSON格式，其他的文本信息不需要
5. 返回的图表必须有保存功能

JSON格式示例：
{{
    "title": {{"text": "图表标题", "left": "center"}},
    "tooltip": {{"trigger": "axis"}},
    "legend": {{"data": ["系列1", "系列2"]}},
    "xAxis": {{"type": "category", "data": ["数据1", "数据2", "数据3"]}},
    "yAxis": {{"type": "value"}},
    "series": [
        {{"name": "系列1", "type": "line", "data": [10, 20, 30]}},
        {{"name": "系列2", "type": "bar", "data": [15, 25, 35]}}
    ],
    "toolbox": {{
        "feature": {{
            "saveAsImage": {{
                "title": "保存图片",
                "type": "png"
            }}
        }}
    }}
}}

重要：只返回JSON对象，不要有任何解释文字！
        """),
        ("human", "{input}"),  # 用户输入提问的变量
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 第四步: 创建一个代理
    agent = create_tool_calling_agent(llm=llm, tools=tool, prompt=prompt)
    # 第五步: 执行代理
    agent_executer = AgentExecutor(agent=agent, tools=tool, verbose=True)
    # 第六步: 提问
    rs = agent_executer.invoke({"input": text})
    # 返回答案

    return handle_json(rs["output"])


# 定义处理```json
def handle_json(text):
    # 先尝试直接解析JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return format_echarts_json(data)
    except:
        pass

    # 如果有代码块标记，提取JSON
    if "```json" in text:
        try:
            json_str = text.split("```json")[1].split("```")[0].strip()
            data = json.loads(json_str)
            return format_echarts_json(data)
        except:
            pass

    # 尝试从任何代码块提取
    if "```" in text:
        try:
            code_blocks = re.findall(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            for block in code_blocks:
                try:
                    # 清理文本
                    cleaned = block.strip().replace("'", '"')
                    data = json.loads(cleaned)
                    if isinstance(data, dict):
                        return format_echarts_json(data)
                except:
                    continue
        except:
            pass

    # 尝试查找JSON对象
    try:
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            try:
                # 清理常见的JSON问题
                cleaned = match.replace("'", '"')
                cleaned = re.sub(r',\s*}', '}', cleaned)
                cleaned = re.sub(r',\s*]', ']', cleaned)
                data = json.loads(cleaned)
                if isinstance(data, dict):
                    return format_echarts_json(data)
            except:
                continue
    except:
        pass

    # 如果所有方法都失败，返回原始文本
    return text


def format_echarts_json(data):
    """格式化ECharts JSON配置"""
    if not isinstance(data, dict):
        data = {}

    # 确保有标题
    if "title" not in data:
        data["title"] = {"text": "数据分析图表", "left": "center"}

    # 确保有保存功能
    if "toolbox" not in data:
        data["toolbox"] = {
            "feature": {
                "saveAsImage": {
                    "title": "保存为图片",
                    "type": "png"
                }
            }
        }

    # 确保有数据系列
    if "series" not in data:
        data["series"] = []
    elif not isinstance(data["series"], list):
        data["series"] = [data["series"]]

    # 返回格式化的JSON
    return json.dumps(data, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 测试函数
    test_queries = [
        "分析各产品类别平均价格的变化趋势，请用折线图表呈现",
        "请用图表分析一下2025年11月订单的支付情况，请用饼图呈现",
        "国家用户数量展示不同的占比情况",
        "分析2025年各月销售额趋势",
    ]

    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"测试查询: {query}")
        print(f"{'=' * 60}")

        try:
            result = speak_echarts(query)
            print("返回结果:")
            print(result[:500] + "..." if len(result) > 500 else result)

            # 验证是否为有效JSON
            try:
                json.loads(result)
                print("✓ 有效的JSON格式")
            except json.JSONDecodeError:
                print("✗ 不是有效的JSON格式")

        except Exception as e:
            print(f"执行错误: {e}")