import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const session = {
    state: () => ({
        session: null,
        loading: true
    }),
    mutations: {
        setSession(state, session) {
            state.session = session;
        },
        setSessionLoading(state, loading) {
            state.loading = loading;
        }
    },
    actions: {
        async loadSession({ commit }) {
            commit('setSessionLoading', true);
            await axios
                .get(`/apis/v1/sessions/current/`)
                .then(response => {
                    commit('setSession', response.data.session);
                    commit('setSessionLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setSession', null);
                    commit('setSessionLoading', false);
                    throw error;
                });
        },
        updateSession({ commit }, session) {
            commit('setSession', session);
            commit('setSessionLoading', false);
        },
        updateSessionLoading({ commit }, loading) {
            commit('setSessionLoading', loading);
        },
        async disconnectSession({ commit }) {
            commit('setSessionLoading', true);
            await axios
                .get(`/apis/v1/sessions/stop/`)
                .then(() => {
                    commit('setSession', null);
                    commit('setSessionLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setSession', null);
                    commit('setSessionLoading', false);
                    throw error;
                });
        }
    },
    getters: {
        session: state => state.session,
        sessionLoading: state => state.loading
    }
};
