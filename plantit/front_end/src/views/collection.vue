<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            profile.darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="p-3 vl">
            <b-row>
                <b-col>
                    <b-row align-h="center" v-if="collectionSessionLoading">
                        <b-spinner
                            type="grow"
                            label="Loading..."
                            variant="secondary"
                        ></b-spinner> </b-row
                    ><b-row v-else
                        ><b-col>
                            <h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                {{ collectionSession.path }}
                            </h4>
                            <small
                                >Open on
                                <b>{{ collectionSession.cluster }}</b></small
                            ><br />
                            <small
                                >Showing
                                <b class="mr-1"
                                    >{{
                                        this.totalFileCount < this.filesPerPage
                                            ? this.totalFileCount
                                            : this.filesPerPage
                                    }}
                                    of {{ data.files.length }}</b
                                >file(s),
                                <b class="mr-1">{{
                                    collectionSession.modified.length
                                }}</b
                                >modified</small
                            >
                        </b-col></b-row
                    ></b-col
                >
                <b-col md="auto" align-self="end">
                    <b-dropdown
                        dropleft
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        class="mb-2"
                    >
                        <template #button-content>
                            {{ viewMode }} View
                        </template>
                        <b-dropdown-item @click="setViewMode('Grid')"
                            >Grid</b-dropdown-item
                        >
                        <b-dropdown-item @click="setViewMode('Carousel')"
                            >Carousel</b-dropdown-item
                        > </b-dropdown
                    ><b-pagination
                        size="sm"
                        v-model="currentPage"
                        :per-page="filesPerPage"
                        :total-rows="totalFileCount"
                    ></b-pagination></b-col
            ></b-row>
            <br/>
            <b-row
                v-if="!dataLoading && data.files.length > 0"
                align-h="center"
                class="m-1"
            >
                <b-card-group
                    v-if="viewMode === 'Grid'"
                    deck
                    columns
                    class="justify-content-center"
                >
                    <b-card
                        :img-src="
                            `/apis/v1/collections/thumbnail/?path=${file.path}`
                        "
                        v-for="file in currentPageFiles"
                        v-bind:key="file.id"
                        style="min-width: 20rem;max-width: 20rem"
                        class="overflow-hidden mb-4"
                        :bg-variant="profile.darkMode ? 'dark' : 'white'"
                        :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                        border-variant="default"
                        :header-border-variant="
                            profile.darkMode ? 'secondary' : 'default'
                        "
                        :text-variant="profile.darkMode ? 'white' : 'dark'"
                    >
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            <b>{{ file.label }}</b>
                            <br />
                            <small
                                >{{
                                    `Last modified: ${prettifyShort(
                                        file['date-modified']
                                    )}`
                                }}
                            </small>
                        </p>
                        <hr />
                        <b-button
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            class="text-left m-0"
                            @click="annotateFile(file)"
                        >
                            <i class="fas fa-pen-fancy fa-fw"></i>
                            Annotate
                        </b-button>
                    </b-card>
                </b-card-group>
                <b-carousel v-else controls>
                    <b-carousel-slide
                        v-for="file in currentPageFiles"
                        v-bind:key="file.id"
                        :img-src="
                            `/apis/v1/collections/thumbnail/?path=${file.path}`
                        "
                        ><template #default
                            ><b-row
                                :class="
                                    profile.darkMode
                                        ? 'theme-container-dark p-3'
                                        : 'theme-container-light p-3'
                                "
                                style="opacity: 0.9;"
                            >
                                <b-col class="text-left">
                                    <h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        {{ file.label }}
                                    </h5>
                                    <small>{{
                                        `Last modified: ${prettifyShort(
                                            file['date-modified']
                                        )}`
                                    }}</small>
                                </b-col>
                                <b-col md="auto" align-self="end">
                                    <b-button
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        class="text-right m-0"
                                        @click="annotateFile(file)"
                                    >
                                        <i class="fas fa-pen-fancy fa-fw"></i>
                                        Annotate
                                    </b-button></b-col
                                >
                            </b-row></template
                        ></b-carousel-slide
                    >
                </b-carousel>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from 'moment';

export default {
    name: 'collection',
    data: function() {
        return {
            data: null,
            dataLoading: false,
            viewMode: 'Grid',
            collectionNotFound: false,
            currentFile: '',
            currentPage: 1,
            filesPerPage: 20
        };
    },
    async mounted() {
        await this.loadCollection();
        this.currentFile = this.data.files.length > 0 ? this.data.files[0] : '';
    },
    methods: {
        annotateFile() {},
        prettifyShort: function(date) {
            return `${moment(date).fromNow()}`;
        },
        setViewMode(mode) {
            this.viewMode = mode;
        },
        async loadCollection() {
            this.dataLoading = true;
            return await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${this.$router.currentRoute.params.path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        }
                    }
                )
                .then(response => {
                    this.data = response.data;
                    this.dataLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.dataLoading = false;
                    throw error;
                });
        }
    },
    computed: {
        ...mapGetters([
            'profile',
            'workflow',
            'workflowsRecentlyRun',
            'collectionSession',
            'collectionSessionLoading'
        ]),
        totalFileCount() {
            return this.dataLoading || this.data === null ? 0 : this.data.files.length;
        },
        currentPageFiles() {
            return this.dataLoading || this.data === null
                ? []
                : this.data.files.slice(this.currentPage, this.filesPerPage);
        }
    }
};
</script>

<style scoped></style>
