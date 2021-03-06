import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const runs = {
    state: () => ({
        running: [],
        completed: [],
        loading: true
    }),
    mutations: {
        setRunning(state, running) {
            state.running = running;
        },
        setCompleted(state, completed) {
            state.completed = completed;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        complete(state, run) {
            state.running = state.running.filter(r => r.guid !== run.guid);
            state.completed.push(run);
        }
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
        }
    },
    getters: {
        run: state => guid => {
            let running = state.running.find(run => guid === run.guid);
            if (running === undefined)
                return state.completed.find(run => guid === run.guid);
        },
        runningRuns: state =>
            state.running === undefined ? [] : state.running,
        completedRuns: state =>
            state.completed === undefined ? [] : state.completed,
        runsLoading: state => state.loading
    }
};
