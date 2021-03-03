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
            let url =
                state.user.githubProfile !== undefined &&
                state.user.githubProfile &&
                state.user.githubProfile.username !== ''
                    ? `/apis/v1/workflows/${this.githubUser}/`
                    : '/apis/v1/workflows/list_all/';
            axios
                .get(url)
                .then(response => {
                    this.workflows = response.data.workflows;
                    this.loading = false;
                })
                .catch(error => {
                    this.loading = false;
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
            if (state.user.github_token !== '') {
                axios
                    .get(
                        `https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science+user:@me`,
                        {
                            headers: {
                                Authorization:
                                    'Bearer ' + state.user.github_token
                            }
                        }
                    )
                    .then(response => {
                        commit('setWorkflows', response.data);
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    });
            } else {
                return [];
            }
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
