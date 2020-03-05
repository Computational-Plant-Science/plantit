import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    getWorkflows() {
        /**
         * Get Available stroage types.
         *
         * Returns:
         *    Axios promise containing returning an array of workflow objects
         **/
        return axios
            .get('/apis/v1/workflows/')
            .then(response => {
                return response.data.workflows;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },

    getParameters(workflow) {
        /**
         * Get workflow paramaters
         *
         * Args:
         *   workflow (str): app_name of workflow
         *
         * Returns:
         *    Axios promise containing returning the parameters
         **/
        return axios
            .get(`/apis/v1/workflows/${workflow}/`)
            .then(response => {
                return response.data.parameters;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },

    submitJob(workflow, pk, params) {
        return axios
            .post(`/apis/v1/workflows/${workflow}/submit/${pk}/`, params)
            .then(response => {
                return response;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
