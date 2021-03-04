import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import workflows from './views/explore-workflows.vue';
import workflow from './views/workflow.vue';
import server from './views/server.vue';
import servers from './views/servers.vue';
import user from './views/user.vue';
import users from './views/users.vue';
import run from './views/run.vue';

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
            path: '/workflows',
            name: 'workflows',
            component: workflows,
            meta: {
                title: 'Workflows',
                crumb: [
                    {
                        text: 'Workflows',
                        href: '/workflows'
                    }
                ],
                requiresAuth: true
            }
        },
        {
            path: '/servers',
            name: 'servers',
            component: servers,
            meta: {
                title: 'Servers',
                crumb: [
                    {
                        text: 'Servers',
                        href: '/servers'
                    }
                ],
                requiresAuth: true
            }
        },
        {
            path: '/workflow/:username/:name',
            name: 'workflow',
            props: true,
            component: workflow,
            meta: {
                title: 'Workflow',
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
            path: '/server/:name',
            name: 'server',
            props: true,
            component: server,
            meta: {
                title: 'Server',
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
    if (to.name === 'workflow') to.meta.title = `Workflow: ${to.params.name}`;
    if (to.name === 'run') to.meta.title = `Run: ${to.params.id}`;
    if (to.name === 'server') to.meta.title = `Server: ${to.params.name}`;
    if (to.name === 'user') to.meta.title = `User: ${to.params.username}`;
    if (to.meta.name !== null) document.title = to.meta.title;
    if (to.matched.some(record => record.name === 'workflow')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Workflow: ${to.params.username}/${to.params.name}`,
            href: `/workflow/${to.params.username}/${to.params.name}`
        });
    }
    if (to.matched.some(record => record.name === 'run')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Run: ${to.params.id}`,
            href: `/run/${to.params.id}`
        });
    }
    if (to.matched.some(record => record.name === 'server')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Server: ${to.params.name}`,
            href: `/server/${to.params.name}`
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
