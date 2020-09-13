import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const data = {
    state: () => ({
        tree: {},
        hash: {},
    }),
    getters: {
        tree: state => state.tree
    },
    mutations: {
        setRootDirectory(state, path) {
            state.hash[path] = state.tree;
            state.tree = {
                path: path,
                children: []
            };
        },
        setDirectory(state, directory) {
            let path = directory.path;
            if (!(path in state.hash)) {
                let base = directory.path
                    .split('/')
                    .slice(0, -1)
                    .join('/');
                if (!(base in state.hash))
                    throw Error(`Parent directory ${base} does not exist`);
                state.hash[path] = { path: path };
            }

            state.hash[path].name = directory.name;
            state.hash[path].created = directory['date-created'];
            state.hash[path].modified = directory['date-modified'];
            state.hash[path].children = [];
            if ('folders' in directory) {
                for (const folder in directory.folders) {
                    state.hash[folder.path] = folder;
                    state.hash[path].children.append({
                        name: folder.label,
                        path: folder.path,
                        created: folder['date-created'],
                        modified: folder['date-modified'],
                        children: []
                    });
                }
            }
            if ('files' in directory) {
                for (const file in directory.folders) {
                    state.hash[file.path] = file;
                    state.hash[path].children.append({
                        name: file['label'],
                        path: file['path'],
                        created: file['date-created'],
                        modified: file['date-modified'],
                        size: file['size'],
                        md5: file['md5'],
                        type: file['content-type']
                    });
                }
            }
        },
        remove(state, path) {
            let base = path
                .split('/')
                .slice(0, -1)
                .join('/');
            if (!(base in state.hash))
                throw Error(`Parent directory ${base} does not exist`);
            delete state.hash[path];
        }
    },
    actions: {
        loadRootDirectory({ commit, dispatch }, path, token) {
            commit('setRoot', path);
            dispatch('loadDir', path, token);
        },
        loadDirectory({ commit }, path, token) {
            axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => commit('setDirectory', response.data))
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        addDirectory({ commit }, path, token) {
            axios
                .post(
                    'https://de.cyverse.org/terrain/secured/filesystem/directory/create',
                    { path: path },
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => commit('loadDirectory', response.data))
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        addFile({ dispatch }, path, file, token) {
            axios
                .post(
                    `https://de.cyverse.org/terrain/secured/fileio/upload?dest=${path}`,
                    { file: file },
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(() => {
                    dispatch(
                        'loadDirectory',
                        path
                            .split('/')
                            .slice(0, -1)
                            .join('/'),
                        token
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        remove({ commit, dispatch }, paths, token) {
            axios
                .post(
                    'https://de.cyverse.org/terrain/secured/filesystem/delete',
                    { paths: paths },
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => {
                    commit('remove', response.data.path);
                    dispatch(
                        'loadDirectory',
                        response.data.path
                            .split('/')
                            .slice(0, -1)
                            .join('/'),
                        token
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    }
};
