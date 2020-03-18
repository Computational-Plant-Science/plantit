import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    getCurrentUser() {
        /**
         * Get the current user's information.
         *
         * Requirements:
         *   User must be logged in
         *
         * Returns:
         *    Axios promise containing the current user's information
         **/
        return axios
            .get('/apis/v1/profiles/retrieve/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
}