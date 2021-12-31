import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const workflows = {
    namespaced: true,
    state: () => ({
        public: [],
        publicLoading: true,
        user: [],
        userLoading: true,
        org: {},
        orgLoading: true,
        project: {},
        projectLoading: true,
    }),
    mutations: {
        setPublic(state, workflows) {
            state.public = workflows;
        },
        setUser(state, workflows) {
            state.user = workflows;
        },
        setOrg(state, workflows) {
            state.org = workflows;
        },
        setProject(state, workflows) {
            state.project = workflows;
        },
        setPublicLoading(state, loading) {
            state.publicLoading = loading;
        },
        setUserLoading(state, loading) {
            state.userLoading = loading;
        },
        setOrgLoading(state, loading) {
            state.orgLoading = loading;
        },
        setProjectLoading(state, loading) {
            state.projectLoading = loading;
        },
        add(state, workflow) {
            state.user.push(workflow);
        },
        addOrUpdate(state, workflow) {
            // check public wfs
            let i = state.public.findIndex(
                (wf) =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (i === -1) state.public.unshift(workflow);
            else Vue.set(state.public, i, workflow);

            // check user wfs
            let j = state.user.findIndex(
                (wf) =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (j === -1) state.user.unshift(workflow);
            else Vue.set(state.user, j, workflow);

            // check org wfs
            Object.keys(state.org).forEach(function (key) {
                let k = state.org[key].findIndex(
                    (wf) =>
                        wf.repo.owner.login === workflow.repo.owner.login &&
                        wf.repo.name === workflow.repo.name
                );
                if (k === -1) state.org[key].unshift(workflow);
                else Vue.set(state.org[key], k, workflow);
            });

            // check project wfs
            Object.keys(state.project).forEach(function (key) {
                let k = state.project[key].findIndex(
                    (wf) =>
                        wf.repo.owner.login === workflow.repo.owner.login &&
                        wf.repo.name === workflow.repo.name
                );
                if (k === -1) state.project[key].unshift(workflow);
                else Vue.set(state.project[key], k, workflow);
            });
        },
        remove(state, owner, name) {
            // check public wfs
            let i = state.public.findIndex(
                (wf) => wf.repo.owner.login === owner && wf.repo.name === name
            );
            if (i > -1) state.public.splice(i, 1);

            // check private wfs
            let j = state.user.findIndex(
                (wf) => wf.repo.owner.login === owner && wf.repo.name === name
            );
            if (j > -1) state.user.splice(j, 1);

            // check org wfs
            Object.keys(state.org).forEach(function (key) {
                let k = state.org[key].findIndex(
                    (wf) =>
                        wf.repo.owner.login === owner && wf.repo.name === name
                );
                if (k > -1) state.org[key].splice(k, 1);
            });

            // check project wfs
            Object.keys(state.project).forEach(function (key) {
                let k = state.project[key].findIndex(
                    (wf) =>
                        wf.repo.owner.login === owner && wf.repo.name === name
                );
                if (k > -1) state.project[key].splice(k, 1);
            });
        },
    },
    actions: {
        async loadPublic({ commit }) {
            commit('setPublicLoading', true);
            await axios
                .get('/apis/v1/workflows/')
                .then((response) => {
                    commit('setPublic', response.data.workflows);
                    commit('setPublicLoading', false);
                })
                .catch((error) => {
                    commit('setPublicLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadUser({ commit }) {
            commit('setUserLoading', true);
            await axios
                .get(`/apis/v1/workflows/u/`)
                .then((response) => {
                    commit('setUser', response.data.workflows);
                    commit('setUserLoading', false);
                })
                .catch((error) => {
                    commit('setUserLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadOrg({ commit }) {
            commit('setOrgLoading', true);
            await axios
                .get(`/apis/v1/workflows/o/`)
                .then((response) => {
                    commit('setOrg', response.data.workflows);
                    commit('setOrgLoading', false);
                })
                .catch((error) => {
                    commit('setOrgLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadProject({ commit }) {
            commit('setProjectLoading', true);
            await axios
                .get(`/apis/v1/workflows/p/`)
                .then((response) => {
                    commit('setProject', response.data.workflows);
                    commit('setProjectLoading', false);
                })
                .catch((error) => {
                    commit('setProjectLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async setUser({ commit }, workflows) {
            commit('setUser', workflows);
        },
        async refreshPublic({ commit }) {
            commit('setPublicLoading', true);
            await axios
                .get('/apis/v1/workflows/?invalidate=True')
                .then((response) => {
                    commit('setPublic', response.data.workflows);
                    commit('setPublicLoading', false);
                })
                .catch((error) => {
                    commit('setPublicLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refreshOrg({ commit }) {
            commit('setOrgLoading', true);
            await axios
                .get(`/apis/v1/workflows/o/?invalidate=True`)
                .then((response) => {
                    commit('setOrg', response.data.workflows);
                    commit('setOrgLoading', false);
                })
                .catch((error) => {
                    commit('setOrgLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refreshProject({ commit }) {
            commit('setProjectLoading', true);
            await axios
                .get(`/apis/v1/workflows/p/?invalidate=True`)
                .then((response) => {
                    commit('setProject', response.data.workflows);
                    commit('setProjectLoading', false);
                })
                .catch((error) => {
                    commit('setProjectLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async refreshUser({ commit }) {
            commit('setUserLoading', true);
            await axios
                .get(`/apis/v1/workflows/u/?invalidate=True`)
                .then((response) => {
                    commit('setUser', response.data.workflows);
                    commit('setUserLoading', false);
                })
                .catch((error) => {
                    commit('setUserLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async load({ commit }, payload) {
            commit('setUserLoading', true);
            commit('setPublicLoading', true);
            await axios
                .get(
                    `/apis/v1/workflows/${payload.owner}/u/${payload.name}/${payload.branch}/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken,
                        },
                    }
                )
                .then((response) => {
                    commit('addOrUpdate', response.data);
                    commit('setUserLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setUserLoading', false);
                    commit('setPublicLoading', false);
                    throw error;
                });
        },
        async refresh({ commit }, payload) {
            commit('setUserLoading', true);
            commit('setPublicLoading', true);
            await axios
                .get(
                    `/apis/v1/workflows/${payload.owner}/u/${payload.name}/${payload.branch}/refresh/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken,
                        },
                    }
                )
                .then((response) => {
                    commit('addOrUpdate', response.data);
                    commit('setUserLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setUserLoading', false);
                    commit('setPublicLoading', false);
                    throw error;
                });
        },
    },
    getters: {
        workflow: (state) => (owner, name, branch) => {
            var found = state.public.find(
                (repo) =>
                    owner === repo.repo.owner.login &&
                    name === repo.repo.name &&
                    branch === repo.branch.name
            );
            if (found !== undefined) return found;
            found = state.user.find(
                (repo) =>
                    owner === repo.repo.owner.login &&
                    name === repo.repo.name &&
                    branch === repo.branch.name
            );
            if (found !== undefined) return found;
            for (let key in state.org) {
                found = state.org[key].find(
                    (repo) =>
                        owner === repo.repo.owner.login &&
                        name === repo.repo.name &&
                        branch === repo.branch.name
                );
                if (found !== null && found !== undefined) break;
            }
            for (let key in state.project) {
                found = state.project[key].find(
                    (repo) =>
                        owner === repo.repo.owner.login &&
                        name === repo.repo.name &&
                        branch === repo.branch.name
                );
                if (found !== null && found !== undefined) break;
            }
            return found !== undefined ? found : null;
        },
        publicWorkflows: (state) => state.public,
        publicWorkflowsLoading: (state) => state.publicLoading,
        userWorkflows: (state) => state.user,
        userWorkflowsLoading: (state) => state.userLoading,
        orgWorkflows: (state) => state.org,
        orgWorkflowsLoading: (state) => state.orgLoading,
        projectWorkflows: (state) => state.project,
        projectWorkflowsLoading: (state) => state.projectLoading,
    },
};
