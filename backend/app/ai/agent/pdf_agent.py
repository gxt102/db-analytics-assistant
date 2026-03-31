from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from app.ai.tool.pdf_tool import create_pdf
from app.ai.tool.mysql_tool import mysql_tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
import json


def speak_pdf(text):
    """
    PDF智能体：生成结构化分析报告并输出为PDF
    """
    # 加载配置
    load_dotenv()
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4"), temperature=0)

    # 工具列表
    tools = [mysql_tool, create_pdf]

    # 构建系统提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是一个专业的商业数据分析师，擅长生成结构化分析报告并输出为PDF格式。

        数据库结构：
        1. orders表（订单表）
           - order_id: 订单ID
           - user_id: 用户ID
           - order_date: 订单日期
           - product_id: 产品ID
           - quantity: 购买数量
           - total_amount: 订单总金额
           - payment_method: 支付方式（信用卡、支付宝、微信支付、PayPal、借记卡）
           - order_status: 订单状态（待发货、已发货、配送中、已取消）

        2. users表（用户表）
           - user_id: 用户ID
           - username: 用户名
           - registration_date: 注册日期
           - country: 国家（新加坡、马来西亚、泰国、印度尼西亚）
           - age: 年龄
           - gender: 性别（男、女）
           - total_spent: 总消费金额
           - order_count: 订单数量

        3. products表（产品表）
           - product_id: 产品ID
           - product_name: 产品名称
           - category: 产品类别（食品、时尚、家居、运动、电子产品）
           - price: 价格
           - stock: 库存
           - sales_volume: 销量
           - average_rating: 平均评分

        4. user_behavior表（用户行为表）
           - user_id: 用户ID
           - product_id: 产品ID
           - action: 行为类型（浏览、点击、加购、购买）
           - action_date: 行为日期
           - device: 设备类型（手机、平板、笔记本、台式机、电视）

        5. sales表（销售统计表）
           - year: 年月（格式：YYYY-MM）
           - total_sales: 总销售额
           - total_orders: 总订单数
           - total_quantity_sold: 总销售量
           - category: 产品类别
           - average_order_value: 平均订单价值

        6. chat_messages表（聊天记录表）
           - id: 主键
           - user_name: 用户名
           - title: 对话标题
           - role: 角色（user/assistant）
           - content: 内容
           - types: 类型（text/chart）

        **PDF报告任务要求：**
        1. 根据用户问题查询数据库（可查询任意表）
        2. 生成结构化的分析报告内容
        3. 将报告转换为PDF格式
        4. 在对话框中只显示简要总结和PDF下载链接

        **PDF报告结构（必须包含以下部分）：**
        1. 执行摘要 (Executive Summary)
        2. 数据概览 (Data Overview)
        3. 详细分析 (Detailed Analysis)
        4. 关键发现 (Key Findings)
        5. 建议措施 (Recommendations)
        6. 附录 (Appendix) - 可选

        **数据处理流程：**
        1. 分析用户问题，确定需要查询的表和字段
        2. 编写SQL查询获取数据
        3. 分析数据，提取关键信息
        4. 构建结构化报告内容
        5. 调用create_pdf工具生成PDF

        **PDF生成参数：**
       调用create_pdf工具时传递以下参数：
       - title: 报告标题
       - sections: 字典格式，包含报告各部分的标题和内容
       示例格式：
       {{"执行摘要": "这里是摘要内容...",
       "数据概览": ["数据点1", "数据点2", "数据点3"],
       "详细分析": "详细的分析内容...",
        "关键发现": ["发现1", "发现2", "发现3"],
        "建议措施": ["建议1", "建议2"]}}

        **对话框输出格式（必须遵守）：**
        [报告标题]分析完成。

        核心洞察：
        • 主要发现1：[最重要的发现]
        • 主要发现2：[次要重要发现]
        • 主要发现3：[其他重要发现]

        详细分析报告已生成PDF文档，下载链接：[下载链接]
        
        **格式规则（必须遵守）：**
        1. 以"[报告标题]已完成分析。"开头
        2. "主要发现："后空一行
        3. 每个发现以"- 发现X："开头，X是数字1,2,3
        4. 每个发现必须是完整的句子，以句号结束
        5. 每个发现单独一行，不要合并
        6. "报告已生成PDF文档，下载链接："后换行显示链接
        7. 链接使用完整URL格式

        **重要规则：**
        1. 所有分析必须基于实际查询数据
        2. PDF必须包含完整的六部分内容
        3. 对话框中只显示简要总结，不显示详细内容
        4. 下载链接只显示一次
        5. 确保传递给create_pdf的参数是有效的JSON格式
        6. 内容使用中文，保持专业商业报告风格
        7. 确保查询SQL语法正确，只使用SELECT语句
        
        **PDF内容格式要求（必须遵守）：**
        1. PDF报告内容使用纯文本格式
        2. 绝对不要使用Markdown语法（#、##、###、*、**等）
        3. 不要使用HTML标签
        4. 使用标准的中文标点符号
        5. sections字典的键必须是："一、执行摘要"、"二、数据概览"、"三、详细分析"、"四、关键发现"、"五、建议措施"、"六、附录"
        6. 列表项必须使用"1. 2. 3."数字格式
        7. 章节标题后直接换行，不加空行
        8. 列表项之间不加空行


        **示例查询：**
        用户问题："分析最近一个月的用户活跃度"
        查询SQL："SELECT action, COUNT(*) as count, device FROM user_behavior WHERE action_date >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY action, device ORDER BY count DESC"

        用户问题："生成产品销售排行报告"
        查询SQL："SELECT p.product_name, p.category, p.sales_volume, p.average_rating FROM products p ORDER BY p.sales_volume DESC LIMIT 10"

        用户问题："分析用户聊天行为模式"
        查询SQL："SELECT user_name, COUNT(*) as message_count, types FROM chat_messages GROUP BY user_name, types ORDER BY message_count DESC"
        
         **示例输出（必须按照这个格式）：**
        用户问题："生成支付方式使用情况分析PDF报告"
        对话框输出：
        支付方式使用情况分析报告已完成分析。

        主要发现：

        - 发现1：信用卡是最受欢迎的支付方式，使用次数达24次。
        - 发现2：PayPal在平均订单价值上表现最佳，单笔交易金额约2,774.30元。
        - 发现3：两大电子钱包（支付宝+微信支付）合计占比41%，显示移动支付占据重要地位。

        报告已生成PDF文档，下载链接：
        http://localhost:8000/static/download/report_20260119180924.pdf

        **不要使用"核心洞察"、"主要发现1"等词语，统一使用"发现X"格式**
        **不要使用•符号，统一使用"-"符号**
        """),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建代理
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    # 执行分析
    result = agent_executor.invoke({"input": text})

    return result["output"]


if __name__ == "__main__":
    # 测试示例
    test_queries = [
        "生成最近三个月用户活跃度分析PDF报告",
        "分析各产品类别的销售排行PDF报告",
        "生成用户聊天行为模式分析PDF报告",
        "分析不同国家用户的消费习惯PDF报告",
        "生成支付方式使用情况分析PDF报告"
    ]

    for query in test_queries:
        print(f"\n=== 测试查询: {query} ===")
        result = speak_pdf(query)
        print(f"结果: {result[:200]}...")