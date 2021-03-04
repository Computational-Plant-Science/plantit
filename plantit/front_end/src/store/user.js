import axios from 'axios';
import * as Sentry from '@sentry/browser';
import jwtDecode from 'jwt-decode';

export const user = {
    state: () => ({
        profile: {
            loggedIn: false,
            keycloak: null,
            darkMode: false,
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null
        },
        profileLoading: true
    }),
    mutations: {
        setLoggedIn(state, loggedIn) {
            state.profile.loggedIn = loggedIn;
        },
        setDarkMode(state, mode) {
            state.profile.darkMode = mode;
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
        setProfileLoading(state, loading) {
            state.profileLoading = loading;
        }
    },
    actions: {
        async toggleDarkMode({ commit }) {
            return axios
                .get('/apis/v1/users/toggle_dark_mode/')
                .then(response => {
                    commit('setDarkMode', response.data['dark_mode']);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadProfile({ commit }) {
            commit('setProfileLoading', true);

            // fetch Django user profile
            return axios
                .get(`/apis/v1/users/get_current/`)
                .then(response => {
                    // set profile info
                    commit('setDjangoProfile', response.data.django_profile);
                    commit('setCyverseProfile', response.data.cyverse_profile);
                    commit('setGithubProfile', response.data.github_profile);

                    // set dark mode
                    commit(
                        'setDarkMode',
                        response.data.django_profile.dark_mode
                    );

                    // determine whether user is logged in
                    let decoded = jwtDecode(
                        response.data.django_profile.cyverse_token
                    );
                    let now = Math.floor(Date.now() / 1000);
                    if (now > decoded.exp) {
                        commit('setLoggedIn', false);
                    }

                    commit('setProfileLoading', false);
                })
                .catch(error => {
                    commit('setProfileLoading', false);
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        }
    },
    getters: {
        profile: state => state.profile,
        profileLoading: state => state.profileLoading
    }
};
