import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';
import Guide from './views/Guide.vue';
import Docs from './views/Docs.vue';
import Workflows from './views/Workflows.vue';
import Workflow from './views/Workflow.vue';
import Runs from './views/Runs.vue';
import Run from './views/Run.vue';
import Profile from './views/Profile.vue';
import Login from './views/Login.vue';
import Logout from './views/Logout.vue';
import Auth from '@/services/apiV1/Auth.js';

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
                crumb: [
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
                crumb: [
                    {
                        text: 'Log Out',
                        href: '/logout'
                    }
                ]
            }
        },
        {
            path: '/workflows',
            name: 'workflows',
            component: Workflows,
            meta: {
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
            path: '/profile',
            name: 'profile',
            component: Profile,
            meta: {
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Profile',
                        href: '/profile'
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
            },
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
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!Auth.isLoggedIn()) {
            window.location = '/login/?next=' + to.fullPath;
        } else {
            //User is logged in
            next();
        }
    } else {
        //No Auth required
        next();
    }
});

export default router;
