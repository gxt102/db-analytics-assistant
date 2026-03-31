from collections import defaultdict
from fastapi import APIRouter
from app.api.schema.ChatArgs import ChatArgs
from app.ai.agent.chat_agent import speak_text
from app.ai.agent.docx_agent import speak_docx
from app.ai.agent.pdf_agent import speak_pdf  # 新增导入
from app.ai.agent.echarts_agent import speak_echarts
import pymysql
import json

chat_router = APIRouter()


@chat_router.post("/chat")
def chat(args: ChatArgs):
    print("参数", args)

    # 判断问题类型并调用相应智能体
    if "报告" in args.question and "PDF" in args.question:
        answer = speak_pdf(args.question)  # 调用PDF智能体
        sql = (f"insert into chat_messages (user_name,title,role,content,types) values "
               f"('{args.userName}','{args.title}','user','{args.question}','text'),"
               f"('{args.userName}','{args.title}','assistant','{answer}','pdf')")  # 类型改为pdf
        iss = mysql_tool(sql)
        return {"code": 200, "msg": "success", "data": answer, "type": "pdf"}
    elif "报告" in args.question:
        answer = speak_docx(args.question)
        sql = (f"insert into chat_messages (user_name,title,role,content,types) values "
               f"('{args.userName}','{args.title}','user','{args.question}','text'),"
               f"('{args.userName}','{args.title}','assistant','{answer}','text')")
        iss = mysql_tool(sql)
        return {"code": 200, "msg": "success", "data": answer, "type": "text"}
    elif "图表" in args.question:
        try:
            answer = speak_echarts(args.question)
            # 验证返回的是否是有效的JSON
            try:
                # 尝试解析为JSON
                json.loads(answer)
                # 如果成功，说明是有效的图表JSON
                chart_data = answer
            except json.JSONDecodeError:
                # 如果不是JSON，可能是错误信息
                print(f"图表生成返回了非JSON数据: {answer[:200]}...")
                # 生成一个错误提示图表
                chart_data = generate_error_chart("图表生成失败", answer[:100])

            sql = (f"insert into chat_messages (user_name,title,role,content,types) values "
                   f"('{args.userName}','{args.title}','user','{args.question}','text'),"
                   f"('{args.userName}','{args.title}','assistant','{chart_data}','chart')")
            iss = mysql_tool(sql)
            return {"code": 200, "msg": "success", "data": chart_data, "type": "chart"}
        except Exception as e:
            print(f"图表生成异常: {e}")
            # 生成错误图表
            error_chart = generate_error_chart("图表生成异常", str(e)[:100])
            sql = (f"insert into chat_messages (user_name,title,role,content,types) values "
                   f"('{args.userName}','{args.title}','user','{args.question}','text'),"
                   f"('{args.userName}','{args.title}','assistant','{error_chart}','chart')")
            iss = mysql_tool(sql)
            return {"code": 200, "msg": "success", "data": error_chart, "type": "chart"}
    else:
        answer = speak_text(args.question)
        sql = (f"insert into chat_messages (user_name,title,role,content,types) values "
               f"('{args.userName}','{args.title}','user','{args.question}','text'),"
               f"('{args.userName}','{args.title}','assistant','{answer}','text')")
        iss = mysql_tool(sql)
        return {"code": 200, "msg": "success", "data": answer, "type": "text"}


def generate_error_chart(title, message):
    """生成错误提示图表"""
    error_config = {
        "title": {
            "text": title,
            "subtext": message,
            "left": "center",
            "textStyle": {
                "fontSize": 18,
                "color": "#f56c6c"
            }
        },
        "graphic": [{
            "type": "text",
            "left": "center",
            "top": "40%",
            "style": {
                "text": "图表渲染失败",
                "font": "bold 24px Microsoft YaHei",
                "fill": "#f56c6c"
            }
        }, {
            "type": "text",
            "left": "center",
            "top": "55%",
            "style": {
                "text": "建议重试或联系管理员",
                "font": "14px Microsoft YaHei",
                "fill": "#909399"
            }
        }],
        "toolbox": {
            "feature": {
                "saveAsImage": {
                    "title": "保存为图片",
                    "type": "png"
                }
            }
        }
    }
    return json.dumps(error_config, ensure_ascii=False)


# 增删改
def mysql_tool(sql: str) -> bool:
    """
    执行sql语句
    """
    try:
        # 1 创建一个数据库连接
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Dnttkl1220!",
            db="0113",
            port=3306,
            charset="utf8mb4"  # 改为utf8mb4支持更广字符
        )
        # 2 创建一个游标对象
        cursor = conn.cursor()
        # 3 执行sql语句
        cursor.execute(sql)
        # 4 执行增删改,需提交事务
        conn.commit()
        # 获取执行结果
        num = cursor.rowcount
        if num > 0:
            print("插入成功")
            # 5 关闭数据库连接
            cursor.close()
            conn.close()
            return True
        else:
            print("插入失败")
            # 5 关闭数据库连接
            cursor.close()
            conn.close()
            return False
    except Exception as e:
        print(f"数据库操作错误: {e}")
        return False


# 定义一个查询聊天的接口
@chat_router.get("/query")
def query(userName: str):
    sql = f"select * from chat_messages where user_name = '{userName}' order by id asc"
    try:
        conn = pymysql.connect(host="localhost", user="root", password="Dnttkl1220!", db="0113", port=3306,
                               charset="utf8mb4")
        cursor = conn.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        cursor.close()
        conn.close()

        # 正确构建数据结构
        new_list = []
        for x in rs:
            d = {
                "id": x[0],
                "user_name": x[1],
                "title": x[2],
                "role": x[3],
                "content": x[4],
                "type": x[5]
            }
            new_list.append(d)

        # 使用 build_chat_list 构建聊天结构
        data = build_chat_list(new_list)
        return {"code": 200, "msg": "success", "data": data}
    except Exception as e:
        print(f"查询聊天记录错误: {e}")
        return {"code": 500, "msg": "查询失败", "data": []}


# 构建聊天列表
def build_chat_list(records):
    chat_map = defaultdict(list)
    for r in records:
        # 直接使用数据库主键作为消息ID，保持一致性
        message_id = str(r['id'])  # 直接使用数据库主键

        # 处理图表消息：确保content是字符串格式
        content = r["content"]
        if r["type"] == "chart":
            if isinstance(content, dict):
                content = json.dumps(content, ensure_ascii=False)
            # 确保图表数据是有效的JSON字符串
            elif isinstance(content, str):
                try:
                    # 如果是字符串，尝试解析再序列化以确保格式正确
                    json.loads(content)
                except:
                    # 如果不是JSON，保持原样
                    pass

        chat_map[r["title"]].append({
            "id": message_id,  # 使用数据库主键
            "role": r["role"],
            "content": content,
            "type": r["type"]
        })

    # 按时间顺序排序（假设id越大越新）
    for title in chat_map:
        chat_map[title] = sorted(chat_map[title], key=lambda x: int(x['id']))

    chat_list = []
    for i, (title, msgs) in enumerate(chat_map.items(), start=1):
        chat_list.append({
            "id": str(i),
            "title": title,
            "messages": msgs
        })

    # 按最新的对话排序
    chat_list.sort(key=lambda x: max([int(m['id']) for m in x['messages']]) if x['messages'] else 0, reverse=True)

    return chat_list