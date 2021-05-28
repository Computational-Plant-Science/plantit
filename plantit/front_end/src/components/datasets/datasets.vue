<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <b-row
            ><b-col
                ><b-row
                    ><b-col
                        ><h2
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Your Datasets
                        </h2></b-col
                    ></b-row
                >
                <hr class="mt-2 mb-2" style="border-color: gray" />
                <b-tabs
                    nav-class="bg-transparent"
                    active-nav-item-class="bg-secondary text-dark"
                    pills
                >
                    <b-tab
                        :title-link-class="
                            profile.darkMode ? 'text-white' : 'text-dark'
                        "
                        :class="
                            profile.darkMode
                                ? 'theme-dark m-0 p-3'
                                : 'theme-light m-0 p-3'
                        "
                    >
                        <template #title>
                            <b>Yours</b>
                        </template>
                        <!--<b-row class="mb-2"
                                            ><b-col>
                                                <b-input-group size="sm">
                                                    <template #prepend>
                                                        <b-input-group-text>
                                                            Search
                                                        </b-input-group-text></template
                                                    ><b-form-input
                                                        :class="
                                                            profile.darkMode
                                                                ? 'theme-search-dark'
                                                                : 'theme-search-light'
                                                        "
                                                        size="lg"
                                                        type="search"
                                                        v-model="
                                                            yourDatasetsSearchText
                                                        "
                                                    ></b-form-input></b-input-group></b-col
                                        ></b-row>-->
                        <b-row>
                            <b-col>
                                <datatree
                                    :node="yourDatasets"
                                    select="directory"
                                    :upload="true"
                                    :download="true"
                                    :agents="agents"
                                    :class="
                                        profile.darkMode
                                            ? 'theme-dark'
                                            : 'theme-light'
                                    "
                                ></datatree></b-col></b-row
                    ></b-tab>
                    <b-tab
                        :title-link-class="
                            profile.darkMode ? 'text-white' : 'text-dark'
                        "
                        :class="
                            profile.darkMode
                                ? 'theme-dark m-0 p-3'
                                : 'theme-light m-0 p-3'
                        "
                    >
                        <template #title>
                            <b>Shared</b>
                        </template>
                        <!--<b-row class="mb-2"
                                            ><b-col>
                                                <b-input-group>
                                                    <template #prepend>
                                                        <b-input-group-text>
                                                            Search
                                                        </b-input-group-text></template
                                                    ><b-form-input
                                                        :class="
                                                            profile.darkMode
                                                                ? 'theme-search-dark'
                                                                : 'theme-search-light'
                                                        "
                                                        size="lg"
                                                        type="search"
                                                        v-model="
                                                            sharedDatasetsSearchText
                                                        "
                                                    ></b-form-input></b-input-group></b-col
                                        ></b-row>-->
                        <b-row>
                            <b-col>
                                <datatree
                                    :node="sharedDatasets"
                                    select="directory"
                                    :agents="agents"
                                    :upload="true"
                                    :download="true"
                                    :class="
                                        profile.darkMode
                                            ? 'theme-dark'
                                            : 'theme-light'
                                    "
                                ></datatree></b-col></b-row
                    ></b-tab>
                    <b-tab
                        :title-link-class="
                            profile.darkMode ? 'text-white' : 'text-dark'
                        "
                        :class="
                            profile.darkMode
                                ? 'theme-dark m-0 p-3'
                                : 'theme-light m-0 p-3'
                        "
                    >
                        <template #title>
                            <b>Sharing</b>
                        </template>
                        <!--<b-row class="mb-2"
                                            ><b-col>
                                                <b-input-group>
                                                    <template #prepend>
                                                        <b-input-group-text>
                                                            Search
                                                        </b-input-group-text></template
                                                    ><b-form-input
                                                        :class="
                                                            profile.darkMode
                                                                ? 'theme-search-dark'
                                                                : 'theme-search-light'
                                                        "
                                                        size="lg"
                                                        type="search"
                                                        v-model="
                                                            sharingDatasetsSearchText
                                                        "
                                                    ></b-form-input></b-input-group></b-col
                                        ></b-row>-->
                        <b-row v-if="alertEnabled">
                            <b-col class="m-0 p-0">
                                <b-alert
                                    :show="alertEnabled"
                                    :variant="
                                        alertMessage.startsWith('Failed')
                                            ? 'danger'
                                            : 'success'
                                    "
                                    dismissible
                                    @dismissed="alertEnabled = false"
                                >
                                    {{ alertMessage }}
                                </b-alert>
                            </b-col>
                        </b-row>
                        <b-row
                            v-for="directory in sharingDatasets"
                            v-bind:key="directory.path"
                        >
                            <b-col
                                ><small>{{ directory.path }}</small></b-col
                            ><b-col md="auto" class="mt-1">
                                <small
                                    >Shared with {{ directory.guest }}</small
                                ></b-col
                            ><b-col md="auto">
                                <b-button
                                    class="mb-2"
                                    size="sm"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'outline-dark'
                                    "
                                    @click="unshareDataset(directory)"
                                    ><i class="fas fa-user-lock fa-fw"></i>
                                    Unshare</b-button
                                ></b-col
                            ></b-row
                        >
                        <b-row v-if="sharingDatasets.length === 0"
                            ><b-col
                                ><p>
                                    <small class="text-danger"
                                        >You haven't shared any datasets with
                                        anyone.</small
                                    >
                                </p></b-col
                            ></b-row
                        >
                    </b-tab>
                </b-tabs></b-col
            ></b-row
        >
    </b-container>
</template>

<script>
import moment from 'moment';
import datatree from '@/components/datasets/data-tree.vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';

export default {
    name: 'datasets',
    components: {
        datatree
    },
    async created() {
        await Promise.all([
            this.loadDataset(
                `/iplant/home/${this.profile.djangoProfile.username}/`,
                this.profile.djangoProfile.cyverse_token
            ),
            this.loadSharedDatasets(),
            this.loadSharingDatasets()
        ]);
    },
    data: function() {
        return {
            yourDatasets: null,
            sharedDatasets: null,
            sharingDatasets: null,
            yourDatasetsSearchText: '',
            sharedDatasetsSearchText: '',
            sharingDatasetsSearchText: ''
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('datasets', ['openedDataset', 'openedDatasetLoading'])
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        async loadDataset(path, token) {
            return axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => {
                    this.yourDatasets = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadSharingDatasets() {
            await axios
                .get(`/apis/v1/datasets/sharing/`)
                .then(response => {
                    this.sharingDatasets = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadSharedDatasets() {
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        }
                    }
                )
                .then(response => {
                    this.sharedDatasets = response.data;
                    this.sharedDataLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.sharedDataLoading = false;
                    throw error;
                });
        },
        openDataset() {
            this.$store.dispatch('datasets/updateLoading', true);
            let data = { agent: this.agent.name };
            // if (this.mustAuthenticate)
            //     data['auth'] = {
            //         username: this.authenticationUsername,
            //         password: this.authenticationPassword
            //     };

            axios({
                method: 'post',
                url: `/apis/v1/datasets/open/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    await this.$store.dispatch(
                        'datasets/updateOpened',
                        response.data.session
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async unshareDataset(directory) {
            await axios({
                method: 'post',
                url: `/apis/v1/datasets/unshare/`,
                data: {
                    user: directory.guest,
                    path: directory.path,
                    role: directory.role
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(() => {
                    this.loadSharingDatasets();
                    this.alertMessage = `Unshared dataset ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to unshare dataset ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.alertEnabled = true;
                    throw error;
                });
        }
    }
};
</script>

<style scoped></style>
