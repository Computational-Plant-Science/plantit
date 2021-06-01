import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import dashboard from './views/dashboard.vue';
import users from './components/users/users.vue';
import user from './components/users/user.vue';
import workflows from './components/workflows/workflows.vue';
import workflow from './components/workflows/workflow.vue';
import agents from './components/agents/agents.vue';
import agent from './components/agents/agent.vue';
import runs from './components/runs/runs.vue';
import run from './components/runs/run.vue';
import datasets from './components/datasets/datasets.vue';
import dataset from './components/datasets/dataset.vue';
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
            path: '/dashboard',
            name: 'dashboard',
            component: dashboard,
            meta: {
                title: 'Dashboard',
                crumb: [
                    {
                        text: 'Dashboard',
                        href: '/dashboard'
                    }
                ],
                requiresAuth: false
            },
            children: [
                {
                    path: 'users',
                    name: 'users',
                    component: users,
                    meta: {
                        title: 'Users',
                        crumb: [
                            {
                                text: 'Dashboard',
                                href: '/dashboard'
                            },
                            {
                                text: 'Users',
                                href: '/dashboard/users'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':username',
                            name: 'user',
                            props: true,
                            component: user,
                            meta: {
                                title: 'User',
                                crumb: [
                                    {
                                        text: 'Dashboard',
                                        href: '/dashboard'
                                    },
                                    {
                                        text: 'Users',
                                        href: '/dashboard/users'
                                    }
                                ],
                                requiresAuth: true
                            },
                            children: []
                        }
                    ]
                },
                {
                    path: 'datasets',
                    name: 'datasets',
                    props: true,
                    component: datasets,
                    meta: {
                        title: 'Datasets',
                        crumb: [
                            {
                                text: 'Dashboard',
                                href: '/dashboard'
                            },
                            {
                                text: 'Datasets',
                                href: '/dashboard/datasets'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':path',
                            name: 'dataset',
                            props: true,
                            component: dataset,
                            meta: {
                                title: 'Dataset',
                                crumb: [
                                    {
                                        text: 'Dashboard',
                                        href: '/dashboard'
                                    },
                                    {
                                        text: 'Datasets',
                                        href: '/datasets/datasets'
                                    }
                                ],
                                requiresAuth: true
                            }
                        }
                    ]
                },
                {
                    path: 'workflows',
                    name: 'workflows',
                    component: workflows,
                    meta: {
                        title: 'Workflows',
                        crumb: [
                            {
                                text: 'Dashboard',
                                href: '/dashboard'
                            },
                            {
                                text: 'Workflows',
                                href: '/dashboard/workflows'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':owner/:name',
                            name: 'workflow',
                            props: true,
                            component: workflow,
                            meta: {
                                title: 'Workflow',
                                crumb: [
                                    {
                                        text: 'Dashboard',
                                        href: '/dashboard'
                                    },
                                    {
                                        text: 'Workflows',
                                        href: '/dashboard/workflows'
                                    }
                                ],
                                requiresAuth: true
                            }
                        }
                    ]
                },
                {
                    path: 'agents',
                    name: 'agents',
                    component: agents,
                    meta: {
                        title: 'Agents',
                        crumb: [
                            {
                                text: 'Dashboard',
                                href: '/dashboard'
                            },
                            {
                                text: 'Agents',
                                href: '/dashboard/agents'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':guid',
                            name: 'agent',
                            props: true,
                            component: agent,
                            meta: {
                                title: 'Agent',
                                crumb: [
                                    {
                                        text: 'Dashboard',
                                        href: '/dashboard'
                                    },
                                    {
                                        text: 'Agents',
                                        href: '/dashboard/agents'
                                    }
                                ],
                                requiresAuth: true
                            }
                        }
                    ]
                },
                {
                    path: 'runs',
                    name: 'runs',
                    component: runs,
                    meta: {
                        title: 'Runs',
                        crumb: [
                            {
                                text: 'Dashboard',
                                href: '/dashboard'
                            },
                            {
                                text: 'Runs',
                                href: '/dashboard/runs'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':owner/:name',
                            name: 'run',
                            props: true,
                            component: run,
                            meta: {
                                title: 'Run',
                                crumb: [
                                    {
                                        text: 'Dashboard',
                                        href: '/dashboard'
                                    },
                                    {
                                        text: 'Runs',
                                        href: '/dashboard/runs'
                                    }
                                ],
                                requiresAuth: true
                            }
                        }
                    ]
                }
            ]
        },
        {
            path: '*',
            name: '404',
            component: () =>
                import(
                    /* webpackChunkName: "about" */ './components/not-found.vue'
                ),
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
    if (to.name === 'dashboard') {
        await store.dispatch('user/loadProfile'); // refresh user profile
        to.meta.title = 'Dashboard';
    }
    if (to.name === 'workflow') {
        to.meta.title = `Workflow: ${to.params.name}`;
        while (to.meta.crumb.length > 2) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `${to.params.owner}/${to.params.name}`
        });
    }
    if (to.name === 'run') {
        to.meta.title = `Run: ${to.params.owner}/${to.params.name}`;
        while (to.meta.crumb.length > 2) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `${to.params.owner}/${to.params.name}`
        });
    }
    if (to.name === 'agent') {
        to.meta.title = `Agent: ${to.params.guid}`;
        while (to.meta.crumb.length > 2) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `${to.params.guid}`
        });
    }
    // if (to.name === 'dataset') to.meta.title = `Dataset: ${to.params.path}`;
    // if (to.name === 'artifact') to.meta.title = `Artifact: ${to.params.path}`;
    if (to.meta.name !== null) document.title = to.meta.title;
    // if (to.matched.some(record => record.name === 'workflow')) {
    //     while (to.meta.crumb.length > 0) to.meta.crumb.pop();
    //     // to.meta.crumb.push({
    //     //     text: `Workflow: ${to.params.username}/${to.params.name}`,
    //     //     href: `/workflow/${to.params.username}/${to.params.name}`
    //     // });
    // }
    // if (to.matched.some(record => record.name === 'run')) {
    //     while (to.meta.crumb.length > 0) to.meta.crumb.pop();
    //     // to.meta.crumb.push({
    //     //     text: `Run: ${to.params.id}`,
    //     //     href: `/run/${to.params.id}`
    //     // });
    // }
    // if (to.matched.some(record => record.name === 'agent')) {
    //     while (to.meta.crumb.length > 0) to.meta.crumb.pop();
    //     to.meta.crumb.push({
    //         text: `Agent: ${to.params.name}`,
    //         href: `/agent/${to.params.name}`
    //     });
    // }
    // if (to.matched.some(record => record.name === 'user')) {
    //     while (to.meta.crumb.length > 0) to.meta.crumb.pop();
    //     to.meta.crumb.push({ text: 'Your Dashboard' });
    //     to.meta.crumb.push({
    //         text: `User: ${to.params.username}`,
    //         href: `/user/${to.params.username}`
    //     });
    // }
    // if (to.matched.some(record => record.name === 'dataset')) {
    //     while (to.meta.crumb.length > 0) to.meta.crumb.pop();
    //     to.meta.crumb.push({
    //         text: `Dataset: ${to.params.path}`,
    //         href: `/dataset/${to.params.path}`
    //     });
    // }
    // if (to.matched.some(record => record.name === 'artifact')) {
    //     while (to.meta.crumb.length > 0) to.meta.crumb.pop();
    //     to.meta.crumb.push({
    //         text: `Artifact: ${to.params.path}`,
    //         href: `/artifact/${to.params.path}`
    //     });
    // }
    if (to.meta.requiresAuth && !store.getters['user/profile'].loggedIn) {
        window.location.replace(
            process.env.VUE_APP_URL + '/apis/v1/idp/cyverse_login/'
        );
    } else next();
});

export default router;
