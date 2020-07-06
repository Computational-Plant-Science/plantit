import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    getClusters() {
        return axios
            .get('/apis/v1/clusters/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
