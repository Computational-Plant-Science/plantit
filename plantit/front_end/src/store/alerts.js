export const alerts = {
    namespaced: true,
    state: () => ({
        alerts: [],
    }),
    mutations: {
        add(state, alert) {
            state.alerts.unshift(alert);
        },
        remove(state, alert) {
            let i = state.alerts.findIndex((a) => a.guid === alert.guid);
            if (i > -1) state.alerts.splice(i, 1);
        },
    },
    actions: {
        add({ commit }, alert) {
            commit('add', alert);
        },
        remove({ commit }, alert) {
            commit('remove', alert);
        },
    },
    getters: {
        alerts: (state) => state.alerts,
    },
};
