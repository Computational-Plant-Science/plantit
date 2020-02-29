import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
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
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () =>
                import(/* webpackChunkName: "about" */ './views/About.vue')
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
            path: '/user/job',
            name: 'job',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Job.vue'),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/dashboard',
            name: 'dashboard',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Dashboard.vue'),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/collections',
            name: 'collections',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Collections.vue'),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/collection',
            name: 'collection',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Collection.vue'),
            props: route => ({ pk: parseInt(route.query.pk) }),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/collection/new',
            name: 'newCollection',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/NewCollection.vue'),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/collection/add',
            name: 'addFiles',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/AddFiles.vue'),
            props: route => ({ pk: parseInt(route.query.pk) }),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/workflow/choose',
            name: 'analyze',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Analyze.vue'),
            props: route => ({ pk: parseInt(route.query.pk) }),
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/user/workflow/submit',
            name: 'submit_workflow',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/SubmitWorkflow.vue'),
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
                import(/* webpackChunkName: "about" */ './views/PageNotFound.vue')
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
