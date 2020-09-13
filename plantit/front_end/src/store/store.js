import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';
import Cookies from 'js-cookie';
import { users } from '@/store/users';
import { workflows } from '@/store/workflows';
import { data } from '@/store/data';

Vue.use(Vuex);

export default new Vuex.Store({
    state: () => ({
        csrfToken: Cookies.get(axios.defaults.xsrfCookieName)
    }),
    getters: {
        csrfToken: state => state.csrfToken
    },
    modules: {
        users,
        workflows,
        data
    }
});
