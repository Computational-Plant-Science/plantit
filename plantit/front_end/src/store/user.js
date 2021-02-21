import axios from 'axios';
import * as Sentry from '@sentry/browser';
import jwtDecode from 'jwt-decode';

export const user = {
    state: () => ({
        loggedIn: false,
        keycloak: null,
        darkMode: false,
        profile: {
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null
        },
    }),
    getters: {
        loggedIn: state => state.loggedIn,
        keycloak: state => state.keycloak,
        darkMode: state => state.darkMode,
        profile: state => state.profile,
    },
    mutations: {
        setLoggedIn(state, loggedIn) {
            state.loggedIn = loggedIn;
        },
        setDarkMode(state, mode) {
            state.darkMode = mode;
        },
        setDjangoProfile(state, profile) {
            state.profile.djangoProfile = profile;
        },
        setCyverseProfile(state, profile) {
            state.profile.cyverseProfile = profile;
        },
        setGithubProfile(state, profile) {
            state.profile.githubProfile = profile;
        }
    },
    actions: {
        async toggleDarkMode({ commit }) {
            return axios
                .get('/apis/v1/users/toggle_dark_mode/')
                .then(resp => {
                    commit('setDarkMode', resp.data['dark_mode']);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadCurrentUser({ commit }) {
            return axios
                .get('/apis/v1/users/retrieve/')
                .then(django => {
                    commit('setDjangoProfile', django.data);
                    if (django.data.profile.cyverse_token === '') {
                        commit('setLoggedIn', false);
                        //window.location.href = 'https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fkc.cyverse.org%2Fauth%2Frealms%2FCyVerse%2Faccount%2F';
                    }
                    if (django.data.profile.cyverse_token !== '') {
                        let decoded = jwtDecode(
                            django.data.profile.cyverse_token
                        );
                        let now = Math.floor(Date.now() / 1000);
                        if (now > decoded.exp) {
                            commit('setLoggedIn', false);
                            //window.location.href = 'https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fkc.cyverse.org%2Fauth%2Frealms%2FCyVerse%2Faccount%2F'
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
                                commit('setLoggedIn', true);
                                commit(
                                    'setCyverseProfile',
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
                                    'setGithubProfile',
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
