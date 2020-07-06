import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';
import Guide from './views/Guide.vue';
import Docs from './views/Docs.vue';
import Workflows from './views/Workflows.vue';
import SubmitWorkflow from './views/SubmitWorkflow.vue';
import Jobs from './views/Jobs.vue';
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
                        href: '/',
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
                        href: '/',
                    },
                    {
                        text: 'About',
                        href: '/about',
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
                        href: '/',
                    },
                    {
                        text: 'Guide',
                        href: '/guide',
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
                        href: '/',
                    },
                    {
                        text: 'Docs',
                        href: '/docs',
                    }
                ]
            }
        },
        {
            path: '/login?next=/dashboard/',
            name: 'login',
            component: Login,
            meta: {
                crumb: [
                    {
                        text: 'Log In',
                        href: '/login/?next=/dashboard/',
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
                        href: '/logout',
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
                        href: '/',
                    },
                    {
                        text: 'Workflows',
                        href: '/workflows',
                    }
                ]
            }
        },
        {
            path: '/workflows/submit/:owner/:name',
            name: 'submit',
            props: true,
            component: SubmitWorkflow,
            meta: {
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/',
                    },
                    {
                        text: 'Workflows',
                        href: '/workflows',
                    }
                ]
            }
        },
        {
            path: '/jobs',
            name: 'jobs',
            component: Jobs,
            meta: {
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/',
                    },
                    {
                        text: 'Jobs',
                        href: '/jobs',
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
                        href: '/',
                    },
                    {
                        text: 'Profile',
                        href: '/profile',
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
                        href: '/',
                    },
                    {
                        text: '404',
                    }
                ]
            }
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.name === 'submit') && to.meta.crumb[to.meta.crumb.length - 1].text !== 'Submit') {
        to.meta.crumb.push(
            {
                text: to.params.owner,
                href: `/workflows/${to.params.owner}`,
            },
            {
                text: to.params.name,
                href: `/workflows/${to.params.owner}/${to.params.name}`,
            },
            {
                text: 'Submit',
                href: `/workflows/${to.params.owner}/${to.params.name}/submit`,
            }
        );
    }
    if (from.matched.some(record => record.name === 'submit')) {
        to.meta.crumb = to.meta.crumb.slice(0, 2);
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
