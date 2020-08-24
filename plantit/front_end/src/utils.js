import axios from "axios";
import * as Sentry from "@sentry/browser";

class API {
    url;
    constructor() {
        if (this.constructor === API) {
            throw new Error("Abstract classes can't be instantiated.");
        }
    }
    list() {
        return axios
            .get(this.url)
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
    create(data) {
        return axios
            .post(this.url, data)
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
    update(pk, data) {
        return axios
            .patch(`${this.url}/${pk}/`, data)
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
    get(pk) {
        return axios
            .get(`${this.url}/${pk}/`)
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
    delete(pk) {
        return axios
            .delete(`${this.url}/${pk}/`)
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
}

module.exports = {
    API,
    to_header(token) {
        return { Authorization: 'Bearer ' + token };
    }
};
