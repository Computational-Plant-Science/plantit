import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    list() {
        return axios
            .get('/apis/v1/profiles/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    getCurrentUser() {
        return axios
            .get('/apis/v1/profiles/retrieve/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    getCurrentUserGithubUser() {
        return axios
            .get('/apis/v1/profiles/github_user/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    getCurrentUserGithubRepos() {
        return axios
            .get('/apis/v1/profiles/github_repos/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    getCountries() {
        return axios
            .get('/apis/v1/profiles/countries/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    getUniversities(country) {
        return axios
            .get('/apis/v1/profiles/universities/', {
                params: {
                    country: country
                }
            })
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    updateUserInfo(
        userName,
        firstName,
        lastName,
        country,
        continent,
        institution,
        institutionType,
        fieldOfStudy
    ) {
        const data = {
            first_name: firstName,
            last_name: lastName,
            profile: {
                country: country,
                continent: continent,
                institution: institution,
                institution_type: institutionType,
                field_of_study: fieldOfStudy
            }
        };
        return axios
            .patch(`/apis/v1/profiles/${userName}/`, data)
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
