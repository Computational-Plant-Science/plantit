import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const runs = {
    state: () => ({
        running: [],
        completed: [],
        loading: true
    }),
    mutations: {
        setRunning(state, runs) {
            state.running = runs;
        },
        setCompleted(state, runs) {
            state.completed = runs;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        update(state, run) {
            if (run.is_complete) {
                state.running = state.running.filter(r => r.guid !== run.guid);
                state.completed.unshift(run);
            } else {
                let i = state.running.findIndex(r => r.guid === run.guid);
                if (i === -1) state.running.unshift(run);
                else state.running[state.running.findIndex(r => r.guid === run.guid)] = run;
            }
        },
    },
    actions: {
        async loadRuns({ commit, rootState }) {
            commit('setLoading', true);

            // load running
            await Promise.all([
                axios
                    .get(
                        `/apis/v1/runs/${rootState.user.profile.djangoProfile.username}/get_by_user/?page=0&running=True`
                    )
                    .then(response => {
                        var ids = [];
                        var running = Array.prototype.slice.call(response.data);

                        // filter unique?
                        running = running.filter(function(run) {
                            if (ids.indexOf(run.id) >= 0) return false;
                            ids.push(run.id);
                            return true;
                        });

                        // sort by last updated
                        running.sort(function(a, b) {
                            return new Date(b.updated) - new Date(a.updated);
                        });

                        commit('setRunning', running);
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    }),
                axios
                    .get(
                        `/apis/v1/runs/${rootState.user.profile.djangoProfile.username}/get_by_user/?page=0&running=False`
                    )
                    .then(response => {
                        var ids = [];
                        var completed = Array.prototype.slice.call(response.data);

                        // filter unique?
                        completed = completed.filter(function(run) {
                            if (ids.indexOf(run.id) >= 0) return false;
                            ids.push(run.id);
                            return true;
                        });

                        // sort by last updated
                        completed.sort(function(a, b) {
                            return new Date(b.updated) - new Date(a.updated);
                        });

                        commit('setCompleted', completed);
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    })
            ]);

            commit('setLoading', false);
        },
        updateRun({ commit }, run) {
            commit('update', run);
        }
    },
    getters: {
        run: state => guid => {
            let found = state.running.find(r => guid === r.guid);
            if (found !== undefined) return found;
            return state.completed.find(run => guid === run.guid);
        },
        runningRuns: state =>
            state.running === undefined ? [] : state.running,
        completedRuns: state =>
            state.completed === undefined ? [] : state.completed,
        runsLoading: state => state.loading
    }
};
