import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const collections = {
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
        async loadCollectionSession({ commit }) {
            commit('setSessionLoading', true);
            await axios
                .get(`/apis/v1/collections/opened/`)
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
        updateCollectionSession({ commit }, session) {
            commit('setSession', session);
            commit('setSessionLoading', false);
        },
        updateCollectionSessionLoading({ commit }, loading) {
            commit('setSessionLoading', loading);
        },
        async closeCollectionSession({ commit }) {
            commit('setSessionLoading', true);
            await axios
                .get(`/apis/v1/collections/close/`)
                .then(() => {
                    commit('setSession', null);
                    commit('setSessionLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setSessionLoading', false);
                    throw error;
                });
        }
    },
    getters: {
        collectionSession: state => state.session,
        collectionSessionLoading: state => state.loading
    }
};
