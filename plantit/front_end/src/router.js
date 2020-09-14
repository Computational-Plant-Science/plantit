import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';
import Guide from './views/Guide.vue';
import Docs from './views/Docs.vue';
import Data from './views/Data.vue';
import Workflows from './views/Workflows.vue';
import Workflow from './views/Workflow.vue';
import Runs from './views/Runs.vue';
import Run from './views/Run.vue';
import User from './views/User.vue';
import Users from './views/Users.vue';
import Login from './views/Login.vue';
import Logout from './views/Logout.vue';

Vue.use(Router);

let router = new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home,
            meta: {
                title: 'PlantIT',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    }
                ]
            }
        },
        {
            path: '/about',
            name: 'about',
            component: About,
            meta: {
                title: 'About',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'About',
                        href: '/about'
                    }
                ]
            }
        },
        {
            path: '/guide',
            name: 'guide',
            component: Guide,
            meta: {
                title: 'Guide',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Guide',
                        href: '/guide'
                    }
                ]
            }
        },
        {
            path: '/docs',
            name: 'docs',
            component: Docs,
            meta: {
                title: 'Docs',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Docs',
                        href: '/docs'
                    }
                ]
            }
        },
        {
            path: '/login?next=/workflows/',
            name: 'login',
            component: Login,
            meta: {
                title: 'Log In',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Log In',
                        href: '/login/?next=/workflows/'
                    }
                ]
            }
        },
        {
            path: '/logout',
            name: 'logout',
            component: Logout,
            meta: {
                title: 'Log Out',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Log Out',
                        href: '/logout'
                    }
                ]
            }
        },
        {
            path: '/data',
            name: 'data',
            component: Data,
            meta: {
                title: 'Data',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Data',
                        href: '/data'
                    }
                ]
            }
        },
        {
            path: '/workflows',
            name: 'workflows',
            component: Workflows,
            meta: {
                title: 'Workflows',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Workflows',
                        href: '/workflows'
                    }
                ]
            }
        },
        {
            path: '/workflows/:owner/:name',
            name: 'workflow',
            props: true,
            component: Workflow,
            meta: {
                title: '',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Workflows',
                        href: '/workflows'
                    }
                ]
            }
        },
        {
            path: '/runs',
            name: 'runs',
            component: Runs,
            meta: {
                title: 'Runs',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Runs',
                        href: '/runs'
                    }
                ]
            }
        },
        {
            path: '/runs/:id',
            name: 'run',
            props: true,
            component: Run,
            meta: {
                title: '',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Runs',
                        href: '/runs'
                    }
                ]
            }
        },
        {
            path: '/users',
            name: 'users',
            component: Users,
            meta: {
                title: '',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Users',
                        href: '/users'
                    }
                ],
            }
        },
        {
            path: '/users/:username',
            name: 'user',
            props: true,
            component: User,
            meta: {
                title: '',
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Users',
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
                import(
                    /* webpackChunkName: "about" */ './views/PageNotFound.vue'
                ),
            meta: {
                title: 'Not Found',
                crumb: [
                    {
                        text: 'PlantIT',
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
    if (to.name === 'workflow') {
        to.meta.title = `Workflow: ${to.params.name}`;
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
        if (to.meta.crumb.length === 3) {
            to.meta.crumb.pop();
        }
        to.meta.crumb.push({
            text: to.params.id,
            href: `/runs/${to.params.id}`
        });
    }
    if (to.matched.some(record => record.name === 'user')) {
        if (to.meta.crumb.length === 3) {
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
