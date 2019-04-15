import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false
Vue.config.devtools = true

const page_data = JSON.parse(document.getElementById('app_data').innerHTML)

new Vue({
  render: h => h(App, {
    props: {
      collection: page_data.collection,
      referrer: page_data.referrer
    }
  }),
}).$mount('#app')
