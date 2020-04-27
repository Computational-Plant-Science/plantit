import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';
import UserInfo from './views/UserInfo.vue';
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
            path: '/about',
            name: 'about',
            component: About
        },
        {
            path: '/user/profile',
            name: 'profile',
            component: UserInfo,
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/jobs',
            name: 'jobs',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Jobs.vue'),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/workflows',
            name: 'workflows',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Workflows.vue'),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/job',
            name: 'job',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Job.vue'),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/collection',
            name: 'collection',
            component: () =>
                import(
                    /* webpackChunkName: "about" */ './views/Collection.vue'
                ),
            props: route => ({ pk: parseInt(route.query.pk) }),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/collections',
            name: 'collections',
            component: () =>
                import(
                    /* webpackChunkName: "about" */ './views/Collections.vue'
                ),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/collection/new',
            name: 'newCollection',
            component: () =>
                import(
                    /* webpackChunkName: "about" */ './views/NewCollection.vue'
                ),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/workflow/submit',
            name: 'submit_workflow',
            component: () =>
                import(
                    /* webpackChunkName: "about" */ './views/SubmitWorkflow.vue'
                ),
            props: route => ({
                collection_pk: parseInt(route.query.collection_pk),
                workflow_name: route.query.workflow_name
            }),
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
