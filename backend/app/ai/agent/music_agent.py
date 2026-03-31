from dotenv import load_dotenv  #读取配置
from langchain_openai import ChatOpenAI #聊天模型
import os #系统内置
from app.ai.tool.music_tool import play_music,stop_music
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.agents import create_tool_calling_agent,AgentExecutor

def speak_music(text):
    # 第一步: 创建一个大模型
    # 加载配置
    load_dotenv()
    # 创建一个聊天模型
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"))

    # 第二步: 创建一个工具:给大模型注册一个工具
    tool = [play_music, stop_music]

    # 第三步: 创建一个提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是一个音乐播放助手, 你有两个工具: play_music，stop_music
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
    return rs["output"]