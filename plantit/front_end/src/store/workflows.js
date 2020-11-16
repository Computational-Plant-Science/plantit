import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const workflows = {
    state: () => ({
        workflows: [],
        lastFlow: null
    }),
    mutations: {
        setWorkflows(state, workflows) {
            state.workflows = workflows;
        },
        setLastFlow(state, flow) {
            state.lastFlow = flow;
        }
    },
    actions: {
        loadWorkflows({ commit, state }) {
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
        setLastFlow({ commit }, flow) {
            commit('setLastFlow', flow);
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
        lastFlow: state => state.lastFlow
    }
};
