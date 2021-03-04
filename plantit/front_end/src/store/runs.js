import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const runs = {
    state: () => ({
        runs: [],
        runsLoading: true
    }),
    mutations: {
        setRuns(state, runs) {
            state.runs = runs;
        },
        setRunsLoading(state, loading) {
            state.runsLoading = loading;
        }
    },
    actions: {
        loadRuns({ commit, rootState }) {
            commit('setRunsLoading', true);
            return axios
                .get(
                    `/apis/v1/runs/${rootState.profile.djangoProfile.username}/get_by_user/0/`
                )
                .then(response => {
                    var ids = [];
                    var runs = this.runs.concat(response.data);

                    // filter unique?
                    runs = this.runs.filter(function(run) {
                        if (ids.indexOf(run.id) >= 0) return false;
                        ids.push(run.id);
                        return true;
                    });

                    // sort by last updated
                    runs.sort(function(a, b) {
                        return new Date(b.updated) - new Date(a.updated);
                    });
                    commit('setRunsLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setRunsLoading', false);
                    throw error;
                });
        }
    },
    getters: {
        run: state => guid => {
            return state.runs.find(run => guid === run.guid);
        },
        runs: state => state.runs,
        runsLoading: state => state.runsLoading
    }
};
