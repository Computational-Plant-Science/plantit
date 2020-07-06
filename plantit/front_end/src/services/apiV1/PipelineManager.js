import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    list() {
        return axios
            .get('/apis/v1/pipelines/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    get(owner, name) {
        return axios
            .get(`/apis/v1/pipelines/${owner}/${name}/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    start(pipeline, pk, params) {
        return axios({
            method: 'post',
            url: `/apis/v1/pipelines/${pipeline}/start/${pk}/`,
            data: params,
            headers: { 'Content-Type': 'application/json' }
        }).catch(err => {
            Sentry.captureException(err);
        });
    }
};
