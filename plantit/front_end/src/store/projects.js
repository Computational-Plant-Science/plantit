import axios from 'axios';
import * as Sentry from '@sentry/browser';
import Vue from "vue";

export const projects = {
    namespaced: true,
    state: () => ({
        personal: [],
        others: [],
        loading: true
    }),
    mutations: {
        setPersonal(state, projects) {
            state.personal = projects;
        },
        setOthers(state, projects) {
            state.others = projects;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        addOrUpdate(state, project) {
            let i = state.personal.findIndex(inv => inv.unique_id === project.unique_id);
            if (i === -1) state.personal.unshift(project);
            else Vue.set(state.personal, i, project);

            let j = state.others.findIndex(inv => inv.unique_id === project.unique_id);
            if (j === -1) state.others.unshift(project);
            else Vue.set(state.others, j, project);
        },
    },
    actions: {
        async loadPersonal({ commit, rootState }) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/miappe/${rootState.user.profile.djangoProfile.username}/`)
                .then(response => {
                    commit('setPersonal', response.data.projects);
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
        addOrUpdate({ commit }, projects) {
            commit('addOrUpdate', projects);
        }
    },
    getters: {
        personalProjects: state => state.personal,
        othersProjects: state => state.others,
        projectsLoading: state => state.loading,
    }
};
