import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const tasks = {
    namespaced: true,
    state: () => ({
        tasks: [],
        delayed: [],
        repeating: [],
        triggered: [],
        loading: true,
        nextPage: 2,
    }),
    mutations: {
        setAll(state, tasks) {
            state.tasks = tasks;
        },
        setDelayed(state, tasks) {
            state.delayed = tasks;
        },
        setRepeating(state, tasks) {
            state.repeating = tasks;
        },
        setTriggered(state, tasks) {
            state.triggered = tasks;
        },
        addAll(state, tasks) {
            state.tasks = state.tasks.concat(tasks);
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        setNextPage(state, nextPage) {
            state.nextPage = nextPage;
        },
        addOrUpdate(state, task) {
            let i = state.tasks.findIndex((t) => t.guid === task.guid);
            if (i === -1) state.tasks.unshift(task);
            else Vue.set(state.tasks, i, task);

            // check if task.delayed_id or task.repeating_id matches any delayed or repeating tasks and remove them
            let j = state.delayed.findIndex((t) => t.name === task.delayed_id);
            if (j !== -1) state.delayed.splice(j, 1);
            let k = state.repeating.findIndex(
                (t) => t.name === task.repeating_id
            );
            if (k !== -1) state.repeating.splice(k, 1);
            let l = state.triggered.findIndex(
                (t) => t.name === task.triggered_id
            );
            if (l !== -1) state.triggered.splice(l, 1);
        },
        addDelayed(state, task) {
            state.delayed.unshift(task);
        },
        addRepeating(state, task) {
            state.repeating.unshift(task);
        },
        addTriggered(state, task) {
            state.triggered.unshift(task);
        },
    },
    actions: {
        setAll({ commit }, tasks) {
            commit('setAll', tasks);
        },
        setDelayed({ commit }, tasks) {
            commit('setDelayed', tasks);
        },
        setRepeating({ commit }, tasks) {
            commit('setRepeating', tasks);
        },
        setTriggered({ commit }, tasks) {
            commit('setTriggered', tasks);
        },
        setLoading({ commit }, loading) {
            commit('setLoading', loading);
        },
        async loadAll({ commit }) {
            commit('setLoading', true);
            await Promise.all([
                axios
                    .get(`/apis/v1/tasks/?page=1`)
                    .then((response) => {
                        var guids = [];
                        var tasks = Array.prototype.slice.call(
                            response.data.tasks
                        );

                        // filter unique?
                        tasks = tasks.filter(function (t) {
                            if (guids.indexOf(t.guid) >= 0) return false;
                            guids.push(t.guid);
                            return true;
                        });

                        // sort by last updated
                        tasks.sort(function (a, b) {
                            return new Date(b.updated) - new Date(a.updated);
                        });

                        commit('setAll', tasks);
                        commit('setNextPage', response.data.next_page);
                    })
                    .catch((error) => {
                        Sentry.captureException(error);
                        throw error;
                    }),
            ]);
            commit('setLoading', false);
        },
        async loadMore({ commit }, payload) {
            commit('setLoading', true);
            await Promise.all([
                axios
                    .get(`/apis/v1/tasks/?page=${payload.page}`)
                    .then((response) => {
                        var guids = [];
                        var tasks = Array.prototype.slice.call(
                            response.data.tasks
                        );

                        // filter unique?
                        tasks = tasks.filter(function (t) {
                            if (guids.indexOf(t.guid) >= 0) return false;
                            guids.push(t.guid);
                            return true;
                        });

                        // sort by last updated
                        tasks.sort(function (a, b) {
                            return new Date(b.updated) - new Date(a.updated);
                        });

                        commit('addAll', tasks);
                        commit('setNextPage', response.data.next_page);
                    })
                    .catch((error) => {
                        Sentry.captureException(error);
                        throw error;
                    }),
            ]);
            commit('setLoading', false);
        },
        async loadDelayed({ commit }) {
            commit('setLoading', true);
            await Promise.all([
                axios
                    .get(`/apis/v1/tasks/delayed/`)
                    .then((response) => {
                        commit('setDelayed', response.data.tasks);
                    })
                    .catch((error) => {
                        Sentry.captureException(error);
                        throw error;
                    }),
            ]);
            commit('setLoading', false);
        },
        async loadRepeating({ commit }) {
            commit('setLoading', true);
            await Promise.all([
                axios
                    .get(`/apis/v1/tasks/repeating/`)
                    .then((response) => {
                        commit('setRepeating', response.data.tasks);
                    })
                    .catch((error) => {
                        Sentry.captureException(error);
                        throw error;
                    }),
            ]);
            commit('setLoading', false);
        },
        async loadTriggered({ commit }) {
            commit('setLoading', true);
            await Promise.all([
                axios
                    .get(`/apis/v1/tasks/triggered/`)
                    .then((response) => {
                        commit('setTriggered', response.data.tasks);
                    })
                    .catch((error) => {
                        Sentry.captureException(error);
                        throw error;
                    }),
            ]);
            commit('setLoading', false);
        },
        refresh({ commit }, payload) {
            commit('setLoading', true);
            axios
                .get(`/apis/v1/tasks/${payload.guid}/`)
                .then((response) => {
                    commit('addOrUpdate', response.data);
                    commit('setLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    return error;
                });
        },
        addOrUpdate({ commit }, task) {
            commit('addOrUpdate', task);
        },
        addDelayed({ commit }, task) {
            commit('addDelayed', task);
        },
        addRepeating({ commit }, task) {
            commit('addRepeating', task);
        },
        addTriggered({ commit }, task) {
            commit('addTriggered', task);
        },
    },
    getters: {
        task: (state) => (guid) => {
            let found = state.tasks.find((t) => guid === t.guid);
            return found !== undefined ? found : null;
        },
        tasks: (state) => (state.tasks === undefined ? [] : state.tasks),
        tasksDelayed: (state) => state.delayed,
        tasksRepeating: (state) => state.repeating,
        tasksTriggered: (state) => state.triggered,
        tasksRunning: (state) => state.tasks.filter((t) => !t.is_complete),
        tasksCompleted: (state) => state.tasks.filter((t) => t.is_complete),
        tasksSucceeded: (state) => state.tasks.filter((t) => t.is_success),
        tasksFailed: (state) => state.tasks.filter((t) => t.is_failure),
        tasksLoading: (state) => state.loading,
        tasksNextPage: (state) => state.nextPage,
    },
};
