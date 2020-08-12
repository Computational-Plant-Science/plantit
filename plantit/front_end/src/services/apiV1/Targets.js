import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    listTargets() {
        return axios
            .get('/apis/v1/targets/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
