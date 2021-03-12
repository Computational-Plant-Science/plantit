import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const workflows = {
    state: () => ({
        workflows: [],
        workflowsLoading: true,
        workflowsRecentlyRun: {}
    }),
    mutations: {
        setWorkflows(state, workflows) {
            state.workflows = workflows;
        },
        updateWorkflow(state, workflow) {
            let i = state.workflows.findIndex(
                wf =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (i === -1) state.workflows.unshift(workflow);
            else Vue.set(state.workflows, i, workflow);
        },
        setWorkflowsLoading(state, loading) {
            state.workflowsLoading = loading;
        },
        setWorkflowRecentlyRun(state, { name, config }) {
            state.workflowsRecentlyRun[name] = config;
        }
    },
    actions: {
        async loadWorkflows({ commit }) {
            commit('setWorkflowsLoading', true);
            await axios
                .get('/apis/v1/workflows/list_all/')
                .then(response => {
                    commit('setWorkflows', response.data.workflows);
                    commit('setWorkflowsLoading', false);
                })
                .catch(error => {
                    commit('setWorkflowsLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refreshWorkflow({ commit }, payload) {
            await axios
                .get(`/apis/v1/workflows/${payload.owner}/${payload.name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    commit('updateWorkflow', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        setWorkflowRecentlyRun({ commit }, payload) {
            commit('setWorkflowRecentlyRun', payload);
        }
    },
    getters: {
        workflow: state => (owner, name) => {
            let found = state.workflows.find(repo => owner === repo.repo.owner.login && name === repo.repo.name);
            if (found !== undefined) return found;
            return null;
        },
        workflows: state => state.workflows,
        workflowsLoading: state => state.workflowsLoading,
        workflowsRecentlyRun: state => state.workflowsRecentlyRun
    }
};
