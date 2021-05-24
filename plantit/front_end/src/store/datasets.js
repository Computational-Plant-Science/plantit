import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const datasets = {
    namespaced: true,
    state: () => ({
        opened: null,
        openedSocket: null,
        loading: true
    }),
    mutations: {
        openSocket(state, guid) {
            let ws_protocol =
                location.protocol === 'https:' ? 'wss://' : 'ws://';
            state.openedSocket = new WebSocket(
                `${ws_protocol}${window.location.host}/ws/sessions/${guid}/`
            );
            state.openedSocket.onmessage = function(event) {
                let data = JSON.parse(event.data);
                state.opened = data.session;
            };
        },
        closeSocket(state) {
            state.openedSocket.close();
            state.openedSocket = null;
        },
        setOpened(state, opened) {
            state.opened = opened;
        },
        setLoading(state, loading) {
            state.loading = loading;
        }
    },
    actions: {
        async loadOpened({ commit }) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/datasets/opened/`)
                .then(response => {
                    commit('setOpened', response.data.session);
                    if (response.data.session !== null)
                        commit('openSocket', response.data.session.guid);
                    commit('setLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setOpened', null);
                    commit('setLoading', false);
                    throw error;
                });
        },
        updateOpened({ commit }, session) {
            commit('setOpened', session);
            commit('setLoading', false);
        },
        updateLoading({ commit }, loading) {
            commit('setLoading', loading);
        },
        async open({ commit }, payload) {
            commit('setLoading', true);
            let data = {
                resource: payload.resource.name,
                path: payload.path
            };

            axios({
                method: 'post',
                url: `/apis/v1/datasets/open/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    commit('setOpened', response.data.session);
                    commit('openSocket', response.data.session.guid);
                    commit('setLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    throw error;
                });
        },
        async closeOpened({ commit }) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/datasets/close/`)
                .then(() => {
                    commit('setOpened', null);
                    commit('closeSocket');
                    commit('setLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    throw error;
                });
        }
    },
    getters: {
        openedDataset: state => state.opened,
        openedDatasetLoading: state => state.loading
    }
};
