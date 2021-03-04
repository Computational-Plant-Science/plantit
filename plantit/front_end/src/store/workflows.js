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
        setWorkflowsLoading(state, loading) {
            state.workflowsLoading = loading;
        },
        setWorkflowRecentlyRun(state, { name, config }) {
            state.workflowsRecentlyRun[name] = config;
        }
    },
    actions: {
        loadWorkflows({ commit }) {
            commit('setWorkflowsLoading', true);
            axios
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
        setWorkflowRecentlyRun({ commit }, payload) {
            commit('setWorkflowRecentlyRun', payload);
        }
    },
    getters: {
        workflow: state => (owner, name) => {
            return state.workflows.find(
                repo =>
                    owner === repo.repository.owner.login &&
                    name === repo.repository.name
            );
        },
        workflows: state => state.workflows,
        workflowsLoading: state => state.workflowsLoading,
        workflowsRecentlyRun: state => state.workflowsRecentlyRun
    }
};
