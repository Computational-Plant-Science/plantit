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
                            {{ publicContext ? 'Public' : 'Your' }} Datasets
                        </h2></b-col
                    ><b-col md="auto" align-self="center"
                        ><small>powered by</small
                        ><b-img
                            class="ml-2 mt-1"
                            rounded
                            style="max-height: 1.1rem;"
                            right
                            :src="
                                require('../../assets/logos/cyverse_bright.png')
                            "
                        ></b-img
                    ></b-col>
                    <b-col md="auto" class="ml-0" align-self="center"
                        ><b-button
                            :disabled="datasetsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            title="Refresh datasets"
                            @click="refreshDatasets"
                            class="ml-0 mt-0 mr-0"
                        >
                            <b-spinner
                                small
                                v-if="datasetsLoading"
                                label="Refreshing..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="mr-1"
                            ></b-spinner
                            ><i v-else class="fas fa-redo mr-1"></i
                            >Refresh</b-button
                        ></b-col
                    >
                    <b-col md="auto" align-self="center"
                        ><b-button
                            :disabled="datasetsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            class="ml-0 mt-0 mr-0"
                            @click="toggleContext"
                            :title="
                                publicContext
                                    ? 'View your datasets'
                                    : 'View public datasets'
                            "
                            v-b-tooltip:hover
                            ><span v-if="publicContext"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else
                                ><i class="fas fa-users"></i> Public</span
                            ></b-button
                        ></b-col
                    ></b-row
                >
                <b-row v-if="publicContext">
                    <b-col
                        ><b-row v-if="publicDatasetsLoading" class="text-center"
                            ><b-col
                                ><b-spinner
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner></b-col
                        ></b-row>
                        <b-row v-else>
                            <b-col>
                                <datatree
                                    :node="publicDatasets"
                                    select="directory"
                                    :upload="true"
                                    :download="true"
                                    :class="
                                        profile.darkMode
                                            ? 'theme-dark'
                                            : 'theme-light'
                                    "
                                ></datatree></b-col></b-row
                    ></b-col>
                </b-row>
                <b-tabs
                    v-else
                    v-model="activeTab"
                    nav-class="bg-transparent"
                    active-nav-item-class="bg-info text-dark"
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
                            <b>Personal</b>
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
                        <b-row
                            v-if="personalDatasetsLoading"
                            class="text-center"
                            ><b-col
                                ><b-spinner
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner></b-col
                        ></b-row>
                        <b-row v-else>
                            <b-col>
                                <datatree
                                    :node="personalDatasets"
                                    select="directory"
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
                        <b-row v-if="sharedDatasetsLoading" class="text-center"
                            ><b-col
                                ><b-spinner
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner></b-col
                        ></b-row>
                        <b-row v-else>
                            <b-col>
                                <datatree
                                    :node="sharedDatasets"
                                    select="directory"
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
                        <!--<b-row v-if="alertEnabled">
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
                        </b-row>-->
                        <b-row
                            v-if="
                                sharingDatasets === null ||
                                    sharingDatasets.length === 0
                            "
                            ><b-col class="text-danger">
                                You haven't shared any datasets with anyone.
                            </b-col></b-row
                        >
                        <div v-else>
                            <b-row
                                v-for="directory in sharingDatasets"
                                v-bind:key="directory.path"
                            >
                                <b-col
                                    ><small>{{ directory.path }}</small></b-col
                                ><b-col md="auto" class="mt-1">
                                    <small
                                        >Shared with
                                        {{ directory.guest }}</small
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
                        </div>
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
    data: function() {
        return {
            activeTab: 0,
            togglingContext: false,
            publicContext: false,
            yourDatasetsSearchText: '',
            sharedDatasetsSearchText: '',
            sharingDatasetsSearchText: ''
        };
    },
    async created() {
        await Promise.all([
            // this.$store.dispatch('datasets/loadPublic'),
            // this.$store.dispatch('datasets/loadPersonal'),
            // this.$store.dispatch('datasets/loadShared'),
            // this.$store.dispatch('datasets/loadSharing')
        ]);
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('datasets', [
            'personalDatasets',
            'publicDatasets',
            'sharedDatasets',
            'sharingDatasets',
            'personalDatasetsLoading',
            'publicDatasetsLoading',
            'sharedDatasetsLoading',
            'sharingDatasetsLoading',
            'openedDataset',
            'openedDatasetLoading'
        ]),
        datasetsLoading() {
            if (this.publicContext) {
                return this.publicDatasetsLoading;
            } else {
                switch (this.activeTab) {
                    case 0:
                        return this.personalDatasetsLoading;
                    case 1:
                        return this.sharedDatasetsLoading;
                    case 2:
                        return this.sharingDatasetsLoading;
                    default:
                        return false;
                }
            }
        },
        getDatasets() {
            if (this.publicContext) {
                return this.publicDatasets;
            } else {
                switch (this.activeTab) {
                    case 0:
                        return this.personalDatasets;
                    case 1:
                        return this.sharedDatasets;
                    case 2:
                        return this.sharingDatasets;
                    default:
                        return [];
                }
            }
        }
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        toggleContext() {
            this.togglingContext = true;
            this.publicContext = !this.publicContext;
            this.togglingContext = false;
        },
        async refreshDatasets() {
            if (this.publicContext)
                await this.$store.dispatch('datasets/loadPublic');
            else
                switch (this.activeTab) {
                    case 0:
                        await this.$store.dispatch(
                            'datasets/loadPersonal'
                        );
                        return;
                    case 1:
                        await this.$store.dispatch(
                            'datasets/loadShared'
                        );
                        return;
                    case 2:
                        await this.$store.dispatch(
                            'datasets/loadSharing'
                        );
                        return;
                }
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
                    this.loadSharing();
                    // this.alertMessage = `Unshared dataset ${
                    //     this.internalLoaded
                    //         ? this.internalNode.path
                    //         : this.node.path
                    // } with ${this.sharedUsers.length} user(s)`;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    // this.alertMessage = `Failed to unshare dataset ${
                    //     this.internalLoaded
                    //         ? this.internalNode.path
                    //         : this.node.path
                    // } with ${this.sharedUsers.length} user(s)`;
                    throw error;
                });
        }
    }
};
</script>

<style scoped></style>
