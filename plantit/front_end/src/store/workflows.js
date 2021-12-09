import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const workflows = {
    namespaced: true,
    state: () => ({
        public: [],
        publicLoading: true,
        personal: [],
        personalLoading: true,
        org: {},
        orgLoading: true,
    }),
    mutations: {
        setPublic(state, workflows) {
            state.public = workflows;
        },
        setPersonal(state, workflows) {
            state.personal = workflows;
        },
        setOrg(state, workflows) {
            state.org = workflows;
        },
        setPublicLoading(state, loading) {
            state.publicLoading = loading;
        },
        setPersonalLoading(state, loading) {
            state.personalLoading = loading;
        },
        setOrgLoading(state, loading) {
            state.orgLoading = loading;
        },
        add(state, workflow) {
            state.personal.push(workflow);
        },
        addOrUpdate(state, workflow) {
            let i = state.public.findIndex(
                (wf) =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (i === -1) state.public.unshift(workflow);
            else Vue.set(state.public, i, workflow);

            let j = state.personal.findIndex(
                (wf) =>
                    wf.repo.owner.login === workflow.repo.owner.login &&
                    wf.repo.name === workflow.repo.name
            );
            if (j === -1) state.personal.unshift(workflow);
            else Vue.set(state.personal, j, workflow);

            Object.keys(state.org).forEach(function (key) {
                let k = state.org[key].findIndex(
                    (wf) =>
                        wf.repo.owner.login === workflow.repo.owner.login &&
                        wf.repo.name === workflow.repo.name
                );
                if (k === -1) state.org[key].unshift(workflow);
                else Vue.set(state.org[key], k, workflow);
            });

            // let k = state.org.findIndex(
            //     wf =>
            //         wf.repo.owner.login === workflow.repo.owner.login &&
            //         wf.repo.name === workflow.repo.name
            // );
            // if (k === -1) state.org.unshift(workflow);
            // else Vue.set(state.org, k, workflow);
        },
        remove(state, owner, name) {
            let i = state.public.findIndex(
                (wf) => wf.repo.owner.login === owner && wf.repo.name === name
            );
            if (i > -1) state.public.splice(i, 1);

            let j = state.personal.findIndex(
                (wf) => wf.repo.owner.login === owner && wf.repo.name === name
            );
            if (j > -1) state.personal.splice(j, 1);

            Object.keys(state.org).forEach(function (key) {
                let k = state.org[key].findIndex(
                    (wf) =>
                        wf.repo.owner.login === owner && wf.repo.name === name
                );
                if (k > -1) state.org[key].splice(k, 1);
            });

            // let k = state.org.findIndex(
            //     wf => wf.repo.owner.login === owner && wf.repo.name === name
            // );
            // if (k > -1) state.org.splice(k, 1);
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
        async loadPersonal({ commit }, owner) {
            commit('setPersonalLoading', true);
            await axios
                .get(`/apis/v1/workflows/${owner}/u/`)
                .then((response) => {
                    commit('setPersonal', response.data.workflows);
                    commit('setPersonalLoading', false);
                })
                .catch((error) => {
                    commit('setPersonalLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadOrg({ commit }, owner) {
            commit('setOrgLoading', true);
            await axios
                .get(`/apis/v1/workflows/${owner}/o/`)
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
        async setPersonal({ commit }, workflows) {
            commit('setPersonal', workflows);
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
        async refreshOrg({ commit }, owner) {
            commit('setOrgLoading', true);
            await axios
                .get(`/apis/v1/workflows/${owner}/o/?invalidate=True`)
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
        async refreshPersonal({ commit }, owner) {
            commit('setPersonalLoading', true);
            await axios
                .get(`/apis/v1/workflows/${owner}/u/?invalidate=True`)
                .then((response) => {
                    commit('setPersonal', response.data.workflows);
                    commit('setPersonalLoading', false);
                })
                .catch((error) => {
                    commit('setPersonalLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async load({ commit }, payload) {
            commit('setPersonalLoading', true);
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
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                    throw error;
                });
        },
        async refresh({ commit }, payload) {
            commit('setPersonalLoading', true);
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
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setPersonalLoading', false);
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
            found = state.personal.find(
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
            // Object.keys(state.org).forEach(function(key) {
            //     found = state.org[key].find(
            //         repo =>
            //             owner === repo.repo.organization &&
            //             name === repo.repo.name &&
            //             branch === repo.branch.name
            //     );
            // });

            // found = state.org.find(
            //     (repo) =>
            //         owner === repo.repo.owner.login &&
            //         name === repo.repo.name &&
            //         branch === repo.branch.name
            // );
            if (found !== undefined) return found;
            return null;
        },
        publicWorkflows: (state) => state.public,
        publicWorkflowsLoading: (state) => state.publicLoading,
        boundWorkflows: (state) =>
            state.personal.filter((workflow) => workflow.bound),
        bindableWorkflows: (state) =>
            state.personal
                .filter((workflow) => !workflow.bound)
                .sort(function (l, r) {
                    if (l.validation['is_valid'] && r.validation['is_valid'])
                        return 0;
                    else if (l.validation['is_valid']) return -1;
                    else return 1;
                }),
        // orgWorkflows: state => state.org.filter(workflow => workflow.bound),
        orgWorkflows: (state) => state.org,
        orgWorkflowsLoading: (state) => state.orgLoading,
        personalWorkflowsLoading: (state) => state.personalLoading,
    },
};
