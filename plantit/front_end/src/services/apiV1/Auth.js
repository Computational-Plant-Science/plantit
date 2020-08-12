import axios from 'axios';
import Cookies from 'js-cookie';
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
    },
    isLoggedIn() {
        // Warning: this is not a secure way to determine whether the user is logged in.
        // It should only be used to determine whether to show/request data that requires authentication to access.
        // The plant IT object is set by django's template system.
        // You can find the pipeline in public/index.html.
        return plantIT.is_authenticated; // eslint-disable-line no-undef
    },
    getCSRFToken() {
        return Cookies.get(axios.defaults.xsrfCookieName);
    }
};
