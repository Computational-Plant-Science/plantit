import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    list() {
        return axios
            .get('/apis/v1/targets/')
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
};
