import axios from 'axios';
import * as Sentry from '@sentry/browser';
import Vue from 'vue';

export const agents = {
    namespaced: true,
    state: () => ({
        public: [],
        publicLoading: true,
        personal: [],
        personalLoading: true
    }),
    mutations: {
        setPublic(state, datasets) {
            state.public = datasets;
        },
        setPersonal(state, datasets) {
            state.personal = datasets;
        },
        setPublicLoading(state, loading) {
            state.publicLoading = loading;
        },
        setPersonalLoading(state, loading) {
            state.personalLoading = loading;
        },
        add(state, agent) {
            state.personal.push(agent);
        },
        addOrUpdate(state, agent) {
            let i = state.public.findIndex(a => a.guid === agent.guid);
            if (i === -1) state.public.unshift(agent);
            else Vue.set(state.public, i, agent);

            let j = state.personal.findIndex(a => a.guid === agent.guid);
            if (j === -1) state.personal.unshift(agent);
            else Vue.set(state.personal, j, agent);
        },
        remove(state, agent) {
            let i = state.public.findIndex(a => a.guid === agent.guid);
            if (i > -1) state.public.splice(i, 1);

            let j = state.personal.findIndex(a => a.guid === agent.guid);
            if (j > -1) state.personal.splice(j, 1);
        }
    },
    actions: {
        async loadPublic({ commit }) {
            commit('setPublicLoading', true);
            await axios
                .get('/apis/v1/agents/?public=True')
                .then(response => {
                    commit('setPublic', response.data.agents);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    commit('setPublicLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadPersonal({ commit }, owner) {
            commit('setPersonalLoading', true);
            await axios
                .get(`/apis/v1/agents/?owner=${owner}`)
                .then(response => {
                    commit('setPersonal', response.data.agents);
                    commit('setPersonalLoading', false);
                })
                .catch(error => {
                    commit('setPersonalLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async setPersonal({ commit }, agents) {
            commit('setPersonal', agents);
        },
        async load({ commit }, name) {
            commit('setPersonalLoading', true);
            commit('setPublicLoading', true);
            await axios
                .get(`/apis/v1/agents/${name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    commit('update', response.data);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                    throw error;
                });
        },
        async refresh({ commit }, name) {
            commit('setPersonalLoading', true);
            commit('setPublicLoading', true);
            await axios
                .get(`/apis/v1/agents/${name}/refresh/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    commit('update', response.data);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setPersonalLoading', false);
                    commit('setPublicLoading', false);
                    throw error;
                });
        },
        add({ commit }, workflow) {
            commit('add', workflow);
        },
        addOrUpdate({ commit }, workflow) {
            commit('addOrUpdate', workflow);
        }
    },
    getters: {
        agent: state => name => {
            var found = state.public.find(agent => name === agent.name);
            if (found !== undefined) return found;
            found = state.personal.find(agent => name === agent.name);
            if (found !== undefined) return found;
            return null;
        },
        publicAgents: state => state.public,
        publicAgentsLoading: state => state.publicLoading,
        personalAgents: state => state.personal,
        personalAgentsLoading: state => state.personalLoading
    }
};
