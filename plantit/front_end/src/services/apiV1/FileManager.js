import axios from 'axios';
import * as Sentry from '@sentry/browser';

function pathJoin(parts) {
    /**
     * Joins names into a valid file path
     *
     * Args:
     *   parts (Array of strings): Names to join into a path.
     *
     * Returns:
     *   A string containing each element in parts with a single / between them.
     *   extra /s in the elements of parts are removed
     **/
    var replace = new RegExp('/' + '{1,}', 'g');
    return parts.join('/').replace(replace, '/');
}

export default {
    getStorageTypes() {
        /**
         * Get Available stroage types.
         *
         * Returns:
         *    Axios promise containing returning an array of storage types
         **/
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
            });
    },
    listDir(dir, storage_type) {
        /**
         * List folder contents in the format required by
         * jsTree  (https://www.jstree.com/docs/json/)
         *
         * Requirements:
         *   User must be logged in
         *   User must have permission to access dir
         *
         * Args:
         *    dir (str): path of directory to list,
         *    storage_type (str): The storage system to access
         **/
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
        /**
         * List folder contents in the format required by
         * jsTree  (https://www.jstree.com/docs/json/)
         *
         * Similar to listDir, except basePath and dir are combined
         * for the api call, then basePath is removed from the item.path
         * before it is returned.
         *
         * Requirements:
         *   User must be logged in
         *   User must have permission to access dir
         *
         * Args:
         *    basePath (str): The base path
         *    dir (str): path of directory to list,
         *    storage_type (str): The storage system to access
         **/
        return axios
            .get(`/apis/v1/files/lsdir/`, {
                params: {
                    path: pathJoin([basePath, dir]),
                    storage_type: storage_type
                }
            })
            .then(response => {
                return response.data.map(item => {
                    // //Make the base path follow the format sent by the back end server
                    // basePath = basePath.split('/')
                    //              .filter(value => value != "").join('/') + "/"
                    item.path = item.path.replace(basePath, '');
                    return item;
                });
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
