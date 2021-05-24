<template>
    <div
        class="w-100 h-100 pl-3 pt-3"
        :style="
            profile.darkMode
                ? 'background-color: #d6df5D'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="pl-3 pt-3">
            <b-row align-v="center" align-h="center" v-if="resourcesLoading">
                <b-col align-self="end" class="text-center">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </b-col>
            </b-row>
            <b-row
                v-else-if="resources.length > 0"
                align-v="center"
                align-h="center"
            >
                <b-col>
                    <b-row
                        ><b-col md="auto"
                            ><h3
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Public Resources
                            </h3> </b-col
                    ></b-row><b-row><b-col
                            ><b-input-group size="sm"
                                ><template #prepend>
                                    <b-input-group-text
                                        ><i class="fas fa-search"></i
                                    ></b-input-group-text> </template
                                ><b-form-input
                                    :class="
                                        profile.darkMode
                                            ? 'theme-search-dark'
                                            : 'theme-search-light'
                                    "
                                    size="lg"
                                    type="search"
                                    v-model="searchText"
                                ></b-form-input>
                                <!--<template #append>
                                    <b-input-group-text
                                        ><b-form-checkbox
                                            class="mt-1"
                                            v-model="includeTags"
                                        >
                                        </b-form-checkbox
                                        >Include Tags</b-input-group-text
                                    >
                                </template>--></b-input-group
                            ></b-col
                        ></b-row
                    >
                    <b-card-group
                        deck
                        columns
                        class="justify-content-center mt-3"
                    >
                        <b-card
                            v-for="resource in filteredResources"
                            v-bind:key="resource.name"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            :header-bg-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            border-variant="default"
                            :header-border-variant="
                                profile.darkMode ? 'secondary' : 'default'
                            "
                            :text-variant="profile.darkMode ? 'white' : 'dark'"
                            style="min-width: 30rem; max-width: 40rem;"
                            class="overflow-hidden mb-4"
                        >
                            <b-row style="z-index: 10">
                                <b-col cols="10">
                                    <h2>
                                        <b-link
                                            :class="
                                                profile.darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            variant="outline-dark"
                                            v-b-tooltip.hover
                                            @click="resourceSelected(resource)"
                                        >
                                            {{ resource.name }}
                                        </b-link>
                                    </h2>
                                    <b-badge
                                        v-if="!resource.public"
                                        variant="warning"
                                        >Private</b-badge
                                    >
                                    <br />
                                    <small>
                                        {{ resource.description }}
                                    </small>
                                    <br />
                                </b-col>
                                <b-col cols="1"></b-col>
                            </b-row>
                            <b-img
                                v-if="resource.logo"
                                rounded
                                class="card-img-right overflow-hidden"
                                style="max-height: 4rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                right
                                :src="resource.logo"
                            ></b-img>
                            <i
                                v-else
                                style="max-width: 7rem;position: absolute;right: 20px;top: 20px;"
                                right
                                class="card-img-left fas fa-server fa-2x fa-fw"
                            ></i>
                        </b-card>
                    </b-card-group>
                    <b-row
                        class="text-center"
                        v-if="
                            filteredResources.length === 0 && resources.length !== 0
                        "
                        ><b-col>No resources matched your search.</b-col></b-row
                    >
                </b-col>
            </b-row>
            <b-row align-h="center" class="text-center" v-else>
                <b-col>
                    None to show.
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
import { mapGetters } from 'vuex';

export default {
    name: 'resources',
    data: function() {
        return {
            resources: [],
            resourcesLoading: false,
            searchText: '',
            includeTags: false
        };
    },
    mounted() {
        this.loadResources();
    },
    computed: {
        ...mapGetters('user', ['profile']),
        filteredResources() {
            return this.resources.filter(resource => resource.name.includes(this.searchText));
        }
    },
    methods: {
        loadResources() {
            this.resourcesLoading = true;
            axios
                .get('/apis/v1/resources/get_all/')
                .then(response => {
                    this.resources = response.data.resources;
                    this.resourcesLoading = false;
                })
                .catch(error => {
                    this.resourcesLoading = false;
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        resourceSelected(resource) {
            router.push({
                name: 'resource',
                params: {
                    name: resource.name
                }
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.hvr:hover
  text-decoration: underline
  text-underline-color: $dark
  cursor: pointer
</style>
