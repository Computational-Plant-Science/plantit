import axios from 'axios';
import * as Sentry from '@sentry/browser';
import Vue from 'vue';

export const agents = {
    namespaced: true,
    state: () => ({
        agents: [],
        loading: true,
    }),
    mutations: {
        setAgents(state, agents) {
            state.agents = agents;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        updateAgent(state, agent) {
            let i = state.agents.findIndex((a) => a.guid === agent.guid);
            if (i === -1) state.agents.unshift(agent);
            else Vue.set(state.agents, i, agent);
        },
    },
    actions: {
        async loadAll({ commit }) {
            commit('setLoading', true);
            await axios
                .get('/apis/v1/agents/')
                .then((response) => {
                    commit('setAgents', response.data.agents);
                    commit('setLoading', false);
                })
                .catch((error) => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },

        async load({ commit }, name) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/agents/${name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken,
                    },
                })
                .then((response) => {
                    commit('updateAgent', response.data);
                    commit('setLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    throw error;
                });
        },
        async refresh({ commit }, name) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/agents/${name}/refresh/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken,
                    },
                })
                .then((response) => {
                    commit('updateAgent', response.data);
                    commit('setLoading', false);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    throw error;
                });
        },
    },
    getters: {
        agent: (state) => (name) => {
            var found = state.agents.find((agent) => name === agent.name);
            return found !== undefined ? found : null;
        },
        agentsPermitted: (state) => (username) =>
            // return public agents, agents this user owns, and agents the user is guest authorized for
            state.agents.filter(
                (a) =>
                    a.public ||
                    a.user === username ||
                    a.users_authorized.some((u) => u.username === username)
            ),
        agentsLoading: (state) => state.loading,
    },
};
