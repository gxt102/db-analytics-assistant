// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import axios from 'axios'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
/* 设置cookie,session跨域配置 */
axios.defaults.withCredentials=true;
/* 设置post请求体,请求格式为json*/
axios.defaults.headers.post['Content-Type'] = 'application/json'
/* 设置全局axios写法 */
Vue.prototype.$http = axios
Vue.use(ElementUI);

Vue.config.productionTip = false

//导航钩子函数，类似于拦截器:to到底路由对象，from从哪个路由调整过来的，next要执行的函数
router.beforeEach(function (to, from, next)  {
  //获取本地存储里的用户信息
  const name = localStorage.getItem("chatName");
  console.log("name"+name)
  //判断到达路由是否允许访问
  if(to.meta.requireAuth){
    console.log("需要登录才能访问")
    //判断用户信息是否存在
    if(name){
      console.log("用户信息存在，可以访问")
      //允许访问
      next();
    }else{
      console.log("用户信息存在，不可以访问")
      //不允许访问，回到登陆页面
      next("/");
    }

  }else{
    //不需要登录
    console.log("不需要登录，才可以访问");
    next();
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
