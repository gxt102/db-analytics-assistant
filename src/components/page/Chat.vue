<template>
<el-container>
  <el-header>
    <el-row>
      <el-col :span="8"><h1>智能数据库分析助手</h1></el-col>
      <el-col :span="8">&nbsp;</el-col>
      <el-col :span="8" align="right" style="padding-top: 9px">
        <el-button type="primary" @click="testApiConnection" :loading="testingApi">测试API连接</el-button>
        <el-button type="success" @click="logout">退出登录</el-button>
      </el-col>
    </el-row>
  </el-header>

  <el-container>
    <!-- 侧边栏 -->
    <el-aside width="260px">
      <div align="center">
        <br>
        <el-button type="primary" icon="el-icon-plus" @click="newChat">新对话</el-button>
      </div>
      <hr>

      <!-- 快捷提问栏 -->
      <div class="quick-questions-bar" v-if="chatList.length > 0">
        <div class="quick-questions-label">常用查询：</div>
        <div class="quick-questions-buttons">
          <el-button
            v-for="(question, index) in quickQuestions"
            :key="index"
            size="mini"
            @click="askQuickQuestion(question)"
            class="quick-question-btn"
          >
            {{ question }}
          </el-button>
        </div>
      </div>

      <el-menu :default-active="activeChatId" @select="selectChat">
        <el-menu-item
          v-for="chat in chatList"
          :key="chat.id"
          :index="chat.id"
        >
          <i class="el-icon-message"></i>
          <span slot="title">
            {{ chat.title ? (chat.title.length > 10 ? chat.title.substring(0,10)+'...' : chat.title) : '新对话' }}
            <el-button
              type="text"
              size="small"
              icon="el-icon-delete"
              @click.stop="deleteChat(chat.id)"
              style="float:right;margin-right:-10px;"
            ></el-button>
          </span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button type="text" @click="clearHistory" style="width:100%;color:#999;">
          <i class="el-icon-delete"></i> 清空历史
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-main>
        <!-- 聊天头部 -->
        <div class="chat-header" v-if="currentChat.title">
          <h3>{{ currentChat.title }}</h3>
          <span class="message-count">{{ currentChat.messages.length }} 条消息</span>
        </div>

        <div class="messages-container">
          <div v-for="message in currentChat.messages"
               :key="message.id"
               :class="['chat-message', message.role]">

            <!-- 头像和时间 -->
            <div class="message-header">
              <el-avatar :src="message.role === 'user' ? userAvatar : botAvatar" size="small"></el-avatar>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>

            <!-- 消息内容 -->
            <div class="message-content">
              <!-- 文本消息 -->
              <div v-if="message.type==='text' || message.type==='pdf'"
                   class="bubble"
                   v-html="formatMessage(message.content)">
              </div>

              <!-- 图表消息 -->
              <div v-if="message.type==='chart' && message.role==='assistant'"
                   :id="`chart-${message.id}`"
                   style="width: 800px;height: 300px"
                   class="bubble">
              </div>


              <div v-if="message.file" class="file-preview">
                <div class="file-info">
                  <span class="file-icon">{{ getFileIcon(message.file.type) }}</span>
                  <div class="file-details">
                    <p class="file-name">{{ message.file.name }}</p>
                    <p class="file-size">{{ formatFileSize(message.file.size) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 正在思考提示 -->
          <div v-show="loading" class="chat-message assistant">
            <div class="message-header">
              <el-avatar :src="botAvatar" size="small"></el-avatar>
              <span class="message-time">{{ formatTime(new Date()) }}</span>
            </div>
            <div class="message-content">
              <div class="bubble typing-indicator">
                <div class="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="typing-text">正在思考中...</span>
              </div>
            </div>
          </div>
        </div>
      </el-main>

<el-footer>
  <!-- 输入区域 -->
  <div class="input-area">
    <el-form :inline="false">
      <el-form-item>
        <el-input
          type="textarea"
          v-model="inputMessage"
          :rows="3"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.enter.shift.exact.prevent="handleShiftEnter"
          placeholder="输入问题... 例如：查询所有用户、最贵的产品是什么、今天的订单统计（按 Enter 发送，Shift + Enter 换行）"
          resize="none"
          class="chat-input"
        ></el-input>
      </el-form-item>

      <el-form-item class="input-actions">
        <div class="action-buttons">
          <el-button
            type="primary"
            @click="sendMessage"
            :disabled="!inputMessage.trim() || loading"
            :loading="loading"
            class="send-btn"
          >
            <i class="el-icon-s-promotion"></i>
            发送
          </el-button>

          <el-button
            type="success"
            @click="exportChat"
            :disabled="currentChat.messages.length === 0"
            class="export-btn"
          >
            <i class="el-icon-download"></i>
            导出聊天
          </el-button>
        </div>

        <div class="input-footer">
          <span class="hint-text">
            <i class="el-icon-info"></i>
            Shift + Enter 换行，Enter 发送
          </span>
        </div>
      </el-form-item>
    </el-form>
  </div>
</el-footer>
    </el-container>
  </el-container>
</el-container>
</template>

<script>
import {marked} from 'marked'
import DOMPurify from 'dompurify'
import * as echarts from 'echarts';

export default {
  name: "Chat",
  data(){
    return {
      isChat: false,
      loading: false,
      testingApi: false,
      inputMessage: "",
      userAvatar: require('@/assets/image/user.jpg'),
      botAvatar: require('@/assets/image/bot.jpg'),
      activeChatId: "1",
      chatList: [],

      // 快捷问题列表
      quickQuestions: [
        '各国家市场表现对比分析报告',
        '分析电子产品类别的年度销售趋势报告',
        '库存优化与补货策略分析报告',
        '展示各产品类别的销量占比,请用饼图表呈现',
        '不同年龄段用户的消费金额分布，请用折线图表呈现',
        '各国家用户数量对比，用柱状图表呈现',
        '业务风险与机会评估PDF报告',
        '产品线盈利能力分析PDF报告',
        '资源配置优化建议PDF报告',
        '来自泰国的用户有哪些？',
        '按性别统计用户数量',
        '哪个国家的用户消费最多？'
      ]
    }
  },
  computed: {
    currentChat() {
      return this.chatList.find(x => x.id === this.activeChatId) || {"messages": [], "title": "新对话"};
    }
  },
  mounted() {
    this.loadChatHistory();
  },
  watch: {
    currentChat: {
      handler(newVal) {
        if (newVal && newVal.messages) {
          this.$nextTick(() => {
            setTimeout(() => {
              this.renderAllCharts();
            }, 300);
          });
        }
      },
      deep: true,
      immediate: true
    },
    chatList: {
      handler() {
        this.$nextTick(() => {
          setTimeout(() => {
            this.renderAllCharts();
          }, 300);
        });
      },
      deep: true
    }
  },
  methods: {
    // 在 methods 中添加
  handleShiftEnter() {
  // 在文本中插入换行符
  const textarea = document.querySelector('.chat-input textarea');
  if (textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    // 在光标位置插入换行符
    this.inputMessage =
      this.inputMessage.substring(0, start) +
      '\n' +
      this.inputMessage.substring(end);

    // 更新光标位置
    this.$nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 1;
      textarea.focus();
    });
  }
},
    // 渲染所有图表
    renderAllCharts() {
      this.currentChat.messages.forEach((message, index) => {
        if (message.type === 'chart' && message.role === 'assistant' && message.content) {
          setTimeout(() => {
            this.renderExistingChart(message.id, message.content);
          }, 50 * (index + 1));
        }
      });
    },

    // 渲染已保存的图表
    renderExistingChart(messageId, data) {
      setTimeout(() => {
        const chartElement = document.getElementById('chart-' + messageId);
        if (!chartElement) {
          setTimeout(() => {
            const retryElement = document.getElementById('chart-' + messageId);
            if (retryElement) {
              this.renderExistingChart(messageId, data);
            }
          }, 100);
          return;
        }

        try {
          if (chartElement._chartInstance) {
            chartElement._chartInstance.dispose();
          }

          let chartConfig;
          try {
            if (typeof data === 'string') {
              chartConfig = JSON.parse(data);
            } else {
              chartConfig = data;
            }
          } catch (e) {
            const jsonMatch = data.toString().match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              try {
                chartConfig = JSON.parse(jsonMatch[0]);
              } catch (parseError) {
                console.error('提取JSON也失败:', parseError);
                return;
              }
            } else {
              console.error('没有找到JSON数据');
              return;
            }
          }

          const myChart = echarts.init(chartElement);
          myChart.setOption(chartConfig);

          chartElement._chartInstance = myChart;

          window.addEventListener('resize', () => {
            myChart.resize();
          });

        } catch (error) {
          console.error('恢复图表失败:', error);
          chartElement.innerHTML = `
            <div style="
              color: #f56c6c;
              background: #fef0f0;
              border: 1px solid #fbc4c4;
              border-radius: 4px;
              padding: 20px;
              text-align: center;
            ">
              <i class="el-icon-warning" style="font-size: 24px; margin-bottom: 10px;"></i>
              <div>图表渲染失败</div>
              <div style="font-size: 12px; color: #999; margin-top: 10px;">
                错误: ${error.message}<br>
                图表ID: ${messageId}
              </div>
            </div>
          `;
        }
      }, 50);
    },

    selectChat(id) {
      this.activeChatId = id;
    },

    newChat() {
      const id = new Date().getTime().toString();
      const chat = {
        "id": id,
        "title": "新对话",
        "messages": [],
        "timestamp": new Date()
      };
      this.chatList.push(chat);
      this.activeChatId = id;
      this.isChat = true;
    },

    showEcharts(data) {
      const id = new Date().getTime();
      const reply = {
        "id": id,
        role: "assistant",
        content: data,
        type: "chart",
        timestamp: new Date()
      };

      this.currentChat.messages.push(reply);

      this.$nextTick(() => {
        setTimeout(() => {
          const chartElement = document.getElementById('chart-' + id);
          if (!chartElement) {
            console.error('Chart element not found:', 'chart-' + id);
            return;
          }

          try {
            let chartConfig;
            try {
              chartConfig = JSON.parse(data);
            } catch (jsonError) {
              const jsonMatch = data.match(/\{[\s\S]*\}/);
              if (jsonMatch) {
                try {
                  chartConfig = JSON.parse(jsonMatch[0]);
                } catch (e) {
                  throw new Error('无法解析图表配置');
                }
              } else {
                throw new Error('返回的不是有效的图表配置');
              }
            }

            const myChart = echarts.init(chartElement);

            if (!chartConfig.series || !Array.isArray(chartConfig.series)) {
              throw new Error('图表配置缺少series数据');
            }

            myChart.setOption(chartConfig);

            window.addEventListener('resize', () => {
              myChart.resize();
            });

          } catch (error) {
            console.error('图表渲染失败:', error);
            chartElement.innerHTML = `
              <div style="
                color: #f56c6c;
                background: #fef0f0;
                border: 1px solid #fbc4c4;
                border-radius: 4px;
                padding: 20px;
                text-align: center;
              ">
                <i class="el-icon-warning" style="font-size: 24px; margin-bottom: 10px;"></i>
                <div>图表渲染失败</div>
                <div style="font-size: 12px; color: #999; margin-top: 10px;">
                  ${error.message}<br>
                  请尝试更具体的问题描述
                </div>
              </div>
            `;
          }
        }, 100);
      });
    },

    formatMessage(content) {
      return DOMPurify.sanitize(marked.parse(content || ''));
    },

    streamReply(fullText) {
      let i = 0;
      const reply = {
        role: "assistant",
        content: "",
        type: "text",
        timestamp: new Date()
      };

      this.currentChat.messages.push(reply);

      const iv = setInterval(() => {
        if (i < fullText.length) {
          reply.content += fullText[i];
          i++;
          this.$forceUpdate();
        } else {
          clearInterval(iv);
        }
      }, 40);
    },

    sendMessage() {
      if (this.inputMessage === "") return;

      if (this.currentChat.messages.length === 0 && this.isChat === false) {
        this.newChat();
      }

      const id = new Date().getTime();
      const userMessage = {
        "id": id,
        "role": "user",
        "content": this.inputMessage,
        "type": "text",
        "timestamp": new Date()
      };

      this.currentChat.messages.push(userMessage);

      // 如果是第一条消息，设置标题
      if (this.currentChat.messages.length === 1) {
        this.currentChat.title = this.inputMessage.length > 20
          ? this.inputMessage.substring(0, 20) + '...'
          : this.inputMessage;
      }

      this.loading = true;

      const name = localStorage.getItem("chatName");
      const params = {
        "userName": name,
        "title": this.currentChat.title,
        "question": this.inputMessage
      };

      // 清空输入框
      const messageToSend = this.inputMessage;
      this.inputMessage = "";

      this.$http.post("http://localhost:8000/chat", params)
        .then(rs => {
          this.loading = false;

          if (rs.data.code === 200) {
            if (rs.data.type === "text" || rs.data.type === "pdf") {
              this.streamReply(rs.data.data);
            } else if (rs.data.type === "chart") {
              this.showEcharts(rs.data.data);
            } else {
              this.streamReply(rs.data.data);
            }

            // 更新聊天历史
            this.updateChatHistory();
          } else {
            this.$message.error(rs.data.msg || "服务器返回错误");
          }
        })
        .catch(error => {
          this.loading = false;
          console.error('发送消息失败:', error);

          let errorMsg = "抱歉，服务暂时不可用，请稍后再试。";

          if (error.response) {
            errorMsg = `服务器错误: ${error.response.status}`;
          } else if (error.request) {
            errorMsg = "网络连接失败，请检查后端服务是否启动";
          }

          this.streamReply(errorMsg);
          this.$message.error("发送失败");
        });
    },

    loadChatHistory() {
      const userName = localStorage.getItem("chatName");

      this.$http.get("http://localhost:8000/query", {params: {"userName": userName}})
        .then(rs => {
          if (rs.data.code === 200) {
            this.chatList = rs.data.data;
            if (this.chatList.length > 0) {
              this.activeChatId = this.chatList[0].id;
            }
          }
        })
        .catch(error => {
          console.error('加载聊天记录失败:', error);
          // 如果没有历史记录，创建默认对话
          if (this.chatList.length === 0) {
            this.newChat();
          }
        });
    },

    updateChatHistory() {
      // 更新聊天列表中的最后消息
      const chatIndex = this.chatList.findIndex(chat => chat.id === this.activeChatId);
      if (chatIndex > -1 && this.currentChat.messages.length > 0) {
        const lastMessage = this.currentChat.messages[this.currentChat.messages.length - 1];
        this.chatList[chatIndex].lastMessage = lastMessage.content;
      }
    },

    // 1. 快捷提问
    askQuickQuestion(question) {
      this.inputMessage = question;
      this.sendMessage();
    },

    // 2. 测试API连接
    async testApiConnection() {
      this.testingApi = true;

      try {
        // 测试健康检查接口
        const healthResponse = await this.$http.get('http://localhost:8000/health');

        // 测试聊天接口
        const chatResponse = await this.$http.post('http://localhost:8000/chat', {
          question: '测试连接',
          userName: localStorage.getItem("chatName"),
          title: '连接测试'
        });

        this.$message({
          message: `✅ API连接测试成功！\n后端服务正常，数据库连接正常。`,
          type: 'success',
          duration: 5000,
          showClose: true
        });

      } catch (error) {
        let errorMsg = '❌ API连接测试失败\n';

        if (error.response) {
          errorMsg += `错误码: ${error.response.status}\n`;
        } else if (error.request) {
          errorMsg += '未收到服务器响应\n请检查：\n1. 后端服务是否启动\n2. 服务地址: http://localhost:8000\n3. 网络连接';
        } else {
          errorMsg += `错误: ${error.message}\n`;
        }

        this.$message({
          message: errorMsg,
          type: 'error',
          duration: 7000,
          showClose: true
        });
      } finally {
        this.testingApi = false;
      }
    },

    // 3. 导出聊天
    exportChat() {
      if (this.currentChat.messages.length === 0) {
        this.$message.warning('当前对话没有内容可以导出');
        return;
      }

      let content = `=== 聊天记录导出 ===\n`;
      content += `标题: ${this.currentChat.title}\n`;
      content += `导出时间: ${new Date().toLocaleString()}\n`;
      content += `消息总数: ${this.currentChat.messages.length}\n`;
      content += `\n=== 对话内容 ===\n\n`;

      this.currentChat.messages.forEach((message, index) => {
        const sender = message.role === 'user' ? '用户' : 'AI助手';
        const time = this.formatTime(message.timestamp);
        content += `${index + 1}. [${time}] ${sender}:\n`;
        content += `${message.content}\n\n`;
      });

      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      const date = new Date().toISOString().split('T')[0];
      const fileName = `${this.currentChat.title}_${date}.txt`;
      link.download = fileName;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      this.$message.success('聊天记录已导出');
    },

    // 4. 删除对话
    deleteChat(chatId) {
      this.$confirm('确定要删除这个对话吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const index = this.chatList.findIndex(chat => chat.id === chatId);
        if (index > -1) {
          this.chatList.splice(index, 1);
          if (this.activeChatId === chatId && this.chatList.length > 0) {
            this.activeChatId = this.chatList[0].id;
          } else if (this.chatList.length === 0) {
            this.newChat();
          }
          this.$message.success('删除成功');
        }
      });
    },

    // 5. 清空历史
    clearHistory() {
      this.$confirm('确定要清空所有历史对话吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.chatList = [];
        this.newChat();
        this.$message.success('已清空所有历史对话');
      });
    },

    // 6. 退出登录
    logout() {
      this.$confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('chatName');
        this.$router.push('/login');
      });
    },

    // 7. 格式化时间
    formatTime(timestamp) {
      if (!timestamp) return '';
      const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return hours + ':' + minutes;
    },

    // 8. 文件图标和大小格式化
    getFileIcon(fileType) {
      const icons = {
        image: '🖼️',
        video: '🎥',
        audio: '🎵',
        pdf: '📄',
        word: '📝',
        excel: '📊',
        ppt: '📽️',
        archive: '🗜️',
        document: '📄'
      };
      return icons[fileType] || '📎';
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
  }
}
</script>

<style scoped>
.el-header {
  background-color: #B3C0D1;
  color: #333;
  text-align: center;
  line-height: 45px;
  height: 80px;
  padding: 0 20px;
}

.el-header h1 {
  margin: 0;
  font-size: 23px;
  line-height: 80px;
}

.el-footer {
  background-color: #f8f9fa !important;
  padding: 15px 20px !important;
  border-top: 1px solid #e0e0e0;
}

.el-aside {
  background-color: ghostwhite;
  color: #333;
  text-align: center;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
}

.el-main {
  background-color: #E9EEF3;
  color: #333;
  padding: 20px;
  height: calc(100vh - 180px);
  overflow-y: auto;
}

/* 快捷提问栏 */
.quick-questions-bar {
  padding: 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.quick-questions-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
  text-align: left;
}

.quick-questions-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-question-btn {
  padding: 4px 8px;
  font-size: 12px;
  white-space: nowrap;
}

/* 侧边栏底部 */
.sidebar-footer {
  margin-top: auto;
  padding: 10px;
  border-top: 1px solid #e0e0e0;
}

/* 聊天头部 */
.chat-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.chat-header h3 {
  margin: 0 0 5px 0;
  color: #333;
}

.message-count {
  font-size: 12px;
  color: #999;
}

/* 消息容器 */
.messages-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* 消息布局 */
.chat-message {
  display: flex;
  margin-bottom: 25px;
  align-items: flex-start;
}

.chat-message.user {
  flex-direction: row-reverse;
}

/* 消息头部（头像+时间） */
.message-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 80px;
  flex-shrink: 0;
  padding: 0 10px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  white-space: nowrap;
}

/* 消息内容 */
.message-content {
  max-width: 85%;
  min-width: 200px;
}

.user .message-content {
  text-align: right;
}

/* 气泡样式 */
.bubble {
  padding: 15px 20px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  text-align: left;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
}

.user .bubble {
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: #fff;
  border-radius: 18px 18px 0 18px;
}

.assistant .bubble {
  background: white;
  color: #333;
  border: 1px solid #e8e8e8;
  border-radius: 18px 18px 18px 0;
}

.user .bubble::after {
  content: '';
  position: absolute;
  right: -8px;
  top: 15px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 8px solid #337ecc;
}

.assistant .bubble::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 15px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-right: 8px solid white;
}

.assistant .bubble::after {
  content: '';
  position: absolute;
  left: -9px;
  top: 15px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-right: 8px solid #e8e8e8;
}

/* 正在输入指示器 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  background: white;
  border-radius: 18px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.typing-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 文件预览 */
.file-preview {
  margin-top: 10px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.file-info {
  display: flex;
  align-items: center;
}

.file-icon {
  font-size: 24px;
  margin-right: 12px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  word-break: break-all;
}

.file-size {
  font-size: 12px;
  color: #999;
}

.input-area {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e8e8;
}

.chat-input {
  width: 100%;
}

.chat-input >>> .el-textarea__inner {
  font-size: 14px;
  line-height: 1.6;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 12px 16px;
  resize: none;
  transition: all 0.3s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.chat-input >>> .el-textarea__inner:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
  outline: none;
}

.chat-input >>> .el-textarea__inner:hover {
  border-color: #c0c4cc;
}

.input-actions {
  margin-top: 15px;
  margin-bottom: 0 !important;
}

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
}

.send-btn, .export-btn {
  padding: 12px 28px !important;
  font-size: 14px !important;
  border-radius: 8px !important;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.send-btn {
  background: linear-gradient(135deg, #409eff, #337ecc) !important;
  border: none !important;
  min-width: 120px;
}

.send-btn:hover {
  background: linear-gradient(135deg, #337ecc, #2c6bb2) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.send-btn:active {
  transform: translateY(0);
}

.export-btn {
  background: linear-gradient(135deg, #67c23a, #5daf34) !important;
  border: none !important;
  min-width: 120px;
}

.export-btn:hover {
  background: linear-gradient(135deg, #5daf34, #529b2e) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.export-btn:active {
  transform: translateY(0);
}

.input-footer {
  margin-top: 12px;
  text-align: center;
}

.hint-text {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.hint-text i {
  font-size: 14px;
}

/* 表格数据样式 */
.bubble table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  font-size: 13px;
  border: 1px solid #e8e8e8;
}

.bubble th {
  background: #f5f7fa;
  padding: 10px 12px;
  text-align: left;
  border: 1px solid #ebeef5;
  font-weight: 600;
  color: #303133;
}

.bubble td {
  padding: 10px 12px;
  border: 1px solid #ebeef5;
  color: #606266;
}

.bubble tr:nth-child(even) {
  background-color: #fafafa;
}

.bubble tr:hover {
  background-color: #f5f7fa;
}

/* 数值高亮 */
.bubble strong {
  color: #1890ff;
  font-weight: 600;
}

/* 代码块样式 */
.bubble pre {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 12px;
  margin: 8px 0;
  overflow-x: auto;
  border: 1px solid #e1e4e8;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 13px;
}

.bubble code {
  background: #f6f8fa;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 13px;
  color: #e96900;
}

/* 列表样式 */
.bubble ul, .bubble ol {
  margin: 8px 0;
  padding-left: 24px;
}

.bubble li {
  margin: 4px 0;
  line-height: 1.6;
}

/* 分割线 */
.bubble hr {
  border: none;
  border-top: 1px solid #e8e8e8;
  margin: 16px 0;
}

/* 引用样式 */
.bubble blockquote {
  border-left: 4px solid #409eff;
  margin: 12px 0;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 0 6px 6px 0;
  color: #666;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .messages-container {
    max-width: 1000px;
  }

  .input-area {
    max-width: 1000px;
  }
}

@media (max-width: 992px) {
  .messages-container {
    max-width: 800px;
  }

  .input-area {
    max-width: 800px;
    padding: 15px;
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .send-btn, .export-btn {
    flex: 1;
    min-width: 140px;
  }

  .message-content {
    max-width: 80%;
  }
}

@media (max-width: 768px) {
  .el-header {
    padding: 0 10px;
    height: 60px;
  }

  .el-header h1 {
    font-size: 18px;
    line-height: 60px;
  }

  .el-footer {
    padding: 10px 12px !important;
  }

  .el-aside {
    width: 200px !important;
    height: calc(100vh - 60px);
  }

  .el-main {
    height: calc(100vh - 140px);
    padding: 15px;
  }

  .input-area {
    padding: 12px;
    border-radius: 8px;
    max-width: 100%;
  }

  .chat-input >>> .el-textarea__inner {
    padding: 10px 14px;
    font-size: 13px;
  }

  .send-btn, .export-btn {
    padding: 10px 20px !important;
    font-size: 13px !important;
    min-width: 110px;
  }

  .message-content {
    max-width: 75%;
  }

  .bubble {
    padding: 12px 16px;
    font-size: 13px;
  }

  .message-header {
    width: 60px;
    padding: 0 5px;
  }

  .quick-questions-buttons {
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .quick-question-btn {
    font-size: 11px;
    padding: 3px 6px;
  }
}

@media (max-width: 480px) {
  .el-header h1 {
    font-size: 16px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 8px;
  }

  .send-btn, .export-btn {
    width: 100%;
    min-width: auto;
  }

  .message-content {
    max-width: 70%;
  }

  .bubble {
    padding: 10px 14px;
    font-size: 12px;
  }
}
</style>
