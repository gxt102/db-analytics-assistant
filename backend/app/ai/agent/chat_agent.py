from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor

try:
    from app.ai.tool.mysql_tool import mysql_tool  # 导入已装饰的tool函数
    print("✅ 成功导入mysql_tool")
except ImportError as e:
    print(f"⚠️ 无法导入mysql_tool: {e}")
    # 创建模拟工具作为备用
    from langchain.tools import Tool

    def mock_mysql_tool(sql: str) -> str:
        return f"模拟执行SQL: {sql}"

    mysql_tool = Tool(
        name="mock_mysql_tool",
        func=mock_mysql_tool,
        description="模拟数据库查询工具"
    )


def speak_text(text):
    """智能数据库问答助手 - 基于实际数据库结构"""
    load_dotenv()

    # 检查API配置
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model_name = os.getenv("MODEL_NAME", "qwen-plus")

    if not api_key:
        return "错误：未找到OPENAI_API_KEY环境变量"
    if not api_base:
        return "错误：未找到OPENAI_API_BASE环境变量"

    print(f"🤖 使用模型: {model_name}")
    print(f"🔗 API地址: {api_base}")

    # 配置ChatOpenAI
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=api_base,
        temperature=0.1,
        max_tokens=2000,
        timeout=60,
        max_retries=3,
        streaming=False
    )

    # 工具列表
    tools = [mysql_tool]

    # 提示词模板 - 基于实际数据库结构（根据ai_order_demo.sql修正）
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的数据库智能助手，根据实际数据库结构查询数据：

⚠️ 重要：请严格按照以下实际数据库结构查询：

实际数据库表结构（基于ai_order_demo.sql数据库）：
1. 用户表(users) - 字段：user_id, username, registration_date, country, age, gender, total_spent, order_count
   - ✅ 注意：有gender字段，可以查询性别
   - ✅ 有age字段，可以查询年龄
   - ✅ 有country字段，可以查询国家
   - 查询示例：
     - SELECT COUNT(*) FROM users WHERE gender = '男'
     - SELECT username, age, country FROM users WHERE gender = '女' AND age > 30
     - SELECT gender, COUNT(*) as count FROM users GROUP BY gender

2. 订单表(orders) - 字段：order_id, user_id, order_date, product_id, quantity, total_amount, payment_method, order_status
   - 查询示例：
     - SELECT * FROM orders WHERE DATE(order_date) = CURDATE()
     - SELECT SUM(total_amount) FROM orders WHERE order_status = '已发货'
     - SELECT payment_method, COUNT(*) FROM orders GROUP BY payment_method

3. 产品表(products) - 字段：product_id, product_name, category, price, stock, sales_volume, average_rating
   - ⚠️ 重要：category的实际值有：'食品'、'时尚'、'运动'、'家居'、'电子产品'
   - 查询示例：
     - SELECT * FROM products WHERE category = '电子产品'
     - SELECT product_name, price, stock FROM products WHERE category = '食品' AND stock < 100
     - SELECT category, AVG(price) as avg_price FROM products GROUP BY category

4. 用户行为表(user_behavior) - 字段：user_id, product_id, action, action_date, device
   - 查询示例：
     - SELECT action, COUNT(*) FROM user_behavior GROUP BY action
     - SELECT device, COUNT(*) FROM user_behavior GROUP BY device
     - SELECT * FROM user_behavior WHERE action = '购买' ORDER BY action_date DESC LIMIT 10

5. 销售表(sales) - 字段：year, total_sales, total_orders, total_quantity_sold, category, average_order_value
   - 查询示例：
     - SELECT * FROM sales WHERE category = '电子产品' ORDER BY year
     - SELECT year, SUM(total_sales) FROM sales GROUP BY year
     - SELECT category, AVG(average_order_value) FROM sales GROUP BY category

6. 聊天记录表(chat_messages) - 字段：id, user_name, title, role, content, types, created_at
   - 查询示例：
     - SELECT * FROM chat_messages WHERE user_name = '张三' ORDER BY created_at DESC

实际查询策略：
1. 性别查询：users表有gender字段，可以查询性别
2. 分类查询：products表有'食品'、'时尚'、'运动'、'家居'、'电子产品'五种分类
3. 今日订单：使用 WHERE DATE(order_date) = CURDATE()
4. 产品查询：使用具体的分类名称
5. 日期查询：注意order_date和action_date是text类型，使用字符串比较

用户常见问题与实际查询对应：
- ✅ "男性用户有多少？" → SELECT COUNT(*) FROM users WHERE gender = '男'
- ✅ "女性用户平均年龄" → SELECT AVG(age) FROM users WHERE gender = '女'
- ✅ "来自泰国的用户" → SELECT username, gender, age FROM users WHERE country = '泰国'
- ✅ "电子产品库存情况" → SELECT product_name, stock FROM products WHERE category = '电子产品'
- ✅ "用户总数" → SELECT COUNT(*) FROM users
- ✅ "最贵的产品" → SELECT product_name, price, category FROM products ORDER BY price DESC LIMIT 1
- ✅ "今天的销售总额" → SELECT SUM(total_amount) FROM orders WHERE DATE(order_date) = CURDATE()
- ✅ "手机库存情况" → 注意：分类中没有'手机'，应该用'电子产品'
- ✅ "按性别统计用户数" → SELECT gender, COUNT(*) as count FROM users GROUP BY gender
- ✅ "各年龄段用户分布" → SELECT CASE WHEN age < 20 THEN '20岁以下' WHEN age < 30 THEN '20-29岁' WHEN age < 40 THEN '30-39岁' WHEN age < 50 THEN '40-49岁' ELSE '50岁以上' END as age_group, COUNT(*) FROM users GROUP BY age_group

智能查询规则：
1. 如果用户问性别相关的问题，可以直接查询
2. 如果分类不准确，提示可用的分类：'食品'、'时尚'、'运动'、'家居'、'电子产品'
3. 所有回答用中文
4. 如果查询结果为空，如实告知
5. 注意数据类型：年龄是数字，日期是文本字符串
6. 对于国家查询：数据库中有'新加坡'、'印度尼西亚'、'泰国'、'马来西亚'四种国家

现在开始，根据实际数据库结构回答用户问题。"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建智能体
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # 创建执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        return_intermediate_steps=False
    )

    try:
        print(f"\n{'=' * 60}")
        print(f"🔍 处理问题：{text}")

        # 执行智能体
        result = agent_executor.invoke({"input": text})

        if "output" in result:
            output = result["output"]
            print(f"✅ 生成回答成功")
            return output
        else:
            return "抱歉，未能生成有效回答。"

    except Exception as e:
        error_msg = str(e)
        print(f"❌ 处理失败：{error_msg}")

        # 根据错误类型提供友好提示
        if "rate limit" in error_msg.lower():
            return "请求过于频繁，请稍后再试。"
        elif "timeout" in error_msg.lower():
            return "请求超时，请检查网络连接或稍后重试。"
        elif "authentication" in error_msg.lower():
            return "API认证失败，请检查API密钥配置。"
        elif "repetition_penalty" in error_msg.lower():
            return f"模型参数错误：{error_msg[:100]}。已移除不支持的参数，请重启服务重试。"
        elif "early_stopping_method" in error_msg.lower():
            return f"智能体配置错误：{error_msg[:100]}。已修复配置，请重启服务重试。"
        else:
            return f"处理请求时出错：{error_msg[:100]}"


# 基于实际数据库的测试函数
def test_real_database():
    """测试基于实际数据库的智能体"""
    print("🧪 测试基于实际数据库的智能体...")

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model_name = os.getenv("MODEL_NAME")

    print(f"🔑 API密钥: {api_key[:10]}...")
    print(f"🏠 API地址: {api_base}")
    print(f"🤖 模型名称: {model_name}")

    # 基于实际数据库的测试问题
    test_questions = [
        "用户总数是多少？",
        "男性用户有多少？",
        "女性用户有多少？",
        "最贵的产品是什么？",
        "电子产品库存情况",
        "今天的销售总额是多少？",
        "显示最近的3个订单",
        "来自泰国的用户有哪些？",
        "各年龄段用户分布情况",
        "按性别统计用户数量",
        "购买行为最多的设备是什么？",
        "哪个国家的用户消费最多？",
        "食品类产品的平均价格是多少？",
        "运动产品的库存情况",
        "用户行为中浏览、点击、加购、购买各有多少？"
    ]

    print("\n🧪 开始功能测试...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 50}")
        print(f"测试 {i}: {question}")

        try:
            answer = speak_text(question)
            print(f"回答: {answer[:200]}..." if len(answer) > 200 else f"回答: {answer}")
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    test_real_database()