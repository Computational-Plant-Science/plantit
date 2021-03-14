import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const runs = {
    state: () => ({
        runs: [],
        loading: true
    }),
    mutations: {
        setRuns(state, runs) {
            state.runs = runs;
        },
        setRunsLoading(state, loading) {
            state.loading = loading;
        },
        updateRun(state, run) {
            let i = state.runs.findIndex(r => r.id === run.id);
            if (i === -1) state.runs.unshift(run);
            else Vue.set(state.runs, i, run);
        }
    },
    actions: {
        async loadRuns({ commit, rootState }) {
            commit('setRunsLoading', true);
            await Promise.all([
                axios
                    .get(
                        `/apis/v1/runs/${rootState.user.profile.djangoProfile.username}/get_by_user/`
                    )
                    .then(response => {
                        var ids = [];
                        var runs = Array.prototype.slice.call(response.data);

                        // filter unique?
                        runs = runs.filter(function(run) {
                            if (ids.indexOf(run.id) >= 0) return false;
                            ids.push(run.id);
                            return true;
                        });

                        // sort by last updated
                        runs.sort(function(a, b) {
                            return new Date(b.updated) - new Date(a.updated);
                        });

                        commit('setRuns', runs);
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    })
            ]);
            commit('setRunsLoading', false);
        },
        updateRun({ commit }, run) {
            commit('updateRun', run);
        },
        refreshRun({ commit }, id) {
            axios
                .get(`/apis/v1/runs/${id}/`)
                .then(response => {
                    commit('updateRun', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        }
    },
    getters: {
        run: state => id => {
            let found = state.runs.find(run => id === run.id);
            if (found !== undefined) return found;
            return null;
        },
        runs: state => (state.runs === undefined ? [] : state.runs),
        runsLoading: state => state.loading
    }
};
