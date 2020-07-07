import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    list() {
        return axios
            .get('/apis/v1/runs/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    pin(pk, pinned) {
        let url = pinned
            ? `/apis/v1/jobs/${pk}/pin/`
            : `/apis/v1/jobs/${pk}/unpin/`;
        return axios
            .post(url)
            .then(response => {
                return response.status == 200;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    getRun(id) {
        return axios
            .get(`/apis/v1/runs/${id}/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    get(pk) {
        return axios
            .get(`/apis/v1/jobs/${pk}/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    delete(pk) {
        return axios
            .delete(`/apis/v1/jobs/${pk}/`)
            .then(response => {
                return response.status == 204;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    results(pk) {
        return `/apis/v1/jobs/${pk}/download_results/`;
    }
};
