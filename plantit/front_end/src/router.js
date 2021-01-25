import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import flows from './views/explore-flows.vue';
import flow from './views/flow.vue';
import run from './views/run.vue';
import user from './views/user.vue';
import users from './views/users.vue';

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
            path: '/:username/:name',
            name: 'flow',
            props: true,
            component: flow,
            meta: {
                title: 'Flow',
                crumb: [
                ],
                requiresAuth: true
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
                ],
                requiresAuth: true
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
                ],
                requiresAuth: false
            }
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.name === 'flow') {
        to.meta.title = `Flow: ${to.params.name}`;
    }
    if (to.name === 'run') {
        to.meta.title = `Run: ${to.params.id}`;
    }
    if (to.name === 'user') {
        to.meta.title = `User: ${to.params.username}`;
    }
    if (to.meta.name !== null) {
        document.title = to.meta.title;
    }
    if (to.matched.some(record => record.name === 'flow')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Flow: ${to.params.username}/${to.params.name}`,
            href: `/${to.params.username}/${to.params.name}`
        });
    }
    if (to.matched.some(record => record.name === 'run')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Run: ${to.params.id}`,
            href: `/${to.params.username}/runs/${to.params.id}`
        });
    }
    if (to.matched.some(record => record.name === 'user')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `User: ${to.params.username}`,
            href: `/${to.params.username}`
        });
    }
    // if (to.matched.some(record => record.meta.requiresAuth)) {
    //     if (!store.getters.loggedIn) {
    //         window.location.href = 'https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fkc.cyverse.org%2Fauth%2Frealms%2FCyVerse%2Faccount%2F'
    //     } else {
    //         next(); // go to wherever I'm going
    //     }
    // } else {
    next(); // does not require auth, make sure to always call next()!
    // }
});

export default router;
