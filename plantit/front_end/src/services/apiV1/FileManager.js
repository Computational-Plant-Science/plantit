import axios from 'axios';
import * as Sentry from '@sentry/browser';

function pathJoin(parts) {
    var replace = new RegExp('/' + '{1,}', 'g');
    return parts.join('/').replace(replace, '/');
}

export default {
    getStorageTypes() {
        return axios
            .post('/apis/v1/files/storage_types')
            .then(response => {
                return response.data.storage_types;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    connectionInfo() {
        return axios
            .get(`/apis/v1/collections/connection_info/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    list(username, password, host, port, zone, path) {
        return axios
            .get(`/apis/v1/collections/list_files/`, {
                params: {
                    username: username,
                    password: password,
                    host: host,
                    port: port,
                    zone: zone,
                    path: path
                }
            })
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
                return err;
            });
    },
    listDir(dir, storage_type) {
        return axios
            .get(`/apis/v1/files/lsdir/`, {
                params: {
                    path: dir,
                    storage_type: storage_type
                }
            })
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    listDirBase(basePath, dir, storage_type) {
        return axios
            .get(`/apis/v1/files/lsdir/`, {
                params: {
                    path: pathJoin([basePath, dir]),
                    storage_type: storage_type
                }
            })
            .then(response => {
                return response.data.map(item => {
                    item.path = item.path.replace(basePath, '');
                    return item;
                });
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
