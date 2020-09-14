import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const users = {
    state: () => ({
        current: null,
        all: []
    }),
    getters: {
        allUsers: state => state.all
        // TODO add 'developers' (users who've contributed workflows)
    },
    mutations: {
        setAll(state, users) {
            state.all = users;
        }
    },
    actions: {
        loadAllUsers({ commit }) {
            axios
                .get('/apis/v1/users/')
                .then(response => {
                    commit('setAll', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        }
    }
};
