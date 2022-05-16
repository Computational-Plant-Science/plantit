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
            dirtMigrationStarted: null,
            dirtMigrationCompleted: null,
            dirtMigrationPath: null,
        },
        profileLoading: true,
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
        setProfileLoading(state, loading) {
            state.profileLoading = loading;
        },
        setDirtMigrationStarted(state, started) {
            state.profile.dirtMigrationStarted = started;
        },
        setDirtMigrationCompleted(state, completed) {
            state.profile.dirtMigrationCompleted = completed;
        },
        setDirtMigrationPath(state, path) {
            state.profile.dirtMigrationPath = path;
        },
    },
    actions: {
        async loadProfile({ commit }) {
            commit('setProfileLoading', true);
            await axios
                .get(`/apis/v1/users/get_current/`)
                .then((response) => {
                    // determine whether user is logged in
                    let decoded = jwtDecode(
                        response.data.django_profile.cyverse_token
                    );
                    let now = Math.floor(Date.now() / 1000);
                    if (now > decoded.exp) commit('setLoggedIn', false);
                    else commit('setLoggedIn', true);

                    // determine whether user is logged into GitHub
                    commit(
                        'setLoggedIntoGithub',
                        response.data.github_profile !== undefined &&
                            response.data.github_profile !== null
                    );

                    // set profile info
                    commit('setDjangoProfile', response.data.django_profile);
                    commit('setCyverseProfile', response.data.cyverse_profile);
                    commit('setGithubProfile', response.data.github_profile);
                    commit('setOrganizations', response.data.organizations);
                    commit('setFirst', response.data.django_profile.first);
                    commit(
                        'setDarkMode',
                        response.data.django_profile.dark_mode
                    );
                    commit('setHints', response.data.django_profile.hints);
                    commit(
                        'setPushNotifications',
                        response.data.django_profile.push_notifications
                    );
                    commit('setStats', response.data.stats);
                    commit(
                        'setDirtMigrationStarted',
                        response.data.django_profile.dirt_migration_started
                    );
                    commit(
                        'setDirtMigrationCompleted',
                        response.data.django_profile.dirt_migration_completed
                    );
                    commit(
                        'setDirtMigrationPath',
                        response.data.django_profile.dirt_migration_path
                    );
                    commit('setProfileLoading', false);
                })
                .catch((error) => {
                    commit('setProfileLoading', false);
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                    else if (
                        error.response.status === 401 ||
                        error.response.status === 403
                    ) {
                        // if we get a 401 or 403, log the user out
                        sessionStorage.clear();
                        window.location.replace('/apis/v1/idp/cyverse_logout/');
                    }
                });
        },
        setProfileLoading({ commit }, loading) {
            commit('setProfileLoading', loading);
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
                .then((response) => {
                    commit('setDarkMode', response.data['dark_mode']);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        setPushNotifications({ commit }, notif) {
            commit('setPushNotifications', notif);
        },
        async togglePushNotifications({ commit }) {
            await axios
                .get('/apis/v1/users/toggle_push_notifications/')
                .then((response) => {
                    commit(
                        'setPushNotifications',
                        response.data['push_notifications']
                    );
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        setHints({ commit }, hints) {
            commit('setHints', hints);
        },
        async toggleHints({ commit }) {
            await axios
                .get('/apis/v1/users/toggle_hints/')
                .then((response) => {
                    commit('setHints', response.data['hints']);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        setStats({ commit }, stats) {
            commit('setStats', stats);
        },
        setDirtMigrationStarted({ commit }, started) {
            commit('setDirtMigrationStarted', started);
        },
        setDirtMigrationCompleted({ commit }, completed) {
            commit('setDirtMigrationCompleted', completed);
        },
        setDirtMigrationPath({ commit }, path) {
            commit('setDirtMigrationPath', path);
        },
    },
    getters: {
        profile: (state) => state.profile,
        profileLoading: (state) => state.profileLoading,
    },
};
