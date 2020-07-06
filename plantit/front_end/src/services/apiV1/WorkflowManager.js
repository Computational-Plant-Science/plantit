import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    getWorkflows() {
        return axios
            .get('/apis/v1/workflows/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    getWorkflow(owner, name) {
        return axios
            .get(`/apis/v1/workflows/${owner}/${name}/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    submitJob(workflow, pk, params) {
        return axios({
            method: 'post',
            url: `/apis/v1/workflows/${workflow}/submit/${pk}/`,
            data: params,
            headers: { 'Content-Type': 'application/json' }
        }).catch(err => {
            Sentry.captureException(err);
        });
    }
};
