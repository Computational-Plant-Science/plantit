import axios from 'axios';
import Cookies from 'js-cookie';
import * as Sentry from '@sentry/browser';

export default {
    login(username, password) {
        /**
         * Login the current session.
         *
         * Args:
         *    username (str): username
         *    password (str): password
         *
         * Returns:
         *    Axios promise containing the server response
         **/
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
        /**
         * Logout the current session.
         *
         * Returns:
         *    Axios promise containing the server response
         **/
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
        /**
         * Check if user is logged in.
         *
         * Warning:
         *    This is not a secure way to be sure the user is logged in.
         *    It should only be used to decide if to show/request data that
         *    requires authenication to access.
         *
         * Returns (bool):
         *    true if user is logged in, false otherwise.
         **/

        //The plant IT object is set by django's template system.
        // You can find the pipeline in public/index.html
        return plantIT.is_authenticated; // eslint-disable-line no-undef
    },

    getCSRFToken() {
        /**
         * Get the current CSRF Token for this session
         *
         * Returns:
         *     CSRF Toekn as a string
         **/
        return Cookies.get(axios.defaults.xsrfCookieName);
    }
};
