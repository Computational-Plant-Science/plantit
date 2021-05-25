import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import workflows from './views/explore-workflows.vue';
import workflow from './views/workflow.vue';
import agent from './views/agent.vue';
import agents from './views/public.vue';
import user from './views/user.vue';
import users from './views/users.vue';
import run from './views/run.vue';
import dataset from './views/dataset.vue';
import annotate from './views/annotate.vue';
import store from './store/store.js';

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
            path: '/agents',
            name: 'agents',
            component: agents,
            meta: {
                title: 'Agents',
                crumb: [
                    {
                        text: 'Agents',
                        href: '/agents'
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
            path: '/agent/:name',
            name: 'agent',
            props: true,
            component: agent,
            meta: {
                title: 'Agent',
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
            path: '/dataset/:path',
            name: 'dataset',
            props: true,
            component: dataset,
            meta: {
                title: 'Dataset',
                crumb: [],
                requiresAuth: true
            }
        },
        {
            path: '/annotate/:path',
            name: 'annotate',
            props: true,
            component: annotate,
            meta: {
                title: 'Annotate',
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

router.beforeEach(async (to, from, next) => {
    await store.dispatch('user/loadProfile');
    if (to.name === 'workflow') to.meta.title = `Workflow: ${to.params.name}`;
    if (to.name === 'run') to.meta.title = `Run: ${to.params.id}`;
    if (to.name === 'agent') to.meta.title = `Resource: ${to.params.name}`;
    if (to.name === 'user') {
        // if (
        //     store.getters['user/profile'].cyverseProfile.username ===
        //     to.params.username
        // )
        //    to.meta.title = 'Dashboard';
        // else to.meta.title = `User: ${to.params.username}`;
        to.meta.title = 'PlantIT';
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: 'Dashboard'
        });
    }
    if (to.name === 'dataset') to.meta.title = `Dataset: ${to.params.path}`;
    if (to.name === 'artifact') to.meta.title = `Artifact: ${to.params.path}`;
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
    if (to.matched.some(record => record.name === 'agent')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Agent: ${to.params.name}`,
            href: `/agent/${to.params.name}`
        });
    }
    if (to.matched.some(record => record.name === 'user')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({text: 'Your Dashboard'});
        // to.meta.crumb.push({
        //     text: `User: ${to.params.username}`,
        //     href: `/user/${to.params.username}`
        // });
    }
    if (to.matched.some(record => record.name === 'dataset')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Dataset: ${to.params.path}`,
            href: `/dataset/${to.params.path}`
        });
    }
    if (to.matched.some(record => record.name === 'artifact')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Artifact: ${to.params.path}`,
            href: `/artifact/${to.params.path}`
        });
    }
    if (to.meta.requiresAuth && !store.getters['user/profile'].loggedIn) {
        window.location.replace(
            process.env.VUE_APP_URL + '/apis/v1/idp/cyverse_login/'
        );
    } else next();
});

export default router;
