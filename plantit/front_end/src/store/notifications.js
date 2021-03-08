import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const notifications = {
    state: () => ({
        unread: [],
        read: [],
        loading: true
    }),
    mutations: {
        setUnread(state, unread) {
            this.unread = unread;
        },
        setRead(state, read) {
            this.read = read;
        },
        setLoading(state, loading) {
            this.loading = loading;
        },
        add(state, notification) {
            state.unread.push(notification);
        },
        markRead(state, notification) {
            state.unread = state.unread.filter(
                n => n.guid !== notification.guid
            );
            state.read.push(notification);
        }
    },
    actions: {
        async loadNotifications({ commit, rootState }) {
            commit('setLoading', true);

            await axios
                .get(
                    `/apis/v1/notifications/${rootState.user.profile.djangoProfile.username}/get_by_user/?page=0`
                )
                .then(response => {
                    commit('setUnread', response.data.filter(n => !n.read));
                    commit('setRead', response.data.filter(n => n.read));
                    commit('setLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    if (error.response.status === 500) throw error;
                });
        },
        async addNotification({ commit }, notification) {
            commit('add', notification);
        },
        async markRead({ commit }, notification) {
            commit('markRead', notification);
        }
    },
    getters: {
        notification: state => guid => {
            let found = state.unread.find(n => guid === n.guid);
            if (found !== undefined) return found;
            return state.read.find(n => guid === n.guid);
        },
        notificationsLoading: state => state.loading,
        unreadNotifications: state =>
            state.unread === undefined ? [] : state.unread,
        readNotifications: state => (state.read === undefined ? [] : state.read)
    }
};
