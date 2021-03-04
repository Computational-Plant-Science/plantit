import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const workflows = {
    state: () => ({
        workflows: [],
        workflowConfigs: {}
    }),
    mutations: {
        setWorkflows(state, workflows) {
            state.workflows = workflows;
        },
        setWorkflowConfig(state, { name, config }) {
            state.workflowConfigs[name] = config;
        }
    },
    actions: {
        loadWorkflows({ commit, state }) {
            axios
                .get(
                    state.user.githubProfile !== undefined &&
                        state.user.githubProfile &&
                        state.user.githubProfile.username !== ''
                        ? `/apis/v1/workflows/${this.githubUser}/`
                        : '/apis/v1/workflows/list_all/'
                )
                .then(response => {
                    commit('setWorkflows', response.data.workflows);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        setWorkflowConfig({ commit }, payload) {
            commit('setWorkflowConfig', payload);
        }
    },
    getters: {
        workflows: state => state.workflows,
        workflow: state => (owner, name) => {
            return state.workflows.find(
                repo =>
                    owner === repo.repository.owner.login &&
                    name === repo.repository.name
            );
        },
        workflowConfigs: state => state.workflowConfigs
    }
};
