import pymysql
import json
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import inspect

class SqlArgs(BaseModel):
    sql: str = Field(..., description="SQL查询语句")


@tool(args_schema=SqlArgs)
def mysql_tool(sql: str) -> str:
    """
    执行SQL查询语句，智能适配不同调用者。
    支持的表：orders, users, products, user_behavior, sales
    """
    # 检查是否以SQL关键字开头
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith(
            ('SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE ', 'ALTER ', 'DROP ', 'SHOW ', 'DESC ')):
        print(f"⚠️ 跳过非SQL语句: {sql[:100]}...")
        return "错误：不是有效的SQL语句"

    # 检查是否包含中文字符
    if '主要发现' in sql or '核心洞察' in sql or '详细分析' in sql:
        print(f"⚠️ 跳过报告内容: {sql[:100]}...")
        return "错误：检测到报告内容，请勿作为SQL执行"

    # 自动检测调用者
    caller_name = detect_caller()

    # 根据调用者决定返回格式
    if caller_name == "echarts_agent":
        return execute_query_with_format(sql, "json")
    else:
        return execute_query_with_format(sql, "legacy")


def detect_caller() -> str:
    """
    自动检测调用者
    """
    try:
        stack = inspect.stack()
        for frame_info in stack[1:]:  # 跳过自身
            filename = frame_info.filename.lower()
            if "echarts_agent" in filename:
                return "echarts_agent"
            elif "docx_agent" in filename:
                return "docx_agent"
            elif "chat_agent" in filename:
                return "chat_agent"
    except:
        pass
    return "other"


def execute_query_with_format(sql: str, format_type: str = "legacy") -> str:
    """
    执行查询并返回指定格式
    """
    conn = None
    cursor = None
    try:

        # 1. 检查是否是SQL语句
        sql_lower = sql.strip().lower()
        if not sql_lower.startswith('select'):
            return format_error("仅支持SELECT查询语句", format_type)

        # 2. 检查是否包含明显的错误消息或非SQL内容
        error_indicators = [
            "error:", "exception:", "traceback:",
            "access denied", "arrearage", "you have an error",
            "{", "}", ":", "''", "'{"
        ]
        for indicator in error_indicators:
            if indicator in sql_lower:
                return format_error(f"检测到非SQL内容: {sql[:100]}...", format_type)

            # 3. 检查SQL长度和格式
        if len(sql) > 10000:  # SQL过长
            return format_error("SQL语句过长", format_type)

            # 4. 检查是否有明显的注入特征
        injection_indicators = [";--", ";#", "union select", "information_schema", "sleep("]
        for indicator in injection_indicators:
            if indicator in sql_lower:
                return format_error("检测到潜在的SQL注入风险", format_type)

        for indicator in error_indicators:
            if indicator in sql_lower:
                return format_error(f"检测到非SQL内容: {sql[:100]}...", format_type)

        # 数据库连接
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Dnttkl1220!",
            db="0113",
            port=3306,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

        cursor = conn.cursor()

        # 安全检查：只允许SELECT查询
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            return format_error("仅支持SELECT查询语句", format_type)

        # 防止恶意SQL
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return format_error(f"不允许执行{keyword}操作", format_type)

        # 执行查询
        cursor.execute(sql)

        # 获取列名
        columns = [desc[0] for desc in cursor.description]

        # 获取数据
        results = cursor.fetchall()

        if not results:
            return format_empty_result(format_type)

        # 格式化结果
        formatted_results = []
        for row in results:
            formatted_row = {}
            for col in columns:
                value = row[col]
                # 处理特殊类型
                if isinstance(value, (bytes, bytearray)):
                    value = str(value, 'utf-8', errors='ignore')
                elif hasattr(value, 'isoformat'):  # 日期时间类型
                    value = value.isoformat()
                formatted_row[col] = value
            formatted_results.append(formatted_row)

        # 限制返回结果数量
        max_results = 100
        if len(formatted_results) > max_results:
            message = f"查询到 {len(formatted_results)} 条记录，显示前{max_results}条"
            formatted_results = formatted_results[:max_results]
        else:
            message = f"查询结果（共{len(formatted_results)}条）"

        # 根据format_type返回不同格式
        return format_result(formatted_results, message, format_type)

    except pymysql.Error as e:
        return format_error(f"数据库错误：{str(e)}", format_type)
    except Exception as e:
        return format_error(f"执行错误：{str(e)}", format_type)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def format_error(message: str, format_type: str) -> str:
    """格式化错误信息"""
    if format_type == "json":
        return json.dumps({
            "status": "error",
            "message": message
        }, ensure_ascii=False)
    else:
        return f"错误：{message}"


def format_empty_result(format_type: str) -> str:
    """格式化空结果"""
    if format_type == "json":
        return json.dumps({
            "status": "success",
            "count": 0,
            "message": "查询结果为空",
            "data": []
        }, ensure_ascii=False)
    else:
        return "查询结果为空"


def format_result(data: list, message: str, format_type: str) -> str:
    """格式化查询结果"""
    if format_type == "json":
        result = {
            "status": "success",
            "count": len(data),
            "message": message,
            "data": data
        }
        return json.dumps(result, ensure_ascii=False)
    else:
        return f"{message}：\n{data}"


# 兼容性函数
def mysql_tool_legacy(sql: str) -> str:
    """强制返回旧版格式"""
    return execute_query_with_format(sql, "legacy")


def mysql_tool_json(sql: str) -> str:
    """强制返回JSON格式"""
    return execute_query_with_format(sql, "json")


if __name__ == "__main__":
    # 测试函数
    test_sql = "SELECT p.category, SUM(o.total_amount) AS total_sales FROM orders o JOIN products p ON o.product_id = p.product_id GROUP BY p.category"

    print("测试自动检测调用者:")

    print("\n1. 模拟echarts_agent调用:")
    # 模拟echarts_agent调用
    print(mysql_tool_json(test_sql)[:200] + "...")

    print("\n2. 模拟docx_agent调用:")
    # 模拟docx_agent调用
    print(mysql_tool_legacy(test_sql)[:200] + "...")
