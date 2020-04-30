import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';
import Profile from './views/Profile.vue';
import Dashboard from './views/Dashboard.vue';
import Guide from './views/Guide.vue';
import Auth from '@/services/apiV1/Auth.js';

Vue.use(Router);

let router = new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/about',
            name: 'about',
            component: About
        },
        {
            path: '/guide',
            name: 'guide',
            component: Guide
        },
        {
            path: '/user/dashboard',
            name: 'dashboard',
            component: Dashboard
        },
        {
            path: '/user/profile',
            name: 'profile',
            component: Profile,
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '*',
            component: () =>
                import(
                    /* webpackChunkName: "about" */ './views/PageNotFound.vue'
                )
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!Auth.isLoggedIn()) {
            window.location = '/login/?next=' + to.fullPath;
        } else {
            //User is logged in
            next();
        }
    } else {
        //No Auth required
        next();
    }
});

export default router;
