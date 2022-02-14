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
        setFirst({ commit }, first) {
            commit('setFirst', first);
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
        logIn({ commit }) {
            commit('setLoggedIn', true);
        },
        async loadProfile({ commit }) {
            commit('setProfileLoading', true);
            await axios
                .get(`/apis/v1/users/get_current/`)
                .then(response => {
                    // determine whether user is logged in
                    let decoded = jwtDecode(response.data.django_profile.cyverse_token);
                    let now = Math.floor(Date.now() / 1000);
                    if (now > decoded.exp) commit('setLoggedIn', false);
                    else commit('setLoggedIn', true);

                    // determine whether user is logged into GitHub
                    commit('setLoggedIntoGithub', response.data.github_profile !== undefined && response.data.github_profile !== null);

                    // set profile info
                    commit('setDjangoProfile', response.data.django_profile);
                    commit('setCyverseProfile', response.data.cyverse_profile);
                    commit('setGithubProfile', response.data.github_profile);
                    commit('setOrganizations', response.data.organizations);
                    commit('setFirst', response.data.django_profile.first);
                    commit('setDarkMode', response.data.django_profile.dark_mode);
                    commit('setHints', response.data.django_profile.hints);
                    commit('setPushNotifications', response.data.django_profile.push_notifications);
                    commit('setStats', response.data.stats);
                    commit('setMaintenanceWindows', response.data.maintenance_windows);
                    commit('setProfileLoading', false);
                })
                .catch(error => {
                    commit('setProfileLoading', false);
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                    else if (error.response.status === 401 || error.response.status === 403) {
                        // if we get a 401 or 403, log the user out
                        sessionStorage.clear();
                        window.location.replace('/apis/v1/idp/cyverse_logout/');
                    }
                });
        }
    },
    getters: {
        profile: state => state.profile,
        profileLoading: state => state.profileLoading
    }
};
