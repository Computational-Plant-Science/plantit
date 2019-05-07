import '@babel/polyfill';
import Vue from 'vue';
import './plugins/bootstrap-vue';
import App from './App.vue';
import router from './router';
import store from './store';
import Axios from 'axios'
import VueAnalytics from 'vue-analytics'

Axios.defaults.xsrfCookieName = 'csrftoken'
Axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

Vue.config.productionTip = false;

// Uncomment and set id to use google analytics tracking
// Vue.use(VueAnalytics, {
//   id: 'UA-XXX-X'
// })

new Vue({
    router,
    store,
    render: h => h(App)
}).$mount('#app');
