import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const notifications = {
    state: () => ({
        notifications: [],
        loading: true
    }),
    mutations: {
        setNotifications(state, notifications) {
            state.notifications = notifications;
        },
        setNotificationsLoading(state, loading) {
            state.loading = loading;
        },
        updateNotification(state, notification) {
            let i = state.notifications.findIndex(
                n => n.id === notification.id
            );
            if (i === -1) state.notifications.unshift(notification);
            else Vue.set(state.notifications, i, notification);
        }
    },
    actions: {
        async loadNotifications({ commit, rootState }) {
            commit('setNotificationsLoading', true);
            await axios
                .get(
                    `/apis/v1/notifications/${rootState.user.profile.djangoProfile.username}/get_by_user/?page=0`
                )
                .then(response => {
                    var ids = [];
                    var notifications = Array.prototype.slice.call(
                        response.data
                    );

                    // filter unique?
                    notifications = notifications.filter(function(n) {
                        if (ids.indexOf(n.id) >= 0) return false;
                        ids.push(n.id);
                        return true;
                    });

                    // sort by last created
                    notifications.sort(function(a, b) {
                        return new Date(b.created) - new Date(a.created);
                    });

                    commit('setNotifications', notifications);
                    commit('setNotificationsLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setNotificationsLoading', false);
                    if (error.response.status === 500) throw error;
                });
        },
        async updateNotification({ commit }, notification) {
            commit('updateNotification', notification);
        }
    },
    getters: {
        notification: state => id => {
            let found = state.notifications.find(n => id === n.id);
            if (found !== undefined) return found;
            return state.notifications.find(n => id === n.id);
        },
        notifications: state => state.notifications === undefined ? [] : state.notifications,
        notificationsLoading: state => state.loading,
    }
};
