import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const workflows = {
    namespaced: true,
    state: () => ({
        workflows: [],
        workflowsLoading: true,
        workflowsRecentlyRun: {}
    }),
    mutations: {
        setAll(state, workflows) {
            state.workflows = workflows;
        },
        update(state, workflow) {
            let i = state.workflows.findIndex(
                wf =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (i === -1) state.workflows.unshift(workflow);
            else Vue.set(state.workflows, i, workflow);
        },
        setLoading(state, loading) {
            state.workflowsLoading = loading;
        },
        setRecentlyRun(state, { name, config }) {
            state.workflowsRecentlyRun[name] = config;
        }
    },
    actions: {
        async loadAll({ commit }) {
            commit('setLoading', true);
            await axios
                .get('/apis/v1/workflows/list_all/')
                .then(response => {
                    commit('setAll', response.data.workflows);
                    commit('setLoading', false);
                })
                .catch(error => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refreshAll({ commit }) {
            commit('setLoading', true);
            await axios
                .get('/apis/v1/workflows/refresh_all/')
                .then(response => {
                    commit('setAll', response.data.workflows);
                    commit('setLoading', false);
                })
                .catch(error => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refresh({ commit }, payload) {
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
                    commit('update', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        setRecentlyRun({ commit }, payload) {
            commit('setRecentlyRun', payload);
        }
    },
    getters: {
        workflow: state => (owner, name) => {
            let found = state.workflows.find(
                repo =>
                    owner === repo.repo.owner.login && name === repo.repo.name
            );
            if (found !== undefined) return found;
            return null;
        },
        workflows: state => state.workflows,
        workflowsLoading: state => state.workflowsLoading,
        workflowsRecentlyRun: state => state.workflowsRecentlyRun
    }
};
