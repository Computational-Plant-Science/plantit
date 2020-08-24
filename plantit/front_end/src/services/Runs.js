import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    list() {
        return axios
            .get('/apis/v1/runs/')
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    },
    get(id) {
        return axios
            .get(`/apis/v1/runs/${id}/`)
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                return error;
            });
    },
    start(params) {
        params['config']['api_url'] = '/apis/v1/runs/start/';
        return axios({
            method: 'post',
            url: `/apis/v1/runs/start/`,
            data: params,
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    },
    getStatus(id) {
        return axios
            .get(`/apis/v1/runs/${id}/status/`)
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                return error;
            });
    },
};
