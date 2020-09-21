import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import guide from './views/guide.vue';
import docs from './views/docs.vue';
import data from './views/data.vue';
import flows from './views/explore-flows.vue';
import flow from './views/flow.vue';
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
            path: '/guide',
            name: 'guide',
            component: guide,
            meta: {
                title: 'Guide',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    },
                    {
                        text: 'user guide',
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
                title: 'Docs',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    },
                    {
                        text: 'developer docs',
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
                title: 'Log In',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    },
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
                title: 'Log Out',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    },
                    {
                        text: 'log out',
                        href: '/logout'
                    }
                ]
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
                        text: 'plantit',
                        href: '/'
                    },
                    {
                        text: 'users',
                        href: '/users'
                    }
                ]
            }
        },
        {
            path: '/data',
            name: 'data',
            component: data,
            meta: {
                title: 'Data',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    },
                    {
                        text: 'explore data',
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
                title: 'Flows',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    },
                    {
                        text: 'flows',
                        href: '/flows'
                    }
                ]
            }
        },
        {
            path: '/:username/:name',
            name: 'flow',
            props: true,
            component: flow,
            meta: {
                title: 'Flow',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    }
                ]
            }
        },
        {
            path: '/:username/runs/:id',
            name: 'run',
            props: true,
            component: run,
            meta: {
                title: 'Run',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
                    }
                ]
            }
        },
        {
            path: '/:username',
            name: 'user',
            props: true,
            component: user,
            meta: {
                title: 'User',
                crumb: [
                    {
                        text: 'plantit',
                        href: '/'
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
                        text: 'plantit',
                        href: '/'
                    },
                    {
                        text: '404'
                    }
                ]
            }
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.name === 'flow') {
        to.meta.title = `Flow ${to.params.name}`;
    }
    if (to.name === 'run') {
        to.meta.title = `Run ${to.params.id}`;
    }
    if (to.name === 'user') {
        to.meta.title = `User ${to.params.username}`;
    }
    if (to.meta.name !== null) {
        document.title = to.meta.title;
    }
    if (to.matched.some(record => record.name === 'flow')) {
        while (to.meta.crumb.length > 1) to.meta.crumb.pop();
        to.meta.crumb.push(
            {
                text: to.params.username,
                href: `/${to.params.username}`
            },
            {
                text: to.params.name,
                href: `/${to.params.username}/${to.params.name}`
            }
        );
    }
    if (to.matched.some(record => record.name === 'run')) {
        while (to.meta.crumb.length > 1) to.meta.crumb.pop();
        to.meta.crumb.push(
            {
                text: to.params.username,
                href: `/${to.params.username}`
            },
            {
                text: 'runs',
                href: `/${to.params.username}`
            },
            {
                text: to.params.id,
                href: `/${to.params.username}/runs/${to.params.id}`
            }
        );
    }
    if (to.matched.some(record => record.name === 'user')) {
        while (to.meta.crumb.length > 1) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: to.params.username,
            href: `/${to.params.username}`
        });
    }
    // if (to.matched.some(record => record.meta.requiresAuth)) {
    //     if (!store.getters.loggedIn) {
    //         window.location = '/login/?next=' + to.fullPath;
    //     } else {
    //     next();
    //     }
    // } else {
    next();
    // }
});

export default router;
