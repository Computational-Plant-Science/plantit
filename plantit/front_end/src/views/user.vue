<template>
    <div class="w-100 h-100 pl-3" style="background-color: transparent">
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
            <div v-if="loadingUser">
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
            <div v-else>
                <b-row align-v="start" class="mb-2">
                    <b-col
                        style="color: white"
                        align-self="end"
                        class="ml-0 mr-0"
                    >
                        <div v-if="githubProfile">
                            <b-row
                                ><b-col
                                    md="auto"
                                    class="ml-0 mr-0"
                                    align-self="end"
                                >
                                    <b-img
                                        class="avatar"
                                        rounded
                                        style="max-height: 9rem; max-width: 9rem; position: relative; top: 38px; box-shadow: -2px 2px 2px #adb5bd"
                                        :src="
                                            githubProfile
                                                ? githubProfile.avatar_url
                                                : ''
                                        "
                                        v-if="githubProfile"
                                    ></b-img>
                                    <i
                                        v-else
                                        class="far fa-user fa-fw fa-4x"
                                    ></i>
                                </b-col>
                            </b-row>
                            <br />
                            <br />
                        </div>
                        <b-row
                            :class="darkMode ? 'text-light' : 'text-secondary'"
                        >
                            <b-col class="ml-0 mr-0" align-self="end">
                                <h3
                                    :class="
                                        darkMode ? 'text-light' : 'text-dark'
                                    "
                                >
                                    {{
                                        cyverseProfile
                                            ? `${cyverseProfile.first_name} ${cyverseProfile.last_name} `
                                            : githubProfile
                                            ? githubProfile.login
                                            : ''
                                    }}<small
                                        :class="
                                            darkMode
                                                ? 'text-warning'
                                                : 'text-dark'
                                        "
                                        v-if="djangoProfile !== null"
                                        >({{ djangoProfile.username }})</small
                                    >
                                </h3>
                                <a
                                    v-if="githubProfile"
                                    :class="
                                        darkMode ? 'text-light' : 'text-dark'
                                    "
                                    :href="
                                        'https://github.com/' +
                                            githubProfile.login
                                    "
                                >
                                    <i class="fab fa-github fa-1x fa-fw"></i>
                                    {{
                                        'https://github.com/' +
                                            githubProfile.login
                                    }}
                                </a>
                            </b-col>
                        </b-row>
                    </b-col>
                </b-row>
                <b-row align-v="center"
                    ><b-col>
                        <b-tabs
                            pills
                            vertical
                            content-class="mt-2 mr-3"
                            v-model="currentTab"
                            :active-nav-item-class="
                                darkMode ? 'bg-dark' : 'bg-secondary'
                            "
                        >
                            <b-tab v-if="djangoProfile" title="Profile" active>
                                <template v-slot:title>
                                    <b
                                        :class="
                                            darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Profile</b
                                    >
                                </template>
                                <b-card
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :header-border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                >
                                    <b-row>
                                        <b-col md="auto">
                                            <b-card-text
                                                v-if="cyverseProfile"
                                                :class="
                                                    darkMode
                                                        ? 'theme-dark'
                                                        : 'theme-light'
                                                "
                                            >
                                                <p>
                                                    <small>Email</small>
                                                    <br />
                                                    {{ cyverseProfile.email }}
                                                    <br />
                                                    {{
                                                        githubProfile
                                                            ? githubProfile.email
                                                            : ''
                                                    }}
                                                </p>
                                                <p>
                                                    <small>Affiliation</small>
                                                    <br />
                                                    {{
                                                        cyverseProfile ===
                                                        undefined
                                                            ? ''
                                                            : cyverseProfile.institution
                                                    }}
                                                </p>
                                                <p>
                                                    <small>Bio</small>
                                                    <br />
                                                    {{
                                                        githubProfile
                                                            ? githubProfile.bio
                                                            : 'None'
                                                    }}
                                                </p>
                                                <p>
                                                    <small>Location</small>
                                                    <br />
                                                    {{
                                                        githubProfile
                                                            ? githubProfile.location
                                                            : 'None'
                                                    }}
                                                </p>
                                            </b-card-text>
                                        </b-col>
                                    </b-row>
                                </b-card>
                            </b-tab>
                            <b-tab
                                v-if="
                                    this.profile.djangoProfile.username ===
                                        this.$router.currentRoute.params
                                            .username
                                "
                                :title-link-class="tabLinkClass(1)"
                            >
                                <template v-slot:title>
                                    <b :class="tabLinkClass(1)">Data</b>
                                </template>
                                <b-card
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :header-border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                >
                                    <b-row>
                                        <b-col>
                                            <datatree
                                                :node="data"
                                                select="directory"
                                                :upload="true"
                                                :download="true"
                                                :class="
                                                    darkMode
                                                        ? 'theme-dark'
                                                        : 'theme-light'
                                                "
                                            ></datatree></b-col></b-row></b-card
                            ></b-tab>
                            <b-tab :title-link-class="tabLinkClass(2)">
                                <template v-slot:title>
                                    <b :class="tabLinkClass(2)">Flows</b>
                                </template>
                                <b-row
                                    v-if="profile.githubProfile === null"
                                    align-v="center"
                                >
                                    <b-col md="auto" class="mr-2 pr-0">
                                        <b-button
                                            variant="success"
                                            href="/apis/v1/users/github_request_identity/"
                                            class="mr-0"
                                        >
                                            <i class="fab fa-github"></i>
                                            Log in to GitHub
                                        </b-button>
                                    </b-col>
                                    <b-col md="auto" class="ml-0 pl-0">
                                        <b
                                            class="text-center align-center ml-0 pl-0"
                                            >to load flows.</b
                                        >
                                    </b-col>
                                </b-row>
                                <b-row v-else-if="githubProfile">
                                    <flows
                                        class="m-1"
                                        :github-user="githubProfile.login"
                                        :github-token="
                                            profile.djangoProfile.profile
                                                .github_token
                                        "
                                    >
                                    </flows>
                                </b-row>
                            </b-tab>
                            <b-tab v-if="profile.djangoProfile.username === this.$router.currentRoute.params.username" :title-link-class="tabLinkClass(3)">
                                <template v-slot:title>
                                    <b :class="tabLinkClass(3)">Targets</b>
                                </template>
                                <div>
                                    <b-row
                                        v-if="
                                            showToggleSingularityCacheCleaningAlert
                                        "
                                    >
                                        <b-col class="m-0 p-0">
                                            <b-alert
                                                :show="
                                                    showToggleSingularityCacheCleaningAlert
                                                "
                                                :variant="showToggleSingularityCacheCleaningMessage.startsWith('Failed') ? 'danger' : 'success'"
                                                dismissible
                                                @dismissed="
                                                    showToggleSingularityCacheCleaningAlert = false
                                                "
                                            >
                                                {{
                                                    showToggleSingularityCacheCleaningMessage
                                                }}
                                            </b-alert>
                                        </b-col>
                                    </b-row>
                                    <b-row>
                                        <b-col
                                            class="text-left"
                                            align-self="end"
                                            ><h5>
                                                <small
                                                    :class="
                                                        darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                    >Name</small
                                                >
                                            </h5></b-col
                                        >
                                        <b-col
                                            class="text-right"
                                            align-self="end"
                                            ><h5>
                                                <small
                                                    :class="
                                                        darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                    >Resources
                                                </small>
                                            </h5></b-col
                                        >
                                    </b-row>
                                    <hr
                                        :class="
                                            darkMode
                                                ? 'theme-dark'
                                                : 'theme-light'
                                        "
                                    />
                                    <b-row
                                        v-if="targetsLoading"
                                    >
                                        <b-spinner
                                            type="grow"
                                            label="Loading..."
                                            variant="success"
                                        ></b-spinner>
                                    </b-row>
                                    <b-row
                                        class="text-center"
                                        v-if="
                                            !targetsLoading &&
                                                targets.length === 0
                                        "
                                    >
                                        <b-col>
                                            None to show.
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        class="text-right"
                                        v-for="target in targets"
                                        v-bind:key="target.name"
                                    >
                                        <b-col md="auto"
                                            ><b-button
                                                size="md"
                                                block
                                                class="text-left pt-2"
                                                :variant="
                                                    darkMode ? 'dark' : 'white'
                                                "
                                                :disabled="target.role === 'none'"
                                                @click="targetSelected(target)"
                                                >{{ target.name }}</b-button
                                            ></b-col
                                        >
                                        <b-col align-self="center text-left"
                                            ><small
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                >{{

                                                        target.role === 'own'
                                                            ? "(owner)"
                                                            : target.role === 'none' ? '(no access)' : '(guest)'

                                                }}</small
                                            ></b-col
                                        >
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                            ><b>{{ target.max_cores }}</b>
                                            cores</b-col
                                        >
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                            ><b>{{ target.max_processes }}</b>
                                            processes</b-col
                                        >
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                            ><span
                                                v-if="parseInt(target.max_mem)"
                                                >{{ target.max_mem }} GB
                                                memory</span
                                            >
                                            <span
                                                v-else-if="
                                                    parseInt(target.max_mem) > 0
                                                "
                                                class="text-danger"
                                                >{{ target.max_mem }} GB
                                                memory</span
                                            >
                                            <span
                                                v-else-if="
                                                    parseInt(target.max_mem) ===
                                                        -1
                                                "
                                                >virtual memory</span
                                            ></b-col
                                        >
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                        >
                                            <span v-if="target.gpu">
                                                GPU
                                                <i
                                                    :class="
                                                        target.gpu
                                                            ? 'text-warning'
                                                            : ''
                                                    "
                                                    class="far fa-check-circle"
                                                ></i>
                                            </span>
                                            <span v-else
                                                >No GPU
                                                <i
                                                    class="far fa-times-circle"
                                                ></i
                                            ></span>
                                        </b-col>
                                    </b-row>
                                </div>
                            </b-tab>
                        </b-tabs>
                    </b-col>
                </b-row>
            </div>
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import { mapGetters } from 'vuex';
import flows from '@/components/flows.vue';
import datatree from '@/components/data-tree.vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from 'moment';

export default {
    name: 'User',
    components: {
        flows,
        datatree
    },
    data: function() {
        return {
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
            currentTab: 0,
            data: {},
            flows: [],
            runs: [],
            targets: [],
            targetsLoading: false,
            loadingUser: true,
            showToggleSingularityCacheCleaningAlert: false
        };
    },
    computed: mapGetters([
        'profile',
        'loggedIn',
        'darkMode'
    ]),
    async mounted() {
        await this.loadUser();
        this.loadingUser = false;
        await this.loadDirectory(
            `/iplant/home/${this.profile.djangoProfile.username}/`,
            this.profile.djangoProfile.profile.cyverse_token
        );
        await this.loadTargets();
    },
    methods: {
        targetSelected: function(target) {
            router.push({
                name: 'target',
                params: {
                    name: target.name,
                }
            });
        },
        toggleSingularityCacheCleanDelay: function(target) {
            if (target.singularity_cache_clean_enabled)
                axios
                    .get(
                        `/apis/v1/targets/unschedule_singularity_cache_cleaning/?name=${target.name}`
                    )
                    .then(() => {
                        this.showToggleSingularityCacheCleaningMessage = `Disabled Singularity cache cleaning on ${target.name}`;
                        this.showToggleSingularityCacheCleaningAlert = true;
                        this.loadTargets();
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        if (error.response.status === 500) {
                            this.showToggleSingularityCacheCleaningMessage = `Failed to disable Singularity cache cleaning on ${target.name}`;
                            this.showToggleSingularityCacheCleaningAlert = true;
                            throw error;
                        }
                    });
            else
                axios
                    .get(
                        `/apis/v1/targets/schedule_singularity_cache_cleaning/?name=${
                            target.name
                        }&delay=${moment
                            .duration(
                                target.singularity_cache_clean_delay,
                                'seconds'
                            )
                            .asSeconds()}`
                    )
                    .then(() => {
                        this.showToggleSingularityCacheCleaningMessage = `Enabled Singularity cache cleaning on ${target.name}`;
                        this.showToggleSingularityCacheCleaningAlert = true;
                        this.loadTargets();
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        if (error.response.status === 500) {
                            this.showToggleSingularityCacheCleaningMessage = `Failed to enable Singularity cache cleaning on ${target.name}`;
                            this.showToggleSingularityCacheCleaningAlert = true;
                            throw error;
                        }
                    });
        },
        prettifyDuration: function(dur) {
            return moment.duration(dur, 'seconds').humanize();
        },
        tabLinkClass(idx) {
            if (this.djangoProfile === null)
                return this.darkMode ? '' : 'text-dark';
            if (this.currentTab === idx) {
                return this.darkMode ? '' : 'text-dark';
            } else {
                return this.darkMode
                    ? 'background-dark text-light'
                    : 'text-dark';
            }
        },
        statusToString(status) {
            switch (status) {
                case 1:
                    return 'Completed';
                case 2:
                    return 'Failed';
                case 3:
                    return 'Running';
                case 4:
                    return 'Created';
            }
        },
        onRunSelected: function(items) {
            router.push({
                name: 'run',
                params: {
                    id: items[0].id,
                    username: this.profile.djangoProfile.username
                }
            });
        },
        async loadUser() {
            return axios
                .get(
                    `/apis/v1/users/get_by_username/?username=${this.$router.currentRoute.params.username}`
                )
                .then(response => {
                    if (response.data.django_profile)
                        this.djangoProfile = response.data.django_profile;
                    if (response.data.cyverse_profile)
                        this.cyverseProfile = response.data.cyverse_profile;
                    this.githubProfile = response.data.github_profile;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadTargets() {
            this.targetsLoading = true;
            return axios
                .get(`/apis/v1/targets/get_by_username/`)
                .then(response => {
                    this.targetsLoading = false;
                    this.targets = response.data.targets;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.targetsLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        flowSelected: function(flow) {
            router.push({
                name: 'flow',
                params: {
                    owner: flow['repo']['owner']['login'],
                    name: flow['repo']['name']
                }
            });
        },
        async loadDirectory(path, token) {
            return axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => {
                    this.data = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        }
    }
};
</script>

<style lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.background-dark
  background-color: $dark !important
  color: $light

.background-success
  background-color: $success !important
  color: $dark !important
</style>
