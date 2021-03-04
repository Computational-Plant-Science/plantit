import '@babel/polyfill';
import Vue from 'vue';
import './plugins/bootstrap-vue';
import App from './App.vue';
import VueLogger from 'vuejs-logger';
import VueSocketIO from 'vue-socket.io';
import SocketIO from 'socket.io-client';
import VueFriendlyIframe from 'vue-friendly-iframe';
import router from './router';
import store from './store/store';
import Axios from 'axios';
import VueAnalytics from 'vue-analytics';
import AsyncComputed from 'vue-async-computed'
import * as Sentry from '@sentry/browser';
import * as Integrations from '@sentry/integrations';
// import Keycloak from 'keycloak-js';

Axios.defaults.xsrfCookieName = 'csrftoken';
Axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';

Vue.config.productionTip = false;

Vue.use(AsyncComputed);

Vue.use(
    new VueSocketIO({
        debug: true,
        connection: SocketIO(process.env.VUE_API_URL)
    })
);
Vue.use(VueLogger);
Vue.use(VueFriendlyIframe);

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

// let config = {
//     url: 'https://kc.cyverse.org/auth/',
//     realm: 'CyVerse',
//     clientId: 'local-testing',
//     onLoad: 'login-required',
//     publicClient: 'true'
// };

//let keycloak = Keycloak({
//    realm: 'CyVerse',
//    url: 'https://kc.cyverse.org/auth/',
//    'auth-server-url': 'https://kc.cyverse.org/auth/',
//    'ssl-required': 'external',
//    clientId: 'local-testing',
//    resource: 'local-testing',
//    'public-client': true,
//    'confidential-port': 3000
//});
//
//keycloak
//    .init({ onLoad: 'login-required' })
//    .then(auth => {
//        if (!auth) {
//            window.location.reload();
new Vue({
    router,
    store,
    render: h => h(App)
}).$mount('#app');
// `        } else {
// `            Vue.$log.info('Authenticated');
// `            new Vue({
// `                router,
// `                store,
// `                render: h => h(App, { props: { keycloak: keycloak } })
// `            }).$mount('#app');
// `        }
// `
// `        //Token Refresh
// `        setInterval(() => {
// `            keycloak
// `                .updateToken(70)
// `                .then(refreshed => {
// `                    if (refreshed) {
// `                        Vue.$log.info('Token refreshed' + refreshed);
// `                    } else {
// `                        Vue.$log.warn(
// `                            'Token not refreshed, valid for ' +
// `                                Math.round(
// `                                    keycloak.tokenParsed.exp +
// `                                        keycloak.timeSkew -
// `                                        new Date().getTime() / 1000
// `                                ) +
// `                                ' seconds'
// `                        );
// `                    }
// `                })
// `                .catch(() => {
// `                    Vue.$log.error('Failed to refresh token');
// `                });
// `        }, 6000);
// `    })
// `    .catch(() => {
// `        Vue.$log.error('Authenticated Failed');
// `        alert('Authentication failed');
// `    });
