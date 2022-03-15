import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const users = {
    namespaced: true,
    state: () => ({
        users: [],
        usersLoading: true,
    }),
    mutations: {
        set(state, users) {
            state.users = users;
        },
        setLoading(state, loading) {
            state.usersLoading = loading;
        },
    },
    actions: {
        async loadAll({ commit }) {
            commit('setLoading', true);
            await axios
                .get('/apis/v1/users/get_all/')
                .then((response) => {
                    commit('set', response.data.users);
                    commit('setLoading', false);
                })
                .catch((error) => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        setAll({ commit }, users) {
            commit('set', users);
        },
    },
    getters: {
        allUsers: (state) => state.users,
        usersLoading: (state) => state.usersLoading,
        // TODO add 'developers' (users who've contributed workflows)
    },
};
