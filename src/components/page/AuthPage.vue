<template>
  <div class="auth-container">

    <Login v-if="currentPage === 'login'" @switch-to-register="switchToRegister" />
    <Register v-else @switch-to-login="switchToLogin" />
  </div>
</template>

<script>
import Login from './Login.vue'
import Register from './Register.vue'

export default {
  name: 'AuthPage',
  components: {
    Login,
    Register
  },
  data() {
    return {
      currentPage: 'login'
    }
  },
  methods: {
    switchToRegister() {
      this.currentPage = 'register'
    },
    switchToLogin() {
      this.currentPage = 'login'
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
}
</style>
