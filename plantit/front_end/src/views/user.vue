<template>
    <div class="w-100 h-100 pl-3" style="background-color: transparent">
        <b-spinner v-if="loadingUser" type="grow" class="text-center" variant="success"></b-spinner>
        <b-container v-else class="p-3 vl">
            <b-row align-v="start" align-h="center" class="mb-2">
                <b-col style="color: white" align-self="end" class="ml-0 mr-0">
                    <b-row :class="darkMode ? 'text-light' : 'text-secondary'">
                        <b-col class="ml-0 mr-0" align-self="end">
                            <h3 :class="darkMode ? 'text-light' : 'text-dark'">
                                {{
                                    cyverseProfile
                                        ? `${cyverseProfile.first_name} ${cyverseProfile.last_name} `
                                        : githubProfile
                                        ? githubProfile.login
                                        : ''
                                }}<small
                                    :class="
                                        darkMode ? 'text-warning' : 'text-dark'
                                    "
                                    v-if="djangoProfile !== null"
                                    >({{ djangoProfile.username }})</small
                                >
                            </h3>
                            <a
                                v-if="githubProfile"
                                :class="darkMode ? 'text-light' : 'text-dark'"
                                :href="
                                    'https://github.com/' + githubProfile.login
                                "
                            >
                                <i class="fab fa-github fa-1x fa-fw"></i>
                                {{
                                    'https://github.com/' + githubProfile.login
                                }}
                            </a>
                        </b-col>
                        <b-col md="auto" class="ml-0 mr-0" align-self="end">
                            <b-img
                                right
                                class="avatar"
                                rounded
                                style="max-height: 7rem; max-width: 7rem; position: relative; top: 38px; box-shadow: -2px 2px 2px #adb5bd"
                                :src="
                                    githubProfile
                                        ? githubProfile.avatar_url
                                        : ''
                                "
                                v-if="githubProfile"
                            ></b-img>
                            <i v-else class="fas fa-user fa-fw fa-4x"></i>
                        </b-col>
                    </b-row>
                </b-col>
            </b-row>
            <b-row align-v="center" align-h="center"
                ><b-col>
                    <b-tabs
                        pills
                        content-class="mt-2"
                        v-model="currentTab"
                        active-nav-item-class="background-success text-dark"
                    >
                        <b-tab
                            v-if="djangoProfile"
                            title="Profile"
                            active
                            :title-link-class="tabLinkClass(0)"
                        >
                            <template v-slot:title>
                                <b :class="tabLinkClass(0)">Profile</b>
                            </template>
                            <b-card
                                :header-bg-variant="darkMode ? 'dark' : 'white'"
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :border-variant="darkMode ? 'dark' : 'white'"
                                :header-border-variant="
                                    darkMode ? 'dark' : 'white'
                                "
                            >
                                <b-row align-h="left">
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
                                                <small class="text-secondary"
                                                    >Email</small
                                                >
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
                                                <small class="text-secondary"
                                                    >Affiliation</small
                                                >
                                                <br />
                                                {{
                                                    cyverseProfile === undefined
                                                        ? ''
                                                        : cyverseProfile.institution
                                                }}
                                            </p>
                                            <p>
                                                <small class="text-secondary"
                                                    >Bio</small
                                                >
                                                <br />
                                                {{
                                                    githubProfile
                                                        ? githubProfile.bio
                                                        : 'None'
                                                }}
                                            </p>
                                            <p>
                                                <small class="text-secondary"
                                                    >Location</small
                                                >
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
                                this.currentUserDjangoProfile.username ===
                                    this.$router.currentRoute.params.username
                            "
                            :title-link-class="tabLinkClass(1)"
                        >
                            <template v-slot:title>
                                <b :class="tabLinkClass(1)">Data</b>
                            </template>
                            <b-card
                                :header-bg-variant="darkMode ? 'dark' : 'white'"
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :border-variant="darkMode ? 'dark' : 'white'"
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
                                v-if="currentUserGitHubProfile === null"
                                align-v="center"
                                align-h="center"
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
                                        currentUserDjangoProfile.profile
                                            .github_token
                                    "
                                >
                                </flows>
                            </b-row>
                        </b-tab>
                    </b-tabs>
                </b-col>
            </b-row>
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
            loadingUser: true
        };
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn',
        'darkMode'
    ]),
    async mounted() {
        await this.loadUser();
        this.loadingUser = false;
        await this.loadDirectory(
            `/iplant/home/${this.currentUserDjangoProfile.username}/`,
            this.currentUserDjangoProfile.profile.cyverse_token
        );
    },
    methods: {
        tabLinkClass(idx) {
            if (this.djangoProfile === null)
                return this.darkMode ? '' : 'text-dark';
            if (this.currentTab === idx) {
                // return this.darkMode
                //     ? 'background-dark text-success'
                //     : 'bg-light text-dark';
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
                    username: this.currentUserDjangoProfile.username
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
