import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const runs = {
    namespaced: true,
    state: () => ({
        runs: [],
        loading: true
    }),
    mutations: {
        setAll(state, runs) {
            state.runs = runs;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        update(state, run) {
            let i = state.runs.findIndex(r => r.id === run.id);
            if (i === -1) state.runs.unshift(run);
            else Vue.set(state.runs, i, run);
        }
    },
    actions: {
        async loadAll({ commit, rootState }) {
            commit('setLoading', true);
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

                        commit('setAll', runs);
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    })
            ]);
            commit('setLoading', false);
        },
        refresh({ commit }, id) {
            axios
                .get(`/apis/v1/runs/${id}/`)
                .then(response => {
                    commit('update', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        update({ commit }, run) {
            commit('update', run);
        },
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
