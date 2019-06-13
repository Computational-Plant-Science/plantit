import '@babel/polyfill';
import Vue from 'vue';
import './plugins/bootstrap-vue';
import App from './App.vue';
import router from './router';
import store from './store';
import Axios from 'axios';
import VueAnalytics from 'vue-analytics';
import * as Sentry from '@sentry/browser';
import * as Integrations from '@sentry/integrations';

Axios.defaults.xsrfCookieName = 'csrftoken';
Axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';

Vue.config.productionTip = false;

//The plant IT object is set by django's template system.
// You can find the definition in public/index.html
if (process.env.VUE_APP_ANALYTICS_ID) {
    Vue.use(VueAnalytics, {
        id: process.env.VUE_APP_ANALYTICS_ID,
        router
    });
}

if (
    process.env.VUE_APP_SENTRY_IO_KEY &&
    process.env.VUE_APP_SENTRY_IO_PROJECT
) {
    Sentry.init({
        dsn:
            'https://' +
            process.env.VUE_APP_SENTRY_IO_KEY +
            '@sentry.io/' +
            process.env.VUE_APP_SENTRY_IO_PROJECT,
        integrations: [new Integrations.Vue({ Vue, attachProps: true })]
    });
}

new Vue({
    router,
    store,
    render: h => h(App)
}).$mount('#app');
