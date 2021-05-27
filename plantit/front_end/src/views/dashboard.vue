<template>
    <b-container
        fluid
        class="m-0 p-0"
        style="min-height: 98vh; background-color: transparent;"
    >
        <b-container class="p-3 vl" fluid style="background-color: transparent">
            <div v-if="profileLoading">
                <br />
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
            <div v-else>Welcome, {{ profile.cyverseProfile.first_name }}</div>
        </b-container>
        <router-view
            :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
        ></router-view>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'dashboard',
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('runs', ['runsLoading', 'runs']),
        ...mapGetters('notifications', ['notifications']),
        ...mapGetters('workflows', ['personal', 'personalLoading']),
        ...mapGetters('datasets', ['openedDataset', 'openedDatasetLoading'])
    }
};
</script>

<style scoped></style>
