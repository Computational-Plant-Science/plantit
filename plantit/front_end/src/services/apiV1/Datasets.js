import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    create(name, description) {
        return axios
            .post('/apis/v1/collections/create/', {
                name: name,
                description: description
            })
            .then(response => {
                return response;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    pin(owner, name, pinned) {
        return axios
            .post(
                pinned
                    ? `/apis/v1/collections/${owner}/${name}/pin/`
                    : `/apis/v1/collections/${owner}/${name}/unpin/`
            )
            .then(response => {
                return response.status === 200;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    listAll() {
        return axios
            .get('/apis/v1/collections/')
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    listByOwner(owner) {
        return axios
            .get(`/apis/v1/collections/${owner}/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    get(owner, name) {
        return axios
            .get(`/apis/v1/collections/${owner}/${name}/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    listMetadata(owner, name) {
        return axios
            .get(`/apis/v1/collections/${owner}/${name}/list_metadata/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    delete(owner, name) {
        return axios
            .delete(`/apis/v1/collections/${owner}/${name}/`)
            .then(response => {
                return response.status === 204;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    updateDescription(owner, name, description) {
        return axios
            .post(`/apis/v1/collections/${owner}/${name}/update_description/`, {
                description: description
            })
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    updateMetadata(owner, name, metadata) {
        return axios
            .post(`/apis/v1/collections/${owner}/${name}/update_metadata/`, {
                metadata: metadata
            })
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    listFiles(owner, name) {
        return axios
            .get(`/apis/v1/collections/${owner}/${name}/list_files/`)
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    listFilesForCustomIrodsConnection(username, password, host, port, zone, path) {
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
    uploadFiles(owner, name, files) {
        return axios
            .post(`/apis/v1/collections/${owner}/${name}/upload_files/`, {
                files: files
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    },
    deleteFiles(owner, name, files) {
        return axios
            .post(`/apis/v1/collections/${owner}/${name}/delete_files/`, {
                files: files
            })
            .then(response => {
                return response.data;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
