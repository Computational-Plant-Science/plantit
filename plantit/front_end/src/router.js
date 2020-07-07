import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';
import Guide from './views/Guide.vue';
import Docs from './views/Docs.vue';
import Pipelines from './views/Pipelines.vue';
import StartPipeline from './views/StartPipeline.vue';
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
            path: '/login?next=/pipelines/',
            name: 'login',
            component: Login,
            meta: {
                crumb: [
                    {
                        text: 'Log In',
                        href: '/login/?next=/pipelines/'
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
            path: '/pipelines',
            name: 'pipelines',
            component: Pipelines,
            meta: {
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Pipelines',
                        href: '/pipelines'
                    }
                ]
            }
        },
        {
            path: '/pipelines/start/:owner/:name',
            name: 'start',
            props: true,
            component: StartPipeline,
            meta: {
                crumb: [
                    {
                        text: 'PlantIT',
                        href: '/'
                    },
                    {
                        text: 'Pipelines',
                        href: '/pipelines'
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
    if (
        to.matched.some(record => record.name === 'start') &&
        to.meta.crumb[to.meta.crumb.length - 1].text !== 'Start'
    ) {
        to.meta.crumb.push(
            {
                text: to.params.owner,
                href: `/pipelines/${to.params.owner}`
            },
            {
                text: to.params.name,
                href: `/pipelines/${to.params.owner}/${to.params.name}`
            },
            {
                text: 'Start',
                href: `/pipelines/${to.params.owner}/${to.params.name}/start`
            }
        );
    }
    if (from.matched.some(record => record.name === 'start')) {
        to.meta.crumb = to.meta.crumb.slice(0, 2);
    }
    if (
        to.matched.some(record => record.name === 'run') &&
        to.meta.crumb[to.meta.crumb.length - 1].text !== 'Run'
    ) {
        to.meta.crumb.push({
            text: to.params.id,
            href: `/runs/${to.params.id}`
        });
    }
    if (from.matched.some(record => record.name === 'run')) {
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
