import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';
import axios from 'axios';
import Cookies from 'js-cookie';
import { user } from '@/store/user';
import { users } from '@/store/users';
import { tasks } from '@/store/tasks';
import { alerts } from '@/store/alerts';
import { agents } from '@/store/agents';
import { projects } from '@/store/projects';
import { workflows } from '@/store/workflows';
import { datasets } from '@/store/datasets';
import { notifications } from '@/store/notifications';

Vue.use(Vuex);

const store = new Vuex.Store({
    plugins: [
        createPersistedState({
            storage: window.sessionStorage
        })
    ],
    state: () => ({
        csrfToken: Cookies.get(axios.defaults.xsrfCookieName)
    }),
    getters: {
        csrfToken: state => state.csrfToken
    },
    modules: {
        user,
        users,
        tasks,
        alerts,
        agents,
        projects,
        datasets,
        workflows,
        notifications
    }
});

export default store;
