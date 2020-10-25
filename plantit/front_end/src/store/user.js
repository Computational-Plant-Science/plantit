import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const user = {
    state: () => ({
        currentUserDjangoProfile: null,
        currentUserCyVerseProfile: null,
        currentUserGitHubProfile: null,
        keycloak: null,
        darkMode: false
    }),
    getters: {
        keycloak: state => state.keycloak,
        darkMode: state => state.darkMode,
        currentUserDjangoProfile: state => state.currentUserDjangoProfile,
        currentUserCyVerseProfile: state => state.currentUserCyVerseProfile,
        currentUserGitHubProfile: state => state.currentUserGitHubProfile,
        loggedIn: state => state.currentUserDjangoProfile !== null
    },
    mutations: {
        setDarkMode(state, mode) {
            state.darkMode = mode;
        },
        setCurrentUserDjangoProfile(state, profile) {
            state.currentUserDjangoProfile = profile;
        },
        setCurrentUserCyVerseProfile(state, profile) {
            state.currentUserCyVerseProfile = profile;
        },
        setCurrentUserGitHubProfile(state, profile) {
            state.currentUserGitHubProfile = profile;
        }
    },
    actions: {
        toggleDarkMode({ commit }) {
            axios
                .get('/apis/v1/users/toggle_dark_mode/')
                .then(resp => {
                    commit('setDarkMode', resp.data['dark_mode']);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        loadCurrentUser({ commit }) {
            axios
                .get('/apis/v1/users/retrieve/')
                .then(django => {
                    commit('setCurrentUserDjangoProfile', django.data);
                    if (django.data.profile.cyverse_token !== '')
                        axios
                            .get(
                                `https://de.cyverse.org/terrain/secured/user-info?username=${django.data.username}`,
                                {
                                    headers: {
                                        Authorization:
                                            'Bearer ' +
                                            django.data.profile.cyverse_token
                                    }
                                }
                            )
                            .then(cyverse => {
                                commit(
                                    'setCurrentUserCyVerseProfile',
                                    cyverse.data[django.data.username]
                                );
                                commit(
                                    'setDarkMode',
                                    django.data.profile.dark_mode
                                );
                            })
                            .catch(error => {
                                Sentry.captureException(error);
                                if (error.response.status === 500) throw error;
                            });
                    if (
                        django.data.profile.github_username !== '' &&
                        django.data.profile.github_token !== ''
                    )
                        axios
                            .get(
                                `https://api.github.com/users/${django.data.profile.github_username}`,
                                {
                                    headers: {
                                        Authorization:
                                            'Bearer ' +
                                            django.data.profile.github_token
                                    }
                                }
                            )
                            .then(github =>
                                commit(
                                    'setCurrentUserGitHubProfile',
                                    github.data
                                )
                            )
                            .catch(error => {
                                Sentry.captureException(error);
                                if (error.response.status === 500) throw error;
                            });
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        }
    }
};
