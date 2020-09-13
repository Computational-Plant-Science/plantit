import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    login(username, password) {
        return axios
            .post('/apis/v1/auth/login/', {
                username: username,
                password: password
            })
            .then(response => {
                return response;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    logout() {
        return axios
            .get('/apis/v1/auth/logout/')
            .then(response => {
                return response;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
