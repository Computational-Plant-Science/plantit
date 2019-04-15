import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';

Vue.use(Router);

export default new Router({
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
                import(/* webpackChunkName: "about" */ './views/Jobs.vue')
        },
        {
            path: '/user/job',
            name: 'job',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Job.vue')
        },
        {
            path: '/user/dashboard',
            name: 'dashboard',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Dashboard.vue')
        },
        {
            path: '/user/collections',
            name: 'collections',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Collections.vue')
        },
        {
            path: '/user/collection',
            name: 'collection',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Collection.vue'),
            props: (route) => ({ pk: route.query.pk})
        },
        {
            path: '/user/collection/new',
            name: 'newCollection',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/NewCollection.vue')
        },
        {
          path: '/user/collection/add',
          name: 'addFiles',
          component: () =>
              import(/* webpackChunkName: "about" */ './views/AddFiles.vue'),
          props: (route) => ({ pk: parseInt(route.query.pk) })
        },
        {
            path: '/user/workflow/choose',
            name: 'analyze',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Analyze.vue'),
            props: (route) => ({ pk: route.query.pk })
        },
        {
            path: '/user/workflow/submit',
            name: 'submit_workflow',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/SubmitWorkflow.vue'),
            props: (route) => ({ job_pk: route.query.job_pk, workflow_pk: route.query.workflow_pk})
        },
        {
            path: '/login',
            name: 'login',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/Login.vue'),
        }
    ]
});
