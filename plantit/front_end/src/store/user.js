import axios from 'axios';
import router from '../router';
import * as Sentry from '@sentry/browser';
import jwtDecode from 'jwt-decode';

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
                    if (django.data.profile.cyverse_token === '') {
                        router.push('/apis/v1/idp/cyverse_login/');
                    }
                    if (django.data.profile.cyverse_token !== '') {
                        let decoded = jwtDecode(
                            django.data.profile.cyverse_token
                        );
                        let now = Math.floor(Date.now() / 1000);
                        if (now > decoded.exp) {
                            window.location.href = 'https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fkc.cyverse.org%2Fauth%2Frealms%2FCyVerse%2Faccount%2F'
                        }
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
                    }
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
