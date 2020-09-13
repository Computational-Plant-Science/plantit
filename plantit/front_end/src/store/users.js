import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const users = {
    state: () => ({
        user: null,
        githubProfile: null,
        cyverseProfile: null,
        users: [],
        darkMode: false
    }),
    getters: {
        user: state => state.user,
        githubProfile: state => state.githubProfile,
        cyverseProfile: state => state.cyverseProfile,
        loggedIn: state => state.user !== null,
        darkMode: state => state.darkMode,
        users: state => state.users
    },
    mutations: {
        setUser(state, user) {
            state.user = user;
        },
        setGithubProfile(state, profile) {
            state.githubProfile = profile;
        },
        setCyverseProfile(state, profile) {
            state.cyverseProfile = profile;
        },
        setDarkMode(state, darkMode) {
            state.darkMode = darkMode;
        },
        setUsers(state, users) {
            state.users = users;
        }
    },
    actions: {
        loadUser({ commit }) {
            axios
                .get('/apis/v1/users/retrieve/')
                .then(response => {
                    commit('setUser', response.data);
                    if (response.data.profile.cyverse_token !== '')
                        axios
                            .get(
                                `https://de.cyverse.org/terrain/secured/user-info?username=${response.data.username}`,
                                {
                                    headers: {
                                        Authorization:
                                            'Bearer ' +
                                            response.data.profile.cyverse_token
                                    }
                                }
                            )
                            .then(r => {
                                commit(
                                    'setCyverseProfile',
                                    r.data[response.data.username]
                                );
                            })
                            .catch(error => {
                                Sentry.captureException(error);
                                throw error;
                            });
                    if (
                        response.data.profile.github_username !== '' &&
                        response.data.profile.github_token !== ''
                    )
                        axios
                            .get(
                                `https://api.github.com/users/${response.data.profile.github_username}`,
                                {
                                    headers: {
                                        Authorization:
                                            'Bearer ' +
                                            response.data.profile.github_token
                                    }
                                }
                            )
                            .then(r => {
                                commit('setGithubProfile', r.data);
                            })
                            .catch(error => {
                                Sentry.captureException(error);
                                throw error;
                            });
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        loadUsers({ commit }) {
            axios
                .get('/apis/v1/users/')
                .then(response => {
                    commit('setUsers', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        }
    }
};
