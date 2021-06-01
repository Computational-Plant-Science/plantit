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
            let i = state.runs.findIndex(r => r.guid === run.guid);
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
                        `/apis/v1/runs/${rootState.user.profile.djangoProfile.username}/`
                    )
                    .then(response => {
                        var guids = [];
                        var runs = Array.prototype.slice.call(response.data);

                        // filter unique?
                        runs = runs.filter(function(run) {
                            if (guids.indexOf(run.guid) >= 0) return false;
                            guids.push(run.guid);
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
        refresh({ commit }, payload) {
            commit('setLoading', true);
            axios
                .get(`/apis/v1/runs/${payload.owner}/${payload.name}/`)
                .then(response => {
                    commit('update', response.data);
                    commit('setLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    return error;
                });
        },
        update({ commit }, run) {
            commit('update', run);
        },
    },
    getters: {
        searchRun: state => (owner, name) => {
            let found = state.runs.find(run => owner === run.owner && name === run.name);
            if (found !== undefined) return found;
            return null;
        },
        searchRuns: state => owner => {
            return state.runs.filter(run => owner === run.owner);
        },
        runs: state => (state.runs === undefined ? [] : state.runs),
        runsLoading: state => state.loading
    }
};
