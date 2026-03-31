<script>
export default {
  name: "Register",
  data() {
    return {
      form: {
        username: "",
        email: "",
        phone: "",
        password: "",
        confirmPassword: ""
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: this.validateConfirmPassword, trigger: 'blur' }
        ]
      },
      // 新增状态管理
      showPassword: false,
      showConfirmPassword: false,
      loading: false,
      // 密码强度相关
      passwordStrength: {
        percentage: 0,
        color: '#ff4d4f',
        text: '极弱'
      },
      // 验证状态
      usernameStatus: '',
      emailStatus: '',
      phoneStatus: '',
      passwordStatus: '',
      confirmPasswordStatus: ''
    }
  },
  computed: {
    isFormValid() {
      return (
        this.form.username.trim() &&
        this.form.email.trim() &&
        this.form.phone.trim() &&
        this.form.password.trim() &&
        this.form.confirmPassword.trim() &&
        this.usernameStatus === 'success' &&
        this.emailStatus === 'success' &&
        this.phoneStatus === 'success' &&
        this.passwordStatus === 'success' &&
        this.confirmPasswordStatus === 'success'
      )
    }
  },
  watch: {
    'form.username'(newVal) {
      this.checkUsername(newVal);
    },
    'form.email'(newVal) {
      this.checkEmail(newVal);
    },
    'form.phone'(newVal) {
      this.checkPhone(newVal);
    },
    'form.password'(newVal) {
      this.checkPasswordStrength(newVal);
    },
    'form.confirmPassword'(newVal) {
      this.checkConfirmPassword(newVal);
    }
  },
  methods: {
    // 用户名检查
    checkUsername(username) {
      if (!username) {
        this.usernameStatus = '';
        return;
      }

      if (username.length < 3) {
        this.usernameStatus = 'error';
      } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        this.usernameStatus = 'error';
      } else {
        // 模拟异步检查
        setTimeout(() => {
          const takenUsernames = ['admin', 'test', 'user123'];
          if (takenUsernames.includes(username.toLowerCase())) {
            this.usernameStatus = 'error';
          } else {
            this.usernameStatus = 'success';
          }
        }, 300);
      }
    },

    // 邮箱检查
    checkEmail(email) {
      if (!email) {
        this.emailStatus = '';
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        this.emailStatus = 'error';
      } else {
        this.emailStatus = 'success';
      }
    },

    // 手机号检查
    checkPhone(phone) {
      if (!phone) {
        this.phoneStatus = '';
        return;
      }

      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(phone)) {
        this.phoneStatus = 'error';
      } else {
        this.phoneStatus = 'success';
      }
    },

    // 密码强度检查
    checkPasswordStrength(password) {
      if (!password) {
        this.passwordStrength = { percentage: 0, color: '#ff4d4f', text: '极弱' };
        this.passwordStatus = '';
        return;
      }

      let strength = 0;
      if (password.length >= 6) strength += 25;
      if (password.length >= 10) strength += 25;
      if (/[A-Z]/.test(password)) strength += 25;
      if (/[0-9]/.test(password)) strength += 25;


      strength = Math.min(strength, 100);

      let color = '#ff4d4f';
      let text = '极弱';

      if (strength < 50) {
        color = '#ff4d4f';
        text = '弱';
      } else if (strength < 75) {
        color = '#faad14';
        text = '中等';
      } else {
        color = '#52c41a';
        text = '强';
      }

      this.passwordStrength = {
        percentage: strength,
        color: color,
        text: text
      };

      this.passwordStatus = password.length >= 6 ? 'success' : 'error';
    },

    // 确认密码检查
    checkConfirmPassword(confirmPassword) {
      if (!confirmPassword) {
        this.confirmPasswordStatus = '';
        return;
      }

      if (confirmPassword !== this.form.password) {
        this.confirmPasswordStatus = 'error';
      } else {
        this.confirmPasswordStatus = 'success';
      }
    },

    // 验证确认密码
    validateConfirmPassword(rule, value, callback) {
      if (value !== this.form.password) {
        callback(new Error('两次输入密码不一致'));
      } else {
        callback();
      }
    },

    // 注册方法
    async handleRegister() {
      try {
        this.loading = true;

        const valid = await this.$refs.form.validate();
        if (valid) {
          // 模拟注册请求
          await new Promise(resolve => setTimeout(resolve, 1500));

          this.$message.success('注册成功！');
          console.log('注册信息:', this.form);

          // 注册成功后跳转到登录页面
          setTimeout(() => {
            this.goToLogin();
          }, 1500);
        }
      } catch (error) {
        this.$message.error('请完善注册信息');
      } finally {
        this.loading = false;
      }
    },

    // 重置表单
    resetForm() {
      this.$refs.form.resetFields();
      this.usernameStatus = '';
      this.emailStatus = '';
      this.phoneStatus = '';
      this.passwordStatus = '';
      this.confirmPasswordStatus = '';
      this.passwordStrength = { percentage: 0, color: '#ff4d4f', text: '极弱' };
    },

    // 切换到登录页面
    goToLogin() {
      this.$emit('switch-to-login');
    }
  }
}
</script>

<template>
  <div class="register-container">
    <!-- 背景装饰元素 -->
    <div class="decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="register-card">
      <div class="register-header">
        <div class="logo-placeholder">
          <i class="el-icon-user-solid"></i>
        </div>
        <h2>用户注册</h2>
        <p>创建新账户，开启数据分析之旅</p>
      </div>

      <el-form
        ref="form"
        :model="form"
        :rules="rules"
        class="register-form"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            prefix-icon="el-icon-user"
            clearable
          ></el-input>
          <div v-if="usernameStatus" :class="['status-text', usernameStatus]">
            {{ usernameStatus === 'success' ? '✓ 用户名可用' : '✗ 用户名不符合要求' }}
          </div>
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱"
            prefix-icon="el-icon-message"
            clearable
          ></el-input>
          <div v-if="emailStatus" :class="['status-text', emailStatus]">
            {{ emailStatus === 'success' ? '✓ 邮箱格式正确' : '✗ 邮箱格式错误' }}
          </div>
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            prefix-icon="el-icon-phone"
            clearable
          ></el-input>
          <div v-if="phoneStatus" :class="['status-text', phoneStatus]">
            {{ phoneStatus === 'success' ? '✓ 手机号格式正确' : '✗ 请输入正确的手机号' }}
          </div>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <div class="password-input">
            <el-input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              prefix-icon="el-icon-lock"
            ></el-input>
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>

          <!-- 密码强度指示器 -->
          <div v-if="form.password" class="password-strength">
            <div class="strength-meter">
              <div class="strength-bar" :style="{
                width: passwordStrength.percentage + '%',
                background: passwordStrength.color
              }"></div>
            </div>
            <span class="strength-text">密码强度: {{ passwordStrength.text }}</span>
          </div>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <div class="password-input">
            <el-input
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="请再次输入密码"
              prefix-icon="el-icon-lock"
            ></el-input>
            <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
              {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="confirmPasswordStatus" :class="['status-text', confirmPasswordStatus]">
            {{ confirmPasswordStatus === 'success' ? '✓ 密码匹配' : '✗ 两次密码不一致' }}
          </div>
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <el-button
              type="primary"
              @click="handleRegister"
              class="register-btn"
              :loading="loading"
              :disabled="!isFormValid"
            >
              {{ loading ? '注册中...' : '立即注册' }}
            </el-button>
            <el-button @click="resetForm" :disabled="loading">重置</el-button>
          </div>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <span>已有账户？</span>
        <el-button type="text" @click="goToLogin" :disabled="loading">立即登录</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 玻璃态卡片 */
.register-card {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1),
              0 1px 3px rgba(0, 0, 0, 0.05),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
  z-index: 2;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-placeholder {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.register-header h2 {
  color: white;
  margin-bottom: 10px;
  font-weight: 600;
  font-size: 28px;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.register-header p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.register-form {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

:deep(.el-input__inner) {
  height: 45px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  transition: all 0.3s ease;
}

:deep(.el-input__inner:focus) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

:deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.7);
}

/* 密码输入框容器 */
.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 5px;
  color: rgba(255, 255, 255, 0.7);
  transition: color 0.3s ease;
  z-index: 10;
}

.toggle-password:hover {
  color: white;
}

/* 状态文本 */
.status-text {
  font-size: 12px;
  margin-top: 5px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.status-text.success {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.status-text.error {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
}

/* 密码强度指示器 */
.password-strength {
  margin-top: 10px;
}

.strength-meter {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}

.strength-bar {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.register-btn {
  flex: 1;
  height: 45px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  transition: all 0.3s ease;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.register-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.register-footer .el-button {
  padding: 0;
  margin-left: 5px;
  color: white;
}

/* 背景装饰 */
.decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -200px;
  left: -200px;
}

.circle-2 {
  width: 250px;
  height: 250px;
  bottom: -100px;
  right: -100px;
}

.circle-3 {
  width: 180px;
  height: 180px;
  top: 20%;
  right: 10%;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-card {
    padding: 32px 24px;
    max-width: 90%;
  }

  .form-actions {
    flex-direction: column;
  }

  .register-btn,
  .el-button {
    width: 100%;
  }
}
</style>
