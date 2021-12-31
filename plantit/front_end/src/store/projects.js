import axios from 'axios';
import * as Sentry from '@sentry/browser';
import Vue from "vue";

export const projects = {
    namespaced: true,
    state: () => ({
        user: [],
        others: [],
        loading: true
    }),
    mutations: {
        setUser(state, projects) {
            state.user = projects;
        },
        setOthers(state, projects) {
            state.others = projects;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        addOrUpdate(state, project) {
            let i = state.user.findIndex(inv => inv.guid === project.guid);
            if (i === -1) state.user.unshift(project);
            else Vue.set(state.user, i, project);

            // let j = state.others.findIndex(inv => inv.guid === project.guid);
            // if (j === -1) state.others.unshift(project);
            // else Vue.set(state.others, j, project);
        },
    },
    actions: {
        async loadUser({ commit, rootState }) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/miappe/${rootState.user.profile.djangoProfile.username}/`)
                .then(response => {
                    commit('setUser', response.data.projects);
                    commit('setLoading', false);
                })
                .catch(error => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadOthers({ commit, rootState }) {
            commit('setLoading', true)
            await axios
                .get(`/apis/v1/miappe/?team=${rootState.user.profile.djangoProfile.username}`)
                .then(response => {
                    commit('setOthers', response.data.projects);
                    commit('setLoading', false);
                })
                .catch(error => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        setUser({commit}, projects) {
            commit('setUser', projects);
        },
        addOrUpdate({ commit }, projects) {
            commit('addOrUpdate', projects);
        }
    },
    getters: {
        userProjects: state => state.user,
        othersProjects: state => state.others,
        projectsLoading: state => state.loading,
    }
};
