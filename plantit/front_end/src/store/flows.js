import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const flows = {
    state: () => ({
        flows: [],
        flowConfigs: {}
    }),
    mutations: {
        setFlows(state, flows) {
            state.flows = flows;
        },
        setFlowConfig(state, { name, config }) {
            state.flowConfigs[name] = config;
        }
    },
    actions: {
        loadFlows({ commit, state }) {
            let url = (state.user.githubProfile !== undefined && state.user.githubProfile && state.user.githubProfile.username !== '') ? `/apis/v1/flows/${this.githubUser}/` : '/apis/v1/flows/list_all/'
            axios
                .get(url)
                .then(response => {
                    this.flows = response.data.flows
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
                        commit('setFlows', response.data);
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    });
            } else {
                return [];
            }
        },
        setFlowConfig({ commit }, payload) {
            commit('setFlowConfig', payload);
        }
    },
    getters: {
        flows: state => state.flows,
        flow: state => (owner, name) => {
            return state.flows.find(
                repo =>
                    owner === repo.repository.owner.login &&
                    name === repo.repository.name
            );
        },
        flowConfigs: state => state.flowConfigs
    }
};
