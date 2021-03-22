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
        <b-container class="p-3 vl" fluid>
            <b-row>
                <b-col>
                    <b-row align-h="center" v-if="openedCollectionLoading">
                        <b-spinner
                            type="grow"
                            label="Loading..."
                            variant="secondary"
                        ></b-spinner> </b-row
                    ><b-row v-else-if="data !== null && data !== undefined"
                        ><b-col>
                            <h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                {{ openedCollection.path }}
                            </h4>
                            <small
                                >Open on
                                <b>{{ openedCollection.cluster }}</b></small
                            ><br />
                            <small
                                >Showing
                                <b class="mr-1"
                                    >{{ filesShown }} of
                                    {{ data.files.length }}</b
                                >file(s),
                                <b class="mr-1">{{
                                    openedCollection.modified.length
                                }}</b
                                >modified</small
                            >
                        </b-col></b-row
                    ></b-col
                >
                <b-col md="auto" align-self="end">
                    <b-row>
                        <b-dropdown
                            :disabled="
                                !dataLoading &&
                                    data !== null &&
                                    data.files.length === 0
                            "
                            dropleft
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            class="mb-2 text-right"
                        >
                            <template #button-content>
                                {{ viewMode }} View
                            </template>
                            <b-dropdown-item @click="setViewMode('Grid')"
                                >Grid</b-dropdown-item
                            >
                            <b-dropdown-item @click="setViewMode('Carousel')"
                                >Carousel</b-dropdown-item
                            >
                        </b-dropdown>
                        <b-button
                            title="Close collection"
                            variant="outline-danger"
                            class="ml-1 mb-2 text-right"
                            @click="closeCollection"
                        >
                            Close Collection
                            <i class="far fa-folder fa-1x fa-fw"></i>
                        </b-button>
                    </b-row>
                    <b-row align-h="end">
                        <b-pagination
                            size="sm"
                            class="mr-2"
                            v-model="currentPage"
                            :per-page="filesPerPage"
                            :total-rows="totalFileCount"
                        ></b-pagination></b-row></b-col
            ></b-row>
            <br />
            <b-row
                v-if="!dataLoading && data !== null && data !== undefined"
                align-h="center"
                class="m-1"
            >
                <b-col>
                    <b-overlay :show="openedCollection.opening" rounded="sm">
                        <span
                            v-if="
                                !dataLoading &&
                                    data !== null &&
                                    data.files.length === 0
                            "
                            >No files in this collection.</span
                        >
                        <b-card-group v-else-if="viewMode === 'Grid'">
                            <b-card
                                :img-src="
                                    openedCollection.opening
                                        ? ''
                                        : `/apis/v1/collections/thumbnail/?path=${file.path}`
                                "
                                v-for="file in currentPageFiles"
                                v-bind:key="file.id"
                                style="min-width: 20rem;max-width: 20rem;"
                                class="overflow-hidden mb-4 mr-4 text-left"
                                :bg-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                :header-bg-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                border-variant="default"
                                :header-border-variant="
                                    profile.darkMode ? 'secondary' : 'default'
                                "
                                :text-variant="
                                    profile.darkMode ? 'white' : 'dark'
                                "
                            >
                                <p
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
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
                                    :title="`Download ${file.label}`"
                                    v-b-tooltip.hover
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    class="text-left m-0"
                                    @click="downloadFile(file)"
                                >
                                    <i class="fas fa-download fa-fw"></i>
                                </b-button>
                                <b-button
                                    :title="`Annotate ${file.label}`"
                                    v-b-tooltip.hover
                                    v-if="fileIsImage(file.label)"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    class="text-left m-0"
                                    @click="annotateFile(file)"
                                >
                                    <i class="fas fa-pen-fancy fa-fw"></i>
                                </b-button>
                            </b-card>
                        </b-card-group>
                        <b-carousel
                            v-else-if="viewMode === 'Carousel'"
                            controls
                        >
                            <b-carousel-slide
                                v-for="file in currentPageFiles"
                                v-bind:key="file.id"
                                :img-src="
                                    fileIsImage(file.label)
                                        ? `/apis/v1/collections/thumbnail/?path=${file.path}`
                                        : ''
                                "
                                ><template v-if="fileIsText(file.label)" #img
                                    ><div
                                        :class="
                                            profile.darkMode
                                                ? 'theme-container-dark'
                                                : 'theme-container-light'
                                        "
                                        style="min-height: 50rem;white-space: pre-line;"
                                    >
                                        {{ file.textContent }}
                                    </div></template
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
                                                :title="
                                                    `Download ${file.label}`
                                                "
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                class="text-right m-0"
                                                @click="downloadFile(file)"
                                            >
                                                <i
                                                    class="fas fa-download fa-fw"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                v-if="fileIsImage(file.label)"
                                                :title="
                                                    `Annotate ${file.label}`
                                                "
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                class="text-right m-0"
                                                @click="annotateFile(file)"
                                            >
                                                <i
                                                    class="fas fa-pen-fancy fa-fw"
                                                ></i> </b-button
                                        ></b-col> </b-row></template
                            ></b-carousel-slide>
                        </b-carousel>
                    </b-overlay>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from 'moment';
import router from '@/router';
import * as yaml from 'js-yaml';

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
        this.currentFile =
            this.data !== null && this.data.files.length > 0
                ? this.data.files[0]
                : '';
    },
    methods: {
        async downloadFile(file) {
            this.downloading = true;
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/fileio/download?path=${file.path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        },
                        responseType: 'blob'
                    }
                )
                .then(response => {
                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', file.path);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    alert(`Failed to download '${file.path}''`);
                    throw error;
                });
        },
        fileIsImage(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'png' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpg' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpeg'
            );
        },
        fileIsText(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'txt' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'csv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'tsv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yaml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'log' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'out' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'err'
            );
        },
        async closeCollection() {
            await this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to close ${this.openedCollection.path} on ${this.openedCollection.cluster}?`,
                    {
                        title: 'Close Collection?',
                        size: 'sm',
                        okVariant: 'outline-danger',
                        cancelVariant: 'white',
                        okTitle: 'Yes',
                        cancelTitle: 'No',
                        centered: true
                    }
                )
                .then(async value => {
                    if (value) {
                        await this.$store.dispatch('collections/closeOpened');
                        await router.push({
                            name: 'user',
                            params: {
                                username: this.profile.djangoProfile.username
                            }
                        });
                    }
                })
                .catch(err => {
                    throw err;
                });
        },
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
                .then(async response => {
                    this.data = response.data;
                    this.dataLoading = false;
                    await Promise.all([
                        this.data.files
                            .filter(f => this.fileIsText(f.label))
                            .map(async f => await this.loadTextContent(f))
                    ]);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.dataLoading = false;
                    throw error;
                });
        },
        async loadTextContent(file) {
            await axios
                .get(`/apis/v1/collections/content/?path=${file.path}`)
                .then(response => {
                    this.data.files = this.data.files.map(f => {
                        if (f.label === file.label) {
                            if (
                                f.label.endsWith('yml') ||
                                f.label.endsWith('yaml')
                            ) {
                                f['textContent'] = yaml.dump(
                                    yaml.load(response.data),
                                );
                            } else f['textContent'] = response.data;
                        }
                        return f;
                    });
                });
        }
    },
    asyncComputed: {},
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['workflow', 'workflowsRecentlyRun']),
        ...mapGetters('collections', [
            'openedCollection',
            'openedCollectionLoading'
        ]),
        filesShown() {
            return `${(this.totalFileCount < this.filesPerPage
                ? this.totalFileCount
                : this.filesPerPage) *
                this.currentPage -
                this.filesPerPage +
                1} - ${
                this.currentPage * this.filesPerPage <= this.totalFileCount
                    ? (this.totalFileCount < this.filesPerPage
                          ? this.totalFileCount
                          : this.filesPerPage) *
                          (this.currentPage + 1) -
                      this.filesPerPage
                    : this.totalFileCount
            }`;
        },
        totalFileCount() {
            return this.dataLoading || this.data === null
                ? 0
                : this.data.files.length;
        },
        currentPageFiles() {
            return this.dataLoading || this.data === null
                ? []
                : this.data.files.slice(
                      this.currentPage - 1,
                      this.filesPerPage
                  );
        }
    }
};
</script>

<style scoped></style>
