\# 智能数据库分析助手

基于 LangChain + FastAPI + Vue 的智能对话系统，支持自然语言查询数据库、生成分析报告、图表可视化等功能。

\# 核心功能

功能        描述                    示例

智能问答    自然语言查询数据库       "查询所有男性用户"、"最贵的产品是什么"

图表生成    自动生成ECharts图表      "用饼图展示各产品类别销量"

Word报告    生成Word格式分析报告     "生成2025年销售分析报告"

PDF报告     生成PDF格式专业报告      "生成支付方式分析PDF报告"

邮箱验证    验证码登录功能           邮箱验证码登录

\# 技术栈

\## 后端

 **Python 3.9+** / **FastAPI**  Web框架

 **LangChain**                  AI应用框架

 **OpenAI API**                 (通义千问 qwen-plus)  大语言模型

 **PyMySQL**                    MySQL数据库连接

 **Redis**                      验证码存储

 **ReportLab**                  PDF生成

 **python-docx**                Word文档生成

 ## 前端

 **Vue 2**                      渐进式JavaScript框架

 **Element UI**                 桌面端组件库

 **ECharts**                    数据可视化

 **Axios**                      HTTP请求

 **Marked**                     Markdown渲染

 ## 数据库

 **MySQL 8.0**                  业务数据存储

 **Redis**                      验证码缓存

\# 项目根目录/

├── backend/ # 后端代码

│ ├── app/

│ │ ├── ai/

│ │ │ ├── agent/ # AI智能体

│ │ │ │ ├── chat_agent.py # 问答智能体

│ │ │ │ ├── echarts_agent.py # 图表智能体

│ │ │ │ ├── pdf_agent.py # PDF报告智能体

│ │ │ │ ├── docx_agent.py # Word报告智能体

│ │ │ │ ├── email_agent.py # 邮件智能体

│ │ │ │ └── music_agent.py # 音乐播放智能体

│ │ │ └── tool/ # 工具函数

│ │ │ ├── mysql_tool.py # 数据库查询工具

│ │ │ ├── pdf_tool.py # PDF生成工具

│ │ │ ├── docx_tool.py # Word生成工具

│ │ │ ├── email_tool.py # 邮件发送工具

│ │ │ └── music_tool.py # 音乐播放工具

│ │ ├── api/

│ │ │ ├── router/ # API路由

│ │ │ │ ├── chat_router.py # 聊天接口

│ │ │ │ └── login_router.py # 登录接口

│ │ │ └── schema/ # 数据模型

│ │ │ ├── ChatArgs.py

│ │ │ └── EmailArgs.py

│ │ └── main.py # 后端入口

│ ├── static/

│ │ └── download/ # 生成的报告文件

│ ├── .env # 环境变量配置

│ └── requirements.txt # Python依赖

│

└── frontend/ # 前端代码

├── src/

│ ├── assets/

│ │ └── image/ # 图片资源

│ │ ├── bj.jpg # 背景图

│ │ ├── bot.jpg # 机器人头像

│ │ └── user.jpg # 用户头像

│ ├── components/

│ │ └── page/

│ │ ├── AuthPage.vue # 认证页面

│ │ ├── Chat.vue # 聊天主页面

│ │ ├── Login.vue # 登录组件

│ │ └── Register.vue # 注册组件

│ ├── router/

│ │ └── index.js # 路由配置

│ ├── App.vue # 根组件

│ └── main.js # 入口文件

├── index.html

├── package.json

└── login.css # 登录样式

\# 数据库结构

\## 用户表 (users)

CREATE TABLE users (

​    user_id INT PRIMARY KEY,

​    username VARCHAR(50),

​    registration_date DATE,

​    country VARCHAR(50),      -- 新加坡、马来西亚、泰国、印度尼西亚

​    age INT,

​    gender VARCHAR(10),       -- 男、女

​    total_spent DECIMAL(10,2),

​    order_count INT

);

\## 订单表 (orders)

CREATE TABLE orders (

​    order_id INT PRIMARY KEY,

​    user_id INT,

​    order_date DATE,

​    product_id INT,

​    quantity INT,

​    total_amount DECIMAL(10,2),

​    payment_method VARCHAR(50),   -- 信用卡、支付宝、微信支付、PayPal、借记卡

​    order_status VARCHAR(20)      -- 待发货、已发货、配送中、已取消

);

\## 其他表

user_behavior - 用户行为表（浏览、点击、加购、购买）

sales - 销售统计表

chat_messages - 聊天记录表

employer - 登陆系统的人员记录表

products - 产品表

\# 快速开始

\## 环境要求

Python 3.9+

Node.js 14+

MySQL 8.0

Redis

\## 后端启动

进入后端目录

cd backend

Windows系统激活已有虚拟环境

myenv\Scripts\activate

启动后端

python main.py

\## 配置环境变量

创建 .env 文件：

API配置

OPENAI_API_KEY=xxxxxxxxx

OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

MODEL_NAME=qwen-plus

邮件配置

email_host=smtp.qq.com

email_user=xxxxxxxxx@qq.com

email_password=xxxxxxxxxx

Vosk语音模型路径

vosk_model_path=D:\\vosk-model-cn-0.22\\vosk-model-cn-0.22

\##  初始化数据库

conn = pymysql.connect(

​    host="localhost",

​    user="root",

​    password="xxxxxxxxx",    

​    db="0113",

​    port=3306,

​    charset="utf8mb4"

)

\## 启动后端服务

python main.py

后端服务运行在：http://localhost:8000

\## 前端启动

cd frontend

安装依赖

npm install

启动开发服务器

npm run dev

前端服务运行在：http://localhost:8080

\## 访问应用

打开浏览器访问：http://localhost:8080

\# 使用示例

\## 智能问答

输入                        输出

"用户总数是多少？"           返回用户总数

"男性用户有多少？"           返回男性用户数量

"最贵的产品是什么？"         返回最贵的产品信息

"来自泰国的用户有哪些？"     返回泰国用户列表

"今天的销售总额是多少？"     返回今日销售额

\## 图表生成

输入                                             输出

"用饼图展示各产品类别销量占比"                     生成饼图

"各国家用户数量对比，用柱状图表呈现"               生成柱状图

"不同年龄段用户的消费金额分布，请用折线图表呈现"    生成折线图

\## 报告生成

输入                                  输出

"生成2025年销售分析报告"               Word报告下载链接

"分析电子产品类别的年度销售趋势报告"    Word报告下载链接

"生成支付方式使用情况分析PDF报告"       PDF报告下载链接

\# 配置说明

\## 数据库配置

在 backend/app/ai/tool/mysql_tool.py 中修改：

conn = pymysql.connect(

​    host="localhost",      # 数据库地址

​    user="root",           # 用户名

​    password="xxxxxxxx", # 密码   

​    db="0113",             # 数据库名

​    port=3306

)

\## Redis配置

在 backend/app/api/router/login_router.py 中修改：

redis_client = redis.StrictRedis(

​    host='localhost',

​    port=6379,

​    db=0,

​    decode_responses=True  # 自动解码

)

\## 文件存储路径

生成的报告文件保存在：backend/static/download/

访问链接：http://localhost:8000/static/download/文件名

\# 常见问题

Q: 后端启动报错 "ModuleNotFoundError"

A: 安装缺失的依赖：

pip install -r requirements.txt

Q: 数据库连接失败

A:

检查MySQL服务是否启动

确认用户名密码正确

确认数据库 0113 已创建

Q: Redis连接失败

A:

启动Redis服务

redis-server.exe

Q: 邮件发送失败

A:

确认邮箱已开启SMTP服务

使用授权码而非登录密码

检查邮箱服务器配置

Q: 图表不显示

A:

打开浏览器控制台(F12)查看错误

确认返回的是有效的JSON格式

检查ECharts配置是否正确

Q: 前端报跨域错误

A:

确认后端已启动

检查 main.js 中的API地址

\## 更新日志

初始版本发布

智能问答功能

ECharts图表生成

Word/PDF报告生成

邮箱验证码登录

音乐播放功能

Made with  by 杨丹妮