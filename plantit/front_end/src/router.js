import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';
import Guide from './views/Guide.vue';
import Workflows from './views/Workflows.vue';
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
                        icon: '<i class="fas fa-home fa-1x text-dark align-middle:"></i>'
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
                        icon: '<i class="fas fa-home fa-1x text-dark align-middle:"></i>'
                    },
                    {
                        text: 'About',
                        href: '/about',
                        icon: '<i class="fas fa-seedling fa-1x text-dark align-middle"></i>'
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
                        icon: '<i class="fas fa-home fa-1x text-dark align-middle:"></i>'
                    },
                    {
                        text: 'Guide',
                        href: '/guide',
                        icon: '<i class="fas fa-map-signs fa-1x text-dark align-middle"></i>'
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
                        icon: '<i class="fas fa-door-open fa-1x text-dark align-middle"></i>'
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
                        icon: '<i class="fas fa-door-closed fa-1x text-dark align-middle"></i>'
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
                        icon: '<i class="fas fa-home fa-1x text-dark align-middle:"></i>'
                    },
                    {
                        text: 'Workflows',
                        href: '/workflows',
                        icon: '<i class="fas fa-stream fa-1x text-dark align-middle"></i>'
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
                        icon: '<i class="fas fa-home fa-1x text-dark align-middle:"></i>'
                    },
                    {
                        text: 'Jobs',
                        href: '/jobs',
                        icon: '<i class="fas fa-terminal fa-1x text-dark align-middle"></i>'
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
                        icon: '<i class="fas fa-home fa-1x text-dark align-middle:"></i>'
                    },
                    {
                        text: 'Profile',
                        href: '/profile',
                        icon: '<i class="fas fa-user fa-1x text-dark align-middle"></i>'
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
                        text: '404',
                        icon: '<i class="fas fa-question fa-1x text-dark align-middle"></i>'
                    }
                ]
            }
        }
    ]
});

router.beforeEach((to, from, next) => {
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
