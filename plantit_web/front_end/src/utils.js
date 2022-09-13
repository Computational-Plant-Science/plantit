import axios from 'axios';
import * as Sentry from '@sentry/browser';

export function guid() {
    let d = new Date().getTime(); //Timestamp
    let d2 = (performance && performance.now && performance.now() * 1000) || 0; //Time in microseconds since page-load or 0 if unsupported
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16; //random number between 0 and 16
        if (d > 0) {
            //Use timestamp until depleted
            r = (d + r) % 16 | 0;
            d = Math.floor(d / 16);
        } else {
            //Use microseconds since page-load if supported
            r = (d2 + r) % 16 | 0;
            d2 = Math.floor(d2 / 16);
        }
        return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });
}

export class API {
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
