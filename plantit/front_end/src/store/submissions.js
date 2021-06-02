import Vue from 'vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export const submissions = {
    namespaced: true,
    state: () => ({
        submissions: [],
        loading: true
    }),
    mutations: {
        setAll(state, submissions) {
            state.submissions = submissions;
        },
        setLoading(state, loading) {
            state.loading = loading;
        },
        update(state, submission) {
            let i = state.submissions.findIndex(
                sub => sub.guid === submission.guid
            );
            if (i === -1) state.submissions.unshift(submission);
            else Vue.set(state.submissions, i, submission);
        }
    },
    actions: {
        async loadAll({ commit, rootState }) {
            commit('setLoading', true);
            await Promise.all([
                axios
                    .get(
                        `/apis/v1/submissions/${rootState.user.profile.djangoProfile.username}/`
                    )
                    .then(response => {
                        var guids = [];
                        var submissions = Array.prototype.slice.call(
                            response.data.submissions
                        );

                        // filter unique?
                        submissions = submissions.filter(function(sub) {
                            if (guids.indexOf(sub.guid) >= 0) return false;
                            guids.push(sub.guid);
                            return true;
                        });

                        // sort by last updated
                        submissions.sort(function(a, b) {
                            return new Date(b.updated) - new Date(a.updated);
                        });

                        commit('setAll', submissions);
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    })
            ]);
            commit('setLoading', false);
        },
        refresh({ commit }, payload) {
            commit('setLoading', true);
            axios
                .get(`/apis/v1/submissions/${payload.owner}/${payload.name}/`)
                .then(response => {
                    commit('update', response.data);
                    commit('setLoading', false);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    commit('setLoading', false);
                    return error;
                });
        },
        update({ commit }, submission) {
            commit('update', submission);
        }
    },
    getters: {
        submission: state => (owner, name) => {
            let found = state.submissions.find(
                sub => owner === sub.owner && name === sub.name
            );
            if (found !== undefined) return found;
            return null;
        },
        submissions: state =>
            state.submissions === undefined ? [] : state.submissions,
        submissionsByOwner: state => owner => {
            return state.submissions.filter(sub => owner === sub.owner);
        },
        submissionsRunning: state =>
            state.submissions.filter(sub => !sub.is_complete),
        submissionsCompleted: state =>
            state.submissions.filter(sub => sub.is_complete),
        submissionsSucceeded: state =>
            state.submissions.filter(sub => sub.is_success),
        submissionsFailed: state =>
            state.submissions.filter(sub => sub.is_failure),
        submissionsLoading: state => state.loading
    }
};
