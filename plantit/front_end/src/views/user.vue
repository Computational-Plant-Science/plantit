<template>
    <div class="w-100 h-100 pl-3" style="background-color: transparent">
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
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
            <div v-else>
                <b-row align-v="start" class="mb-2">
                    <b-col
                        style="color: white"
                        align-self="end"
                        class="ml-0 mr-0"
                    >
                        <div v-if="userProfile.githubProfile">
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
                                            userProfile.githubProfile
                                                ? userProfile.githubProfile
                                                      .avatar_url
                                                : ''
                                        "
                                        v-if="userProfile.githubProfile"
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
                            :class="
                                profile.darkMode
                                    ? 'text-light'
                                    : 'text-secondary'
                            "
                        >
                            <b-col class="ml-0 mr-0" align-self="end">
                                <h3
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    {{
                                        userProfile.cyverseProfile
                                            ? `${userProfile.cyverseProfile.first_name} ${userProfile.cyverseProfile.last_name} `
                                            : userProfile.githubProfile
                                            ? userProfile.githubProfile.login
                                            : ''
                                    }}<small
                                        :class="
                                            profile.darkMode
                                                ? 'text-warning'
                                                : 'text-dark'
                                        "
                                        v-if="
                                            userProfile.djangoProfile !== null
                                        "
                                        >({{
                                            userProfile.djangoProfile.username
                                        }})</small
                                    >
                                </h3>
                                <a
                                    v-if="userProfile.githubProfile"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    :href="
                                        'https://github.com/' +
                                            userProfile.githubProfile.login
                                    "
                                >
                                    <i class="fab fa-github fa-1x fa-fw"></i>
                                    {{
                                        'https://github.com/' +
                                            userProfile.githubProfile.login
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
                                profile.darkMode ? 'bg-dark' : 'bg-secondary'
                            "
                        >
                            <b-tab
                                v-if="userProfile.djangoProfile"
                                title="Profile"
                                active
                            >
                                <template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Profile</b
                                    >
                                </template>
                                <b-card
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                >
                                    <b-row
                                        ><b-col
                                            ><h5
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Your user profile
                                            </h5></b-col
                                        ></b-row
                                    >
                                    <b-row>
                                        <b-col md="auto">
                                            <b-card-text
                                                v-if="
                                                    userProfile.cyverseProfile
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark'
                                                        : 'theme-light'
                                                "
                                            >
                                                <p>
                                                    <small>Email</small>
                                                    <br />
                                                    {{
                                                        userProfile
                                                            .cyverseProfile
                                                            .email
                                                    }}
                                                    <br />
                                                    {{
                                                        userProfile.githubProfile
                                                            ? userProfile
                                                                  .githubProfile
                                                                  .email
                                                            : ''
                                                    }}
                                                </p>
                                                <p>
                                                    <small>Affiliation</small>
                                                    <br />
                                                    {{
                                                        userProfile.cyverseProfile ===
                                                        undefined
                                                            ? ''
                                                            : userProfile
                                                                  .cyverseProfile
                                                                  .institution
                                                    }}
                                                </p>
                                                <p>
                                                    <small>Bio</small>
                                                    <br />
                                                    {{
                                                        userProfile.githubProfile
                                                            ? userProfile
                                                                  .githubProfile
                                                                  .bio
                                                            : 'None'
                                                    }}
                                                </p>
                                                <p>
                                                    <small>Location</small>
                                                    <br />
                                                    {{
                                                        userProfile.githubProfile
                                                            ? userProfile
                                                                  .githubProfile
                                                                  .location
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
                                    profile.djangoProfile.username ===
                                        $router.currentRoute.params.username
                                "
                                :title-link-class="tabLinkClass(1)"
                            >
                                <template v-slot:title>
                                    <b :class="tabLinkClass(1)">Datasets</b>
                                </template>
                                <b-card
                                    :sub-title-text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                >
                                    <b-row
                                        ><b-col
                                            ><h5
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Your own data
                                            </h5></b-col
                                        ></b-row
                                    >
                                    <b-row>
                                        <b-col>
                                            <datatree
                                                :node="data"
                                                select="directory"
                                                :upload="true"
                                                :download="true"
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark'
                                                        : 'theme-light'
                                                "
                                            ></datatree></b-col
                                    ></b-row>
                                    <hr />
                                    <b-row
                                        ><b-col
                                            ><h5
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Shared with you
                                            </h5></b-col
                                        ></b-row
                                    >
                                    <b-row v-if="directoriesShared.length > 0">
                                        <b-col>
                                            <datatree
                                                v-for="node in directoriesShared"
                                                v-bind:key="node.path"
                                                v-bind:node="node"
                                                select="directory"
                                                :upload="true"
                                                :download="true"
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark'
                                                        : 'theme-light'
                                                "
                                            ></datatree></b-col></b-row
                                    ><b-row v-else
                                        ><b-col
                                            ><small
                                                >Nobody has shared any
                                                directories with you.</small
                                            ></b-col
                                        ></b-row
                                    >
                                    <hr />
                                    <b-row
                                        ><b-col
                                            ><h5
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Data you've shared
                                            </h5></b-col
                                        ></b-row
                                    >
                                    <b-row v-if="showUnsharedAlertMessage">
                                        <b-col class="m-0 p-0">
                                            <b-alert
                                                :show="showUnsharedAlertMessage"
                                                :variant="
                                                    unsharedAlertMessage.startsWith(
                                                        'Failed'
                                                    )
                                                        ? 'danger'
                                                        : 'success'
                                                "
                                                dismissible
                                                @dismissed="
                                                    showUnsharedAlertMessage = false
                                                "
                                            >
                                                {{ unsharedAlertMessage }}
                                            </b-alert>
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        v-for="directory in sharedDirectories"
                                        v-bind:key="directory.path"
                                    >
                                        <b-col
                                            ><small>{{
                                                directory.path
                                            }}</small></b-col
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
                                                @click="
                                                    unshareDirectory(directory)
                                                "
                                                ><i
                                                    class="fas fa-user-lock fa-fw"
                                                ></i>
                                                Unshare</b-button
                                            ></b-col
                                        ></b-row
                                    >
                                    <b-row v-if="sharedDirectories.length === 0"
                                        ><b-col
                                            ><small
                                                >You haven't shared any
                                                directories with anyone.</small
                                            ></b-col
                                        ></b-row
                                    >
                                </b-card></b-tab
                            >
                            <b-tab :title-link-class="tabLinkClass(2)">
                                <template v-slot:title>
                                    <b :class="tabLinkClass(2)">Workflows</b>
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
                                            >to load workflows.</b
                                        >
                                    </b-col>
                                </b-row>
                                <b-row
                                    align-v="center"
                                    align-h="center"
                                    v-if="
                                        userWorkflows.length === 0 &&
                                            !workflowsLoading
                                    "
                                    ><b-col
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >No workflows to show!</b-col
                                    ></b-row
                                >
                                <b-row
                                    v-else-if="
                                        userProfile.githubProfile &&
                                            profile.djangoProfile
                                                .github_token !== undefined
                                    "
                                >
                                    <workflows
                                        class="m-1"
                                        :github-user="
                                            profile.githubProfile.login
                                        "
                                        :github-token="
                                            profile.djangoProfile.github_token
                                        "
                                        :workflows="userWorkflows"
                                    >
                                    </workflows>
                                </b-row>
                            </b-tab>
                            <b-tab
                                v-if="
                                    profile.djangoProfile.username ===
                                        $router.currentRoute.params.username
                                "
                                :title-link-class="tabLinkClass(3)"
                            >
                                <template v-slot:title>
                                    <b :class="tabLinkClass(3)">Servers</b>
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
                                                :variant="
                                                    showToggleSingularityCacheCleaningMessage.startsWith(
                                                        'Failed'
                                                    )
                                                        ? 'danger'
                                                        : 'success'
                                                "
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
                                                        profile.darkMode
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
                                                        profile.darkMode
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
                                            profile.darkMode
                                                ? 'theme-dark'
                                                : 'theme-light'
                                        "
                                    />
                                    <b-row v-if="targetsLoading">
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
                                                    profile.darkMode
                                                        ? 'dark'
                                                        : 'white'
                                                "
                                                :disabled="
                                                    target.role === 'none'
                                                "
                                                @click="targetSelected(target)"
                                                >{{ target.name }}</b-button
                                            ></b-col
                                        >
                                        <b-col align-self="center text-left"
                                            ><small
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                >{{
                                                    target.role === 'own'
                                                        ? '(owner)'
                                                        : target.role === 'none'
                                                        ? '(no access)'
                                                        : '(guest)'
                                                }}</small
                                            ></b-col
                                        >
                                        <b-col
                                            align-self="center"
                                            :class="
                                                profile.darkMode
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
                                                profile.darkMode
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
                                                profile.darkMode
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
                                                profile.darkMode
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
import workflows from '@/components/workflows.vue';
import datatree from '@/components/data-tree.vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from 'moment';

export default {
    name: 'User',
    components: {
        workflows,
        datatree
    },
    data: function() {
        return {
            currentTab: 0,
            directoriesShared: [],
            sharedDirectories: [],
            directoryPolicies: [],
            directoryPolicyNodes: [],
            data: {},
            runs: [],
            targets: [],
            targetsLoading: false,
            showToggleSingularityCacheCleaningAlert: false,
            showUnsharedAlertMessage: false,
            unsharedAlertMessage: ''
        };
    },
    computed: {
        ...mapGetters([
            'profile',
            'profileLoading',
            'workflows',
            'workflowsLoading'
        ]),
        userWorkflows() {
            if (this.workflowsLoading) return [];
            return this.workflows.filter(wf => {
                return wf.repo.owner.login === this.profile.githubProfile.login;
            });
        }
    },
    asyncComputed: {
        async userProfile() {
            if (
                this.$router.currentRoute.params.username ===
                this.profile.djangoProfile.username
            )
                return this.profile;
            else {
                return await axios
                    .get(`/apis/v1/users/get_current`)
                    .then(response => {
                        return {
                            djangoProfile: response.data.django_profile,
                            cyverseProfile: response.data.cyverse_profile,
                            githubProfile: response.data.github_profile
                        };
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        if (error.response.status === 500) throw error;
                    });
            }
        }
    },
    async mounted() {
        await this.$store.dispatch('loadWorkflows');
        await this.loadDirectory(
            `/iplant/home/${this.profile.djangoProfile.username}/`,
            this.profile.djangoProfile.cyverse_token
        );
        await this.loadTargets();
        await this.loadDirectoryPolicies();
        await this.loadSharedDirectories();
    },
    methods: {
        async unshareDirectory(directory) {
            /** Terrain spec
             *{
             *  "sharing": [
             *    {
             *      "user": "string",
             *      "paths: [
             *        {
             *          "path": "string",
             *          "permission": "read",
             *        }
             *      ]
             *    }
             *  ]
             *}
             */
            await axios({
                method: 'post',
                url: `/apis/v1/stores/unshare_directory/`,
                data: {
                    user: directory.guest,
                    path: directory.path,
                    role: directory.role
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(() => {
                    this.loadSharedDirectories();
                    this.unsharedAlertMessage = `Unshared directory ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.showUnsharedAlertMessage = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.unsharedAlertMessage = `Failed to unshare directory ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.showUnsharedAlertMessage = true;
                    throw error;
                });
        },
        async loadSharedDirectories() {
            await axios
                .get(`/apis/v1/stores/get_shared_directories/`)
                .then(response => {
                    this.sharedDirectories = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadDirectoryPolicies() {
            await axios
                .get(`/apis/v1/stores/get_directories_shared/`)
                .then(response => {
                    this.directoriesShared = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        targetSelected: function(target) {
            router.push({
                name: 'server',
                params: {
                    name: target.name
                }
            });
        },
        toggleSingularityCacheCleanDelay: function(target) {
            if (target.singularity_cache_clean_enabled)
                axios
                    .get(
                        `/apis/v1/servers/unschedule_singularity_cache_cleaning/?name=${target.name}`
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
                        `/apis/v1/servers/schedule_singularity_cache_cleaning/?name=${
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
            if (this.profile.djangoProfile === null)
                return this.profile.darkMode ? '' : 'text-dark';
            if (this.currentTab === idx) {
                return this.profile.darkMode ? '' : 'text-dark';
            } else {
                return this.profile.darkMode
                    ? 'background-dark text-light'
                    : 'text-dark';
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
        async loadTargets() {
            this.targetsLoading = true;
            return axios
                .get(`/apis/v1/servers/get_by_username/`)
                .then(response => {
                    this.targetsLoading = false;
                    this.targets = response.data.servers;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.targetsLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        workflowSelected: function(workflow) {
            router.push({
                name: 'workflow',
                params: {
                    owner: workflow['repo']['owner']['login'],
                    name: workflow['repo']['name']
                }
            });
        },
        async getDirectory(path) {
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        }
                    }
                )
                .then(response => {
                    this.directoriesShared.push(response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
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
