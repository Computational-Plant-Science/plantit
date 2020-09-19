import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import about from './views/about.vue';
import guide from './views/guide.vue';
import docs from './views/docs.vue';
import data from './views/data.vue';
import flows from './views/flows.vue';
import flow from './views/flow.vue';
import runs from './views/user-runs.vue';
import run from './views/run.vue';
import user from './views/user.vue';
import users from './views/users.vue';
import login from './views/log-in.vue';
import logout from './views/log-out.vue';

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
                title: 'home',
                crumb: []
            }
        },
        {
            path: '/about',
            name: 'about',
            component: about,
            meta: {
                title: 'about',
                crumb: [
                    {
                        text: 'about',
                        href: '/about'
                    }
                ]
            }
        },
        {
            path: '/guide',
            name: 'guide',
            component: guide,
            meta: {
                title: 'guide',
                crumb: [
                    {
                        text: 'guide',
                        href: '/guide'
                    }
                ]
            }
        },
        {
            path: '/docs',
            name: 'docs',
            component: docs,
            meta: {
                title: 'docs',
                crumb: [
                    {
                        text: 'docs',
                        href: '/docs'
                    }
                ]
            }
        },
        {
            path: '/login?next=/workflows/',
            name: 'login',
            component: login,
            meta: {
                title: 'log in',
                crumb: [
                    {
                        text: 'log in',
                        href: '/login/?next=/workflows/'
                    }
                ]
            }
        },
        {
            path: '/logout',
            name: 'logout',
            component: logout,
            meta: {
                title: 'log out',
                crumb: [
                    {
                        text: 'log out',
                        href: '/logout'
                    }
                ]
            }
        },
        {
            path: '/data',
            name: 'data',
            component: data,
            meta: {
                title: 'data',
                crumb: [
                    {
                        text: 'data',
                        href: '/data'
                    }
                ]
            }
        },
        {
            path: '/flows',
            name: 'flows',
            component: flows,
            meta: {
                title: 'flows',
                crumb: [
                    {
                        text: 'flows',
                        href: '/flows'
                    }
                ]
            }
        },
        {
            path: '/flows/:owner/:name',
            name: 'flow',
            props: true,
            component: flow,
            meta: {
                title: 'flow',
                crumb: [
                    {
                        text: 'flows',
                        href: '/flows'
                    }
                ]
            }
        },
        {
            path: '/runs',
            name: 'runs',
            component: runs,
            meta: {
                title: 'runs',
                crumb: [
                    {
                        text: 'runs',
                        href: '/runs'
                    }
                ]
            }
        },
        {
            path: '/runs/:id',
            name: 'run',
            props: true,
            component: run,
            meta: {
                title: 'run',
                crumb: [
                    {
                        text: 'runs',
                        href: '/runs'
                    }
                ]
            }
        },
        {
            path: '/users',
            name: 'users',
            component: users,
            meta: {
                title: 'users',
                crumb: [
                    {
                        text: 'users',
                        href: '/users'
                    }
                ]
            }
        },
        {
            path: '/users/:username',
            name: 'user',
            props: true,
            component: user,
            meta: {
                title: 'user',
                crumb: [
                    {
                        text: 'users',
                        href: '/users'
                    }
                ],
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
                ]
            }
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.name === 'workflow') {
        to.meta.title = `flow ${to.params.name}`;
    }
    if (to.name === 'run') {
        to.meta.title = `run ${to.params.id}`;
    }
    if (to.name === 'user') {
        to.meta.title = `user ${to.params.username}`;
    }
    if (to.meta.name !== null) {
        document.title = to.meta.title;
    }
    if (to.matched.some(record => record.name === 'workflow')) {
        if (to.meta.crumb.length === 4) {
            to.meta.crumb.pop();
            to.meta.crumb.pop();
        }
        to.meta.crumb.push(
            {
                text: to.params.owner,
                href: `/workflows/${to.params.owner}`
            },
            {
                text: to.params.name,
                href: `/workflows/${to.params.owner}/${to.params.name}`
            }
        );
    }
    if (to.matched.some(record => record.name === 'run')) {
        if (to.meta.crumb.length === 4) {
            to.meta.crumb.pop();
        }
        to.meta.crumb.push({
            text: to.params.id,
            href: `/runs/${to.params.id}`
        });
    }
    if (to.matched.some(record => record.name === 'user')) {
        if (to.meta.crumb.length === 2) {
            to.meta.crumb.pop();
        }
        to.meta.crumb.push({
            text: to.params.username,
            href: `/users/${to.params.username}`
        });
    }
    if (to.matched.some(record => record.meta.requiresAuth)) {
        // if (!Auth.isLoggedIn()) {
        //     window.location = '/login/?next=' + to.fullPath;
        // } else {
        next();
        // }
    } else {
        next();
    }
});

export default router;
