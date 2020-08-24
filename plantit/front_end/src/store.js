import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import Cookies from 'js-cookie';

Vue.use(Vuex);

const users = {
    state: () => ({
        countries: [],
        universities: [],
        user: null,
        users: [],
        darkMode: false
    }),
    mutations: {
        setUser(state, user) {
            state.user = user;
        },
        setUsers(state, users) {
            state.users = users;
        },
        setCountries(state, countries) {
            state.countries = countries;
        },
        setUniversities(state, universities) {
            state.universities = universities;
        }
    },
    actions: {
        loadUser({ commit }) {
            axios
                .get('/apis/v1/users/retrieve/')
                .then(response => {
                    commit('setUser', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
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
                    throw error;
                });
        },
        loadCountriesAndUniversities({ commit }) {
            axios
                .all([
                    axios.get('/apis/v1/users/countries/'),
                    axios.get('/apis/v1/users/universities/')
                ])
                .then(
                    axios.spread((countries, universities) => {
                        commit('setCountries', countries.data);
                        commit('setUniversities', universities.data);
                    })
                )
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        updateUser(
            { commit },
            userName,
            firstName,
            lastName,
            country,
            institution,
            fieldOfStudy
        ) {
            const data = {
                first_name: firstName,
                last_name: lastName,
                profile: {
                    country: country,
                    institution: institution,
                    field_of_study: fieldOfStudy
                }
            };
            return axios
                .patch(`/apis/v1/users/${userName}/`, data)
                .then(response => {
                    commit('setUser', response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    },
    getters: {
        user: state => state.user,
        profile: state => state.user.profile,
        loggedIn: state => state.user !== null,
        profileIncomplete: state =>
            state.user.profile === null ||
            !(
                state.user.profile.country &&
                state.user.profile.institution &&
                state.user.profile.field_of_study
            )
    }
};

const releases = {
    state: () => ({
        version: null
    }),
    mutations: {
        setVersion(state, version) {
            state.version = version;
        }
    },
    actions: {
        loadVersion({ commit }) {
            axios
                .get(
                    'https://api.github.com/repos/Computational-Plant-Science/plantit/releases',
                    { to_header: { Accept: 'application/vnd.github.v3+json' } }
                )
                .then(response => {
                    commit('setVersion', response.data[0].tag_name);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    },
    getters: {
        version: state => state.version
    }
};

export default new Vuex.Store({
    state: () => ({
        csrfToken: Cookies.get(axios.defaults.xsrfCookieName)
    }),
    getters: {
        csrfToken: state => state.csrfToken
    },
    modules: {
        users,
        releases
    }
});
