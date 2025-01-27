import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import VueParticles from 'vue-particles';
import 'font-awesome/css/font-awesome.min.css'
import axios from 'axios'
import value from "./assets/value";
import qs from 'qs'
Vue.prototype.$qs = qs

//接口前缀地址
//axios.defaults.baseURL = '/client/login'
Vue.prototype.$axios = axios
Vue.prototype.$value=value
Vue.config.productionTip = false;
// 设置控件大小为mini
Vue.use(ElementUI,{ size: "mini" });
Vue.use(VueParticles)
axios.interceptors.request.use(function (config){
  let token=sessionStorage.getItem('token')
  if (token){
    config.headers['token']=token
  }
  return config
})
new Vue({
  router,
  render: h => h(App)
}).$mount('#app');
