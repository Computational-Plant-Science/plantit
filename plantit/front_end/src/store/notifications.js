import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const notifications = {
    state: () => ({
        unread: [],
        read: [],
        loading: true
    }),
    mutations: {
        setUnread(state, notifications) {
            this.unread = notifications;
        },
        setRead(state, notifications) {
            this.read = notifications;
        },
        setLoading(state, loading) {
            this.loading = loading;
        },
        update(state, notification) {
            if (notification.read) {
                state.unread = state.unread.filter(n => n.id !== notification.id);
                state.read.unshift(notification);
            } else {
                let i = state.unread.findIndex(n => n.id === notification.id);
                if (i === -1) state.unread.unshift(notification);
                else state.unread[state.unread.findIndex(n => n.id === notification.id)] = notification;
            }
        },
    },
    actions: {
        async loadNotifications({ commit, rootState }) {
            commit('setLoading', true);

            await axios
                .get(
                    `/apis/v1/notifications/${rootState.user.profile.djangoProfile.username}/get_by_user/?page=0`
                )
                .then(response => {
                    var ids = [];
                    var notifications = Array.prototype.slice.call(response.data);

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

                    commit('setUnread', notifications.filter(n => !n.read));
                    commit('setRead', notifications.filter(n => n.read));
                    commit('setLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    if (error.response.status === 500) throw error;
                });
        },
        async updateNotification({ commit }, notification) {
            commit('update', notification);
        },
    },
    getters: {
        notification: state => id => {
            let found = state.unread.find(n => id === n.id);
            if (found !== undefined) return found;
            return state.read.find(n => id === n.id);
        },
        notificationsLoading: state => state.loading,
        unreadNotifications: state =>
            state.unread === undefined ? [] : state.unread,
        readNotifications: state => (state.read === undefined ? [] : state.read)
    }
};
