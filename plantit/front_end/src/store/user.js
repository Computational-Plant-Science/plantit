import axios from 'axios';
import * as Sentry from '@sentry/browser';
import jwtDecode from 'jwt-decode';

export const user = {
    namespaced: true,
    state: () => ({
        profile: {
            first: false,
            loggedIn: false,
            loggedIntoGitHub: false,
            keycloak: null,
            darkMode: false,
            pushNotifications: 'disabled',
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
            organizations: [],
            projects: [],
            hints: false,
            stats: null,
            maintenanceWindows: []
        },
        profileLoading: true
    }),
    mutations: {
        setFirst(state, first) {
            state.profile.first = first;
        },
        setLoggedIn(state, loggedIn) {
            state.profile.loggedIn = loggedIn;
        },
        setLoggedIntoGithub(state, loggedIn) {
            state.profile.loggedIntoGitHub = loggedIn;
        },
        setDarkMode(state, mode) {
            state.profile.darkMode = mode;
        },
        setPushNotifications(state, notifications) {
            state.profile.pushNotifications = notifications;
        },
        setDjangoProfile(state, profile) {
            state.profile.djangoProfile = profile;
        },
        setCyverseProfile(state, profile) {
            state.profile.cyverseProfile = profile;
        },
        setGithubProfile(state, profile) {
            state.profile.githubProfile = profile;
        },
        setOrganizations(state, organizations) {
            state.profile.organizations = organizations;
        },
        setHints(state, show) {
            state.profile.hints = show;
        },
        setStats(state, stats) {
            state.profile.stats = stats;
        },
        setMaintenanceWindows(state, windows) {
            state.profile.maintenanceWindows = windows;
        },
        setProfileLoading(state, loading) {
            state.profileLoading = loading;
        }
    },
    actions: {
        setProfileLoading({commit}, loading) {
            commit('setProfileLoading', loading)
        },
        setLoggedIn({ commit }, loggedIn) {
            commit('setLoggedIn', loggedIn);
        },
        setLoggedIntoGithub({ commit }, loggedIn) {
            commit('setLoggedIntoGithub', loggedIn);
        },
        setDjangoProfile({ commit }, profile) {
            commit('setDjangoProfile', profile);
        },
        setCyverseProfile({ commit }, profile) {
            commit('setCyverseProfile', profile);
        },
        setGithubProfile({ commit }, profile) {
            commit('setGithubProfile', profile);
        },
        setOrganizations({ commit }, orgs) {
            commit('setOrganizations', orgs);
        },
        setFirst({ commit }, first) {
            commit('setFirst', first);
        },
        setDarkMode({ commit }, darkMode) {
            commit('setDarkMode', darkMode);
        },
        async toggleDarkMode({ commit }) {
            await axios
                .get('/apis/v1/users/toggle_dark_mode/')
                .then(response => {
                    commit('setDarkMode', response.data['dark_mode']);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        setPushNotifications({commit}, notif) {
            commit('setPushNotifications', notif);
        },
        async togglePushNotifications({ commit }) {
            await axios
                .get('/apis/v1/users/toggle_push_notifications/')
                .then(response => {
                    commit(
                        'setPushNotifications',
                        response.data['push_notifications']
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        setHints({commit}, hints) {
            commit('setHints', hints);
        },
        async toggleHints({ commit }) {
            await axios
                .get('/apis/v1/users/toggle_hints/')
                .then(response => {
                    commit('setHints', response.data['hints']);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        setStats({commit}, stats) {
            commit('setStats', stats);
        },
        setMaintenanceWindows({commit}, windows) {
            commit('setMaintenanceWindows', windows);
        },
    },
    getters: {
        profile: state => state.profile,
        profileLoading: state => state.profileLoading
    }
};
