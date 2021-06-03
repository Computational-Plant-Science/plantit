import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const tasks = {
    namespaced: true,
    state: () => ({
        tasks: [],
        loading: true
    }),
    mutations: {
        setAll(state, tasks) {
            state.tasks = tasks;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        update(state, task) {
            let i = state.tasks.findIndex(t => t.guid === task.guid);
            if (i === -1) state.tasks.unshift(task);
            else Vue.set(state.tasks, i, task);
        }
    },
    actions: {
        async loadAll({ commit, rootState }) {
            commit('setLoading', true);
            await Promise.all([
                axios
                    .get(
                        `/apis/v1/tasks/${rootState.user.profile.djangoProfile.username}/`
                    )
                    .then(response => {
                        var guids = [];
                        var tasks = Array.prototype.slice.call(response.data.tasks);

                        // filter unique?
                        tasks = tasks.filter(function(t) {
                            if (guids.indexOf(t.guid) >= 0) return false;
                            guids.push(t.guid);
                            return true;
                        });

                        // sort by last updated
                        tasks.sort(function(a, b) {
                            return new Date(b.updated) - new Date(a.updated);
                        });

                        commit('setAll', tasks);
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
                .get(`/apis/v1/tasks/${payload.owner}/${payload.name}/`)
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
        update({ commit }, task) {
            commit('update', task);
        }
    },
    getters: {
        task: state => (owner, name) => {
            let found = state.tasks.find(t => owner === t.owner && name === t.name);
            if (found !== undefined) return found;
            return null;
        },
        tasks: state => (state.tasks === undefined ? [] : state.tasks),
        tasksByOwner: state => owner => state.tasks.filter(t => owner === t.owner),
        tasksRunning: state => state.tasks.filter(t => !t.is_complete),
        tasksCompleted: state => state.tasks.filter(t => t.is_complete),
        tasksSucceeded: state => state.tasks.filter(t => t.is_success),
        tasksFailed: state => state.tasks.filter(t => t.is_failure),
        tasksLoading: state => state.loading
    }
};
