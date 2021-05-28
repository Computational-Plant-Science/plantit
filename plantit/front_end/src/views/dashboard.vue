<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <div v-if="profileLoading">
            <b-row>
                <b-col class="text-center">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </b-col>
            </b-row>
        </div>
        <div v-else>
            <b-row
                ><b-col align-self="middle"
                    ><h1 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Welcome, {{ profile.cyverseProfile.first_name }}
                    </h1></b-col
                ><b-col md="auto" align-self="middle"
                    ><b-button
                        class="mt-1"
                        @click="toggleDarkMode"
                        :title="
                            profile.darkMode
                                ? 'Switch to light mode'
                                : 'Switch to dark mode'
                        "
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        v-b-tooltip:hover
                        ><b-spinner
                            small
                            v-if="togglingDarkMode"
                            label="Loading..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="ml-2 mb-1"
                        ></b-spinner
                        ><i v-else-if="profile.darkMode" class="fas fa-moon"></i
                        ><i v-else class="fas fa-sun"></i></b-button></b-col
            ></b-row>
            <hr class="mt-2 mb-2" style="border-color: gray" />
        </div>
        <b-row
            ><b-col md="auto" style="max-width: 15rem"
                ><b-button
                    class="m-1 text-left"
                    block
                    :variant="profile.darkMode ? 'dark' : 'light'"
                    to="/dashboard/workflows/"
                    ><i class="fas fa-stream fa-fw"></i> Workflows</b-button
                ><b-button
                    class="m-1 text-left"
                    block
                    :variant="profile.darkMode ? 'dark' : 'light'"
                    to="/dashboard/datasets/"
                    ><i class="fas fa-database fa-fw"></i> Datasets</b-button
                >
                <b-button
                    class="m-1 text-left"
                    block
                    :variant="profile.darkMode ? 'dark' : 'light'"
                    to="/dashboard/agents/"
                    ><i class="fas fa-server fa-fw"></i> Agents</b-button
                ><b-button
                    class="m-1 text-left"
                    block
                    :variant="profile.darkMode ? 'dark' : 'light'"
                    to="/dashboard/runs/"
                    ><i class="fas fa-terminal fa-fw"></i> Runs</b-button
                ></b-col
            ><b-col
                ><router-view
                    :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
                ></router-view></b-col
        ></b-row>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'dashboard',
    data: function() {
        return {
            togglingDarkMode: false
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('runs', ['runsLoading', 'runs']),
        ...mapGetters('notifications', ['notifications']),
        ...mapGetters('workflows', ['personal', 'personalLoading']),
        ...mapGetters('datasets', ['openedDataset', 'openedDatasetLoading'])
    },
    methods: {
        async toggleDarkMode() {
            this.togglingDarkMode = true;
            await this.$store.dispatch('user/toggleDarkMode');
            this.togglingDarkMode = false;
        }
    }
};
</script>

<style scoped></style>
