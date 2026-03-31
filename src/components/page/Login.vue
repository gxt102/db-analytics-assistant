<script>
export default {
  name: "Login",
  data() {
    return {
      email: localStorage.getItem('rememberedEmail') || "", // 邮箱
      code: "", // 验证码
      showCodeInput: false, // 是否显示验证码输入框
      isSendingCode: false, // 是否正在发送验证码
      countdown: 60, // 倒计时
      timer: null, // 定时器
      loading: false, // 登录加载状态
      rememberEmail: localStorage.getItem('rememberedEmail') ? true : false // 记住邮箱
    }
  },
  mounted() {
    // 如果有记住的邮箱，自动获取验证码
    if (this.email && this.validateEmail(this.email)) {
      this.showCodeInput = true;
    }

  },
  beforeDestroy() {
    // 组件销毁前清除定时器
    if (this.timer) {
      clearInterval(this.timer);
    }

    if (this.particlesAnimation) {
      cancelAnimationFrame(this.particlesAnimation);
    }
  },
  methods: {
    // 发送验证码方法
    sendCode() {
      if (!this.email) {
        this.showToast('请输入邮箱', 'error');
        return;
      }

      if (!this.validateEmail(this.email)) {
        this.showToast('请输入正确的邮箱格式', 'error');
        return;
      }

      // 显示验证码输入框
      this.showCodeInput = true;

      // 开始倒计时
      this.isSendingCode = true;
      this.countdown = 60;

      // 模拟发送验证码请求
      this.$http.post("http://localhost:8000/sendCode", {
        email: this.email,
        code: this.code
      })
        .then(rs => {
          this.showToast(rs.data.msg, 'success');
          console.log(rs.data);
        })
        .catch(error => {
          this.showToast('验证码发送失败', 'error');
          console.error(error);
        });

      // 启动倒计时
      this.timer = setInterval(() => {
        if (this.countdown <= 0) {
          clearInterval(this.timer);
          this.isSendingCode = false;
          this.countdown = 60;
        } else {
          this.countdown--;
        }
      }, 1000);
    },

    // 邮箱验证
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    },

    // 登录方法
    login() {
      // 表单验证
      if (!this.email || !this.code) {
        this.showToast('请填写邮箱和验证码', 'error');
        return;
      }

      if (!this.validateEmail(this.email)) {
        this.showToast('请输入正确的邮箱格式', 'error');
        return;
      }

      this.loading = true;

      // 发送登录请求
      this.$http.post("http://localhost:8000/login", {
        email: this.email,
        code: this.code
      })
      .then(rs => {
        if (rs.data.code === 200) {
          // 保存记住邮箱设置
          if (this.rememberEmail) {
            localStorage.setItem("rememberedEmail", this.email);
          } else {
            localStorage.removeItem("rememberedEmail");
          }

          localStorage.setItem("chatName", this.email);

          // 登录成功
          this.showToast('登录成功', 'success');

          // 跳转到聊天页面
          setTimeout(() => {
            this.$router.push("/chat");
          }, 800);
        } else {
          // 登录失败
          this.showToast(rs.data.msg, 'error');
          this.loading = false;
        }
      })
      .catch(error => {
        this.showToast('登录失败，请稍后重试', 'error');
        console.error(error);
        this.loading = false;
      });
    },

    // 切换到注册页面
    goToRegister() {
      this.$emit('switch-to-register');
    },

    // Toast提示
    showToast(message, type = 'info') {
      // 使用Element UI的message
      const toastType = type === 'error' ? 'error' :
                      type === 'success' ? 'success' : 'info';

      this.$message({
        message,
        type: toastType,
        duration: 3000,
        customClass: 'custom-toast',
        showClose: true
      });
    }
  }
}
</script>

<template>
  <div class="login-container">

    <!-- 玻璃态卡片 -->
    <div class="login-card glassmorphism">
      <!-- 品牌标识 -->
      <div class="brand-section">
        <div class="brand-logo">
          <div class="logo-circle">
            <div class="logo-inner">
              <span class="logo-icon">🤖</span>
            </div>
            <div class="logo-ring"></div>
          </div>
        </div>
        <div class="brand-text">
          <h1 class="brand-name">智能数据分析助手</h1>
          <p class="brand-tagline">让数据说话，用智能分析</p>
        </div>
      </div>

      <!-- 登录表单 -->
      <div class="login-form">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>请使用邮箱验证码登录</p>
        </div>

        <!-- 邮箱输入 -->
        <div class="form-group">
          <div class="input-icon">
            <el-icon><Message /></el-icon>
          </div>
          <input
            type="email"
            v-model="email"
            required
            autocomplete="email"
            placeholder="请输入邮箱"
            @keyup.enter="showCodeInput ? login() : sendCode()"
          />
        </div>

        <!-- 验证码输入（动态显示） -->
        <div v-if="showCodeInput" class="form-group">
          <div class="input-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <input
            type="text"
            v-model="code"
            required
            placeholder="请输入6位验证码"
            maxlength="6"
            @keyup.enter="login"
          />
          <button
            type="button"
            class="code-btn"
            @click="sendCode"
            :disabled="isSendingCode || !email"
          >
            {{ isSendingCode ? `${countdown}秒后重试` : '获取验证码' }}
          </button>
        </div>

        <!-- 记住我选项 -->
        <div class="form-options">
          <label class="checkbox-container">
            <input type="checkbox" v-model="rememberEmail">
            <span class="checkmark"></span>
            <span class="checkbox-label">记住邮箱</span>
          </label>
          <a href="#" class="forgot-password link-hover" @click.prevent="sendCode">
            {{ showCodeInput ? '重新发送验证码' : '获取验证码' }}
          </a>
        </div>

        <!-- 登录按钮 -->
        <button
          type="button"
          class="login-btn gradient-btn"
          @click="showCodeInput ? login() : sendCode()"
          :disabled="loading || (showCodeInput && (!email || !code))"
        >
          <span v-if="!loading">
            {{ showCodeInput ? '登录' : '获取验证码' }}
          </span>
          <span v-else class="loading">
            <div class="spinner"></div>
            {{ showCodeInput ? '登录中...' : '发送中...' }}
          </span>
        </button>

        <!-- 注册链接 -->
        <div class="register-link">
          还没有账户？
          <a href="#" class="link-hover" @click.prevent="goToRegister">
            <span class="link-text">立即注册</span>
            <svg class="link-arrow" viewBox="0 0 20 20">
              <path d="M12.95 10.707l.707-.707L8 4.343 6.586 5.757 10.828 10l-4.242 4.243L8 15.657l4.95-4.95z"/>
            </svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 玻璃态卡片 */
.glassmorphism {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1),
              0 1px 3px rgba(0, 0, 0, 0.05),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.login-card {
  width: 100%;
  max-width: 440px;
  border-radius: 24px;
  padding: 48px;
  z-index: 2;
  position: relative;
}

/* 品牌标识 */
.brand-section {
  text-align: center;
  margin-bottom: 40px;
}

.brand-logo {
  margin-bottom: 20px;
}

.logo-circle {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.logo-inner {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.logo-icon {
  font-size: 36px;
  color: white;
}

.logo-ring {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(0.95); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 0.8; }
  100% { transform: scale(0.95); opacity: 0.5; }
}

.brand-name {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.brand-tagline {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 400;
  letter-spacing: 0.5px;
}

/* 表单头部 */
.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: white;
  margin-bottom: 8px;
}

.form-header p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

/* 表单组 */
.form-group {
  position: relative;
  margin-bottom: 24px;
}

.form-group input {
  width: 85%;
  padding: 16px 16px 16px 48px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 16px;
  color: white;
  transition: all 0.3s ease;
  outline: none;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.form-group input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.6);
  z-index: 2;
}

.input-icon .el-icon {
  font-size: 20px;
}

/* 验证码按钮 */
.code-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(103, 194, 58, 0.8);
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.code-btn:hover:not(:disabled) {
  background: rgba(103, 194, 58, 1);
  transform: translateY(-50%) scale(1.05);
}

.code-btn:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding-left: 30px;
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 20px;
  width: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.checkbox-container:hover .checkmark {
  background: rgba(255, 255, 255, 0.2);
}

.checkbox-container input:checked ~ .checkmark {
  background: #67C23A;
  border-color: #67C23A;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 6px;
  top: 2px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.forgot-password {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: color 0.3s ease;
  cursor: pointer;
}

.link-hover:hover {
  color: white;
  text-decoration: underline;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.gradient-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.gradient-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.gradient-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading {
  display: flex;
  align-items: center;
  gap: 12px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 注册链接 */
.register-link {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 32px;
}

.register-link a {
  color: white;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  cursor: pointer;
}

.link-text {
  font-weight: 500;
}

.link-arrow {
  width: 16px;
  height: 16px;
  fill: currentColor;
  transition: transform 0.3s ease;
}

.register-link a:hover .link-arrow {
  transform: translateX(4px);
}

/* Toast消息样式 */
:deep(.custom-toast) {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
  }

  .brand-name {
    font-size: 20px;
  }

  .form-header h2 {
    font-size: 20px;
  }

  .code-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
