import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import flows from './views/explore-flows.vue';
import flow from './views/flow.vue';
import run from './views/run.vue';
import target from './views/target.vue';
import user from './views/user.vue';
import users from './views/users.vue';
import targets from './views/targets.vue';

Vue.use(Router);

let router = new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/',
            name: 'home',
            component: home,
            meta: {
                title: 'PlantIT',
                crumb: [],
                requiresAuth: false
            }
        },
        {
            path: '/users',
            name: 'users',
            component: users,
            meta: {
                title: 'Users',
                crumb: [
                    {
                        text: 'Users',
                        href: '/users'
                    }
                ],
                requiresAuth: true
            }
        },
        {
            path: '/flows',
            name: 'flows',
            component: flows,
            meta: {
                title: 'Flows',
                crumb: [
                    {
                        text: 'Flows',
                        href: '/flows'
                    }
                ],
                requiresAuth: true
            }
        },
        {
            path: '/targets',
            name: 'targets',
            component: targets,
            meta: {
                title: 'Targets',
                crumb: [
                    {
                        text: 'Targets',
                        href: '/targets'
                    }
                ],
                requiresAuth: true
            }
        },
        {
            path: '/flow/:username/:name',
            name: 'flow',
            props: true,
            component: flow,
            meta: {
                title: 'Flow',
                crumb: [],
                requiresAuth: true
            }
        },
        {
            path: '/run/:id',
            name: 'run',
            props: true,
            component: run,
            meta: {
                title: 'Run',
                crumb: [],
                requiresAuth: true
            }
        },
        {
            path: '/target/:name',
            name: 'target',
            props: true,
            component: target,
            meta: {
                title: 'Target',
                crumb: [],
                requiresAuth: true
            }
        },
        {
            path: '/user/:username',
            name: 'user',
            props: true,
            component: user,
            meta: {
                title: 'User',
                crumb: [],
                requiresAuth: true
            }
        },
        {
            path: '*',
            name: '404',
            component: () =>
                import(/* webpackChunkName: "about" */ './views/not-found.vue'),
            meta: {
                title: 'Not Found',
                crumb: [
                    {
                        text: '404'
                    }
                ],
                requiresAuth: false
            }
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.name === 'flow') to.meta.title = `Flow: ${to.params.name}`;
    if (to.name === 'run') to.meta.title = `Run: ${to.params.id}`;
    if (to.name === 'target') to.meta.title = `Target: ${to.params.name}`;
    if (to.name === 'user') to.meta.title = `User: ${to.params.username}`;
    if (to.meta.name !== null) document.title = to.meta.title;
    if (to.matched.some(record => record.name === 'flow')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Flow: ${to.params.username}/${to.params.name}`,
            href: `/flow/${to.params.username}/${to.params.name}`
        });
    }
    if (to.matched.some(record => record.name === 'run')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Run: ${to.params.id}`,
            href: `/run/${to.params.id}`
        });
    }
    if (to.matched.some(record => record.name === 'target')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Target: ${to.params.name}`,
            href: `/target/${to.params.name}`
        });
    }
    if (to.matched.some(record => record.name === 'user')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `User: ${to.params.username}`,
            href: `/user/${to.params.username}`
        });
    }
    next();
});

export default router;
