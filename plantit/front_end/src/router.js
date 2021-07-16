import Vue from 'vue';
import Router from 'vue-router';
import splash from './views/splash.vue';
import about from './views/about.vue';
import usage from './views/usage.vue';
import beta from './views/beta.vue';
import home from './views/home.vue';
import users from './components/users/users.vue';
import user from './components/users/user.vue';
import tasks from './components/tasks/tasks.vue';
import task from './components/tasks/task.vue';
import agents from './components/agents/agents.vue';
import agent from './components/agents/agent.vue';
import workflows from './components/workflows/workflows.vue';
import workflow from './components/workflows/workflow.vue';
import datasets from './components/datasets/datasets.vue';
import dataset from './components/datasets/dataset.vue';
import projects from './components/projects/projects.vue';
import project from './components/projects/project.vue';
import store from './store/store.js';

Vue.use(Router);

let router = new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/',
            name: 'splash',
            component: splash,
            meta: {
                title: 'PlantIT',
                crumb: [],
                requiresAuth: false
            }
        },
        {
            path: '/about',
            name: 'about',
            component: about,
            meta: {
                title: 'About PlantIT',
                crumb: [],
                requiresAuth: false
            }
        },
        {
            path: '/usage',
            name: 'usage',
            component: usage,
            meta: {
                title: 'PlantIT Usage',
                crumb: [],
                requiresAuth: false
            }
        },
        {
            path: '/beta',
            name: 'beta',
            component: beta,
            meta: {
                title: 'PlantIT Beta',
                crumb: [],
                requiresAuth: false
            }
        },
        {
            path: '/home',
            name: 'home',
            component: home,
            meta: {
                title: 'Home',
                crumb: [
                    {
                        text: 'Home',
                        href: '/home'
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
                                text: 'Home',
                                href: '/home'
                            },
                            {
                                text: 'Users',
                                href: '/home/users'
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
                                        text: 'Home',
                                        href: '/home'
                                    },
                                    {
                                        text: 'Users',
                                        href: '/home/users'
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
                                text: 'Home',
                                href: '/home'
                            },
                            {
                                text: 'Datasets',
                                href: '/home/datasets'
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
                                        text: 'Home',
                                        href: '/home'
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
                                text: 'Home',
                                href: '/home'
                            },
                            {
                                text: 'Workflows',
                                href: '/home/workflows'
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
                                        text: 'Home',
                                        href: '/home'
                                    },
                                    {
                                        text: 'Workflows',
                                        href: '/home/workflows'
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
                                text: 'Home',
                                href: '/home'
                            },
                            {
                                text: 'Agents',
                                href: '/home/agents'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':name',
                            name: 'agent',
                            props: true,
                            component: agent,
                            meta: {
                                title: 'Agent',
                                crumb: [
                                    {
                                        text: 'Home',
                                        href: '/home'
                                    },
                                    {
                                        text: 'Agents',
                                        href: '/home/agents'
                                    }
                                ],
                                requiresAuth: true
                            }
                        }
                    ]
                },
                {
                    path: 'tasks',
                    name: 'tasks',
                    component: tasks,
                    meta: {
                        title: 'Tasks',
                        crumb: [
                            {
                                text: 'Home',
                                href: '/home'
                            },
                            {
                                text: 'Tasks',
                                href: '/home/tasks'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':owner/:name',
                            name: 'task',
                            props: true,
                            component: task,
                            meta: {
                                title: 'Task',
                                crumb: [
                                    {
                                        text: 'Home',
                                        href: '/home'
                                    },
                                    {
                                        text: 'Tasks',
                                        href: '/home/tasks'
                                    }
                                ],
                                requiresAuth: true
                            }
                        }
                    ]
                },
                {
                    path: 'projects',
                    name: 'projects',
                    component: projects,
                    meta: {
                        title: 'Projects',
                        crumb: [
                            {
                                text: 'Home',
                                href: '/home'
                            },
                            {
                                text: 'Projects',
                                href: '/home/projects'
                            }
                        ],
                        requiresAuth: true
                    },
                    children: [
                        {
                            path: ':owner/:title',
                            name: 'project',
                            props: true,
                            component: project,
                            meta: {
                                title: 'Project',
                                crumb: [
                                    {
                                        text: 'Home',
                                        href: '/home'
                                    },
                                    {
                                        text: 'Projects',
                                        href: '/home/projects'
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
    if (to.name === 'home') {
        to.meta.title = 'Home';
    }
    if (to.name === 'workflow') {
        to.meta.title = `Workflow: ${to.params.name}`;
        while (to.meta.crumb.length > 2) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `${to.params.owner}/${to.params.name}`
        });
    }
    if (to.name === 'task') {
        to.meta.title = `Task: ${to.params.owner}/${to.params.name}`;
        while (to.meta.crumb.length > 2) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `${to.params.owner}/${to.params.name}`
        });
    }
    if (to.name === 'agent') {
        to.meta.title = `Agent: ${to.params.name}`;
        while (to.meta.crumb.length > 2) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `${to.params.name}`
        });
    }
    if (to.name === 'project') {
        to.meta.title = `Project: ${to.params.owner}/${to.params.title}`;
        while (to.meta.crumb.length > 2) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `${to.params.owner}/${to.params.title}`
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
    //     to.meta.crumb.push({ text: 'Your Home' });
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
