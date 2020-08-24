import axios from 'axios';
import * as Utils from '@/utils';
import * as Sentry from '@sentry/browser';

export default {
    get(token, username) {
        return axios
            .get(`https://api.github.com/users/${username}`, {
                headers: Utils.to_header(token)
            })
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
};
