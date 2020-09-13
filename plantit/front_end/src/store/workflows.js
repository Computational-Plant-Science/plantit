import axios from 'axios';
import * as Utils from '@/utils';
import * as Sentry from '@sentry/browser';

export const workflows = {
    state: () => ({
        workflows: []
    }),
    mutations: {
        setWorkflows(state, workflows) {
            state.workflows = workflows;
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
        }
    }
};
