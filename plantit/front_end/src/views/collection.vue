<template>
    <div
        v-if="render"
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
            <div v-if="collectionNotFound">
                <b-row align-content="center">
                    <b-col>
                        <p
                            :class="
                                profile.darkMode
                                    ? 'text-center text-white'
                                    : 'text-center text-dark'
                            "
                        >
                            <i
                                class="fas fa-exclamation-circle fa-3x fa-fw"
                            ></i>
                            <br />
                            <br />
                            This collection does not exist.
                        </p>
                    </b-col>
                </b-row>
            </div>
            <div v-else>
                <b-row>
                    <b-col>
                        <b-row align-h="center" v-if="dataLoading">
                            <b-spinner
                                type="grow"
                                label="Loading..."
                                variant="secondary"
                            ></b-spinner> </b-row
                        ><b-row v-else
                            ><b-col>
                                {{ data.path }}
                            </b-col></b-row
                        ></b-col
                    ></b-row
                >
            </div>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'collection',
    data: function() {
        return {
            data: null,
            dataLoading: false,
            collectionNotFound: false
        };
    },
    async mounted() {
        await this.loadCollection();
    },
    methods: {
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
            'session',
            'sessionLoading'
        ])
    }
};
</script>

<style scoped></style>
