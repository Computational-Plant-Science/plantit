import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const datasets = {
    namespaced: true,
    state: () => ({
        opened: null,
        openedSocket: null,
        public: [],
        publicLoading: true,
        personal: [],
        personalLoading: true,
        shared: [],
        sharedLoading: true,
        sharing: [],
        sharingLoading: true
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
        setOpened(state, dataset) {
            state.opened = dataset;
        },
        setPublic(state, datasets) {
            state.public = datasets;
        },
        setPersonal(state, datasets) {
            state.personal = datasets;
        },
        setShared(state, datasets) {
            state.shared = datasets;
        },
        setSharing(state, datasets) {
            state.sharing = datasets;
        },
        setPublicLoading(state, loading) {
            state.publicLoading = loading;
        },
        setPersonalLoading(state, loading) {
            state.personalLoading = loading;
        },
        setSharedLoading(state, loading) {
            state.sharedLoading = loading;
        },
        setSharingLoading(state, loading) {
            state.sharingLoading = loading;
        }
    },
    actions: {
        async loadPersonalDatasets({ commit, rootState }) {
            commit('setPersonalLoading', true);
            return axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/${rootState.user.profile.djangoProfile.username}/`,
                    {
                        headers: {
                            Authorization: `Bearer ${rootState.user.profile.djangoProfile.cyverse_token}`
                        }
                    }
                )
                .then(response => {
                    commit('setPersonal', response.data);
                    commit('setPersonalLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setPersonalLoading', true);
                    throw error;
                });
        },
        async loadPublicDatasets({ commit, rootState }) {
            commit('setPublicLoading', true);
            return axios
                .get(
                    'https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/shared',
                    {
                        headers: {
                            Authorization: `Bearer ${rootState.user.profile.djangoProfile.cyverse_token}`
                        }
                    }
                )
                .then(response => {
                    commit('setPublic', response.data);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setPublicLoading', true);
                    throw error;
                });
        },
        async loadSharedDatasets({ commit, rootState }) {
            commit('setSharedLoading', true);
            return axios
                .get(
                    'https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/',
                    {
                        headers: {
                            Authorization: `Bearer ${rootState.user.profile.djangoProfile.cyverse_token}`
                        }
                    }
                )
                .then(response => {
                    commit('setShared', response.data);
                    commit('setSharedLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setSharedLoading', true);
                    throw error;
                });
        },
        async loadSharingDatasets({ commit, rootState }) {
            commit('setSharingLoading', true);
            return axios
                .get('/apis/v1/datasets/sharing/', {
                    headers: {
                        Authorization: `Bearer ${rootState.user.profile.djangoProfile.cyverse_token}`
                    }
                })
                .then(response => {
                    commit('setSharing', response.data);
                    commit('setSharingLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setSharingLoading', true);
                    throw error;
                });
        },
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
        async close({ commit }) {
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
        personalDatasets: state => state.personal,
        publicDatasets: state => state.public,
        sharedDatasets: state => state.shared,
        sharingDatasets: state => state.sharing,
        personalDatasetsLoading: state => state.personalLoading,
        publicDatasetsLoading: state => state.publicLoading,
        sharedDatasetsLoading: state => state.sharedLoading,
        sharingDatasetsLoading: state => state.sharingLoading,
        openedDataset: state => state.opened,
        openedDatasetLoading: state => state.loading
    }
};
