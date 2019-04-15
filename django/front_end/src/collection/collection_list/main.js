import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import App from './App.vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.config.productionTip = false
Vue.config.devtools = true
Vue.use(BootstrapVue)

new Vue({
  render: h => h(App, {
    props: {
      items: JSON.parse(document.getElementById('app_data').innerHTML)
    }
  }),
}).$mount('#app')
