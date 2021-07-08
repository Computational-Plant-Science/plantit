import axios from 'axios';
import * as Sentry from '@sentry/browser';
import Vue from "vue";

export const miappe = {
    namespaced: true,
    state: () => ({
        personal: [],
        others: [],
        loading: true
    }),
    mutations: {
        setPersonal(state, investigations) {
            state.personal = investigations;
        },
        setOthers(state, investigations) {
            state.others = investigations;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        addOrUpdate(state, investigation) {
            let i = state.personal.findIndex(inv => inv.unique_id === investigation.unique_id);
            if (i === -1) state.personal.unshift(investigation);
            else Vue.set(state.personal, i, investigation);

            let j = state.others.findIndex(inv => inv.unique_id === investigation.unique_id);
            if (j === -1) state.others.unshift(investigation);
            else Vue.set(state.others, j, investigation);
        },
    },
    actions: {
        async loadPersonal({ commit, rootState }) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/miappe/${rootState.user.profile.djangoProfile.username}/`)
                .then(response => {
                    commit('setPersonal', response.data.investigations);
                    commit('setLoading', false);
                })
                .catch(error => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadOthers({ commit, rootState }) {
            commit('setLoading', true);
            await axios
                .get(`/apis/v1/miappe/?team=${rootState.user.profile.djangoProfile.username}`)
                .then(response => {
                    commit('setOthers', response.data.investigations);
                    commit('setLoading', false);
                })
                .catch(error => {
                    commit('setLoading', false);
                    Sentry.captureException(error);
                    throw error;
                });
        },
        addOrUpdate({ commit }, investigation) {
            commit('addOrUpdate', investigation);
        }
    },
    getters: {
        personalInvestigations: state => state.personal,
        othersInvestigations: state => state.others,
        studies: state => state.studies
    }
};
