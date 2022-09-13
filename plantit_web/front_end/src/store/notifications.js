import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const notifications = {
    namespaced: true,
    state: () => ({
        notifications: [],
        loading: true,
    }),
    mutations: {
        setAll(state, notifications) {
            state.notifications = notifications;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        addOrUpdate(state, notification) {
            let i = state.notifications.findIndex(
                (n) => n.id === notification.id
            );
            if (i === -1) state.notifications.unshift(notification);
            else Vue.set(state.notifications, i, notification);
        },
    },
    actions: {
        setLoading({commit}, loading) {
            commit('setLoading', loading)
        },
        async setAll({ commit }, notifications) {
            commit('setAll', notifications);
        },
        async loadAll({ commit, rootState }) {
            commit('setLoading', true);
            await axios
                .get(
                    `/apis/v1/notifications/${rootState.user.profile.djangoProfile.username}/`
                )
                .then((response) => {
                    var ids = [];
                    var notifications = Array.prototype.slice.call(
                        response.data.notifications
                    );

                    // filter unique?
                    notifications = notifications.filter(function (n) {
                        if (ids.indexOf(n.id) >= 0) return false;
                        ids.push(n.id);
                        return true;
                    });

                    // sort by last created
                    notifications.sort(function (a, b) {
                        return new Date(b.created) - new Date(a.created);
                    });

                    commit('setAll', notifications);
                    commit('setLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    if (error.response.status === 500) throw error;
                });
        },
        async addOrUpdate({ commit }, notification) {
            commit('addOrUpdate', notification);
        },
    },
    getters: {
        notification: (state) => (id) => {
            let found = state.notifications.find((n) => id === n.id);
            if (found !== undefined) return found;
            return state.notifications.find((n) => id === n.id);
        },
        notifications: (state) =>
            state.notifications === undefined ? [] : state.notifications,
        notificationsRead: (state) => state.notifications.filter((n) => n.read),
        notificationsUnread: (state) =>
            state.notifications.filter((n) => !n.read),
        notificationsLoading: (state) => state.loading,
    },
};
