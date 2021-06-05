import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const workflows = {
    namespaced: true,
    state: () => ({
        public: [],
        publicLoading: true,
        personal: [],
        personalLoading: true,
        recentlyRun: {},
    }),
    mutations: {
        setPublic(state, workflows) {
            state.public = workflows;
        },
        setPersonal(state, workflows) {
            state.personal = workflows;
        },
        setPublicLoading(state, loading) {
            state.publicLoading = loading;
        },
        setPersonalLoading(state, loading) {
            state.personalLoading = loading;
        },
        setRecentlyRun(state, { name, config }) {
            state.recentlyRun[name] = config;
        },
        add(state, workflow) {
            state.personal.push(workflow);
        },
        addOrUpdate(state, workflow) {
            let i = state.public.findIndex(
                wf =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (i === -1) state.public.unshift(workflow);
            else Vue.set(state.public, i, workflow);

            let j = state.personal.findIndex(
                wf =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (j === -1) state.personal.unshift(workflow);
            else Vue.set(state.personal, j, workflow);
        },
        remove(state, workflow) {
            let i = state.public.findIndex(
                wf =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (i > -1) state.public.splice(i, 1);

            let j = state.personal.findIndex(
                wf =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (j > -1) state.personal.splice(j, 1);
        }
    },
    actions: {
        async loadPublic({ commit }) {
            commit('setPublicLoading', true);
            await axios
                .get('/apis/v1/workflows/')
                .then(response => {
                    commit('setPublic', response.data.workflows);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    commit('setPublicLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadPersonal({ commit }, owner) {
            commit('setPersonalLoading', true);
            await axios
                .get(`/apis/v1/workflows/${owner}/`)
                .then(response => {
                    commit('setPersonal', response.data.workflows);
                    commit('setPersonalLoading', false);
                })
                .catch(error => {
                    commit('setPersonalLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refreshPublic({ commit }) {
            commit('setPublicLoading', true);
            await axios
                .get('/apis/v1/workflows/?debounce=False')
                .then(response => {
                    commit('setPublic', response.data.workflows);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    commit('setPublicLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refreshPersonal({ commit }, owner) {
            commit('setPersonalLoading', true);
            await axios
                .get(`/apis/v1/workflows/${owner}/?debounce=False`)
                .then(response => {
                    commit('setPersonal', response.data.workflows);
                    commit('setPersonalLoading', false);
                })
                .catch(error => {
                    commit('setPersonalLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async load({ commit }, payload) {
            commit('setPersonalLoading', true);
            commit('setPublicLoading', true);
            await axios
                .get(`/apis/v1/workflows/${payload.owner}/${payload.name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    commit('addOrUpdate', response.data);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                    throw error;
                });
        },
        async refresh({ commit }, payload) {
            commit('setPersonalLoading', true);
            commit('setPublicLoading', true);
            await axios
                .get(
                    `/apis/v1/workflows/${payload.owner}/${payload.name}/refresh/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken
                        }
                    }
                )
                .then(response => {
                    commit('addOrUpdate', response.data);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                    throw error;
                });
        },
        add({ commit }, workflow) {
            commit('add', workflow);
        },
        addOrUpdate({ commit }, workflow) {
            commit('addOrUpdate', workflow);
        },
        remove({ commit }, workflow) {
            commit('remove', workflow);
        },
        setRecentlyRun({ commit }, workflow) {
            commit('setRecentlyRun', workflow);
        }
    },
    getters: {
        workflow: state => (owner, name) => {
            var found = state.public.find(
                repo =>
                    owner === repo.repo.owner.login && name === repo.repo.name
            );
            if (found !== undefined) return found;
            found = state.personal.find(
                repo =>
                    owner === repo.repo.owner.login && name === repo.repo.name
            );
            if (found !== undefined) return found;
            return null;
        },
        publicWorkflows: state => state.public,
        publicWorkflowsLoading: state => state.publicLoading,
        connectedWorkflows: state => state.personal.filter(repo => repo.connected),
        connectableWorkflows: state => state.personal.filter(repo => !repo.connected),
        personalWorkflowsLoading: state => state.personalLoading,
        recentlyRunWorkflows: state => state.recentlyRun
    }
};
