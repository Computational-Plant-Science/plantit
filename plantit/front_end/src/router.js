import Vue from 'vue';
import Router from 'vue-router';
import home from './views/home.vue';
import workflows from './views/explore-workflows.vue';
import workflow from './views/workflow.vue';
import cluster from './views/cluster.vue';
import clusters from './views/clusters.vue';
import user from './views/user.vue';
import users from './views/users.vue';
import run from './views/run.vue';
import collection from './views/collection.vue';
import artifact from './views/artifact.vue';
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
            path: '/clusters',
            name: 'clusters',
            component: clusters,
            meta: {
                title: 'Clusters',
                crumb: [
                    {
                        text: 'Clusters',
                        href: '/clusters'
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
            path: '/cluster/:name',
            name: 'cluster',
            props: true,
            component: cluster,
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
            path: '/collection/:path',
            name: 'collection',
            props: true,
            component: collection,
            meta: {
                title: 'Collection',
                crumb: [],
                requiresAuth: true
            }
        },
        {
            path: '/artifact/:path',
            name: 'artifact',
            props: true,
            component: artifact,
            meta: {
                title: 'Artifact',
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
    if (to.name === 'workflow') to.meta.title = `Workflow: ${to.params.name}`;
    if (to.name === 'run') to.meta.title = `Run: ${to.params.id}`;
    if (to.name === 'cluster') to.meta.title = `Cluster: ${to.params.name}`;
    if (to.name === 'user') to.meta.title = `User: ${to.params.username}`;
    if (to.name === 'collection')
        to.meta.title = `Collection: ${to.params.path}`;
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
    if (to.matched.some(record => record.name === 'cluster')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Cluster: ${to.params.name}`,
            href: `/cluster/${to.params.name}`
        });
    }
    if (to.matched.some(record => record.name === 'user')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `User: ${to.params.username}`,
            href: `/user/${to.params.username}`
        });
    }
    if (to.matched.some(record => record.name === 'collection')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Collection: ${to.params.path}`,
            href: `/collection/${to.params.path}`
        });
    }
    if (to.matched.some(record => record.name === 'artifact')) {
        while (to.meta.crumb.length > 0) to.meta.crumb.pop();
        to.meta.crumb.push({
            text: `Artifact: ${to.params.path}`,
            href: `/artifact/${to.params.path}`
        });
    }

    await store.dispatch('loadProfile');

    if (to.meta.requiresAuth && !store.getters.profile.loggedIn) {
        window.location.replace(process.env.VUE_APP_URL + '/apis/v1/idp/cyverse_login/');
    } else next();
});

export default router;
