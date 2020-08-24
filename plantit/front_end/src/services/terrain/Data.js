import axios from 'axios';
import * as Utils from '@/utils';
import * as Sentry from '@sentry/browser';

export default {
    list(token, path) {
        return axios
            .get(
                `https://de.cyverse.org/terrain/filesystem/directory?path=${path}`,
                { headers: Utils.to_header(token) }
            )
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    },
    createDirectory(token, path) {
        return axios
            .post(
                'https://de.cyverse.org/terrain/secured/filesystem/directory/create',
                { path: path },
                { headers: Utils.to_header(token) }
            )
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    },
    uploadFile(token, path, file) {
        return axios
            .post(
                `https://de.cyverse.org/terrain/secured/fileio/upload?dest=${path}`,
                { file: file },
                { headers: Utils.to_header(token) }
            )
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    },
    remove(token, paths) {
        axios
            .post(
                'https://de.cyverse.org/terrain/secured/filesystem/delete',
                { paths: paths },
                { headers: Utils.to_header(token) }
            )
            .then(response => response.data)
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
    }
};
