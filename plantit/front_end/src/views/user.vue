<template>
    <div class="w-100 h-100 pl-3 pt-3" style="background-color: transparent">
        <br />
        <b-spinner align="center" v-if="loadingUser" type="grow" variant="success"></b-spinner>
        <b-container v-else class="p-3 vl" fluid="">
            <b-row align-v="start" align-h="center" class="mb-2">
                <b-col style="color: white" align-self="end" class="ml-0 mr-0">
                    <b-row :class="darkMode ? 'text-light' : 'text-secondary'">
                        <b-col md="auto" class="ml-0 mr-0" align-self="left">
                            <b-img
                                right
                                class="avatar"
                                rounded="circle"
                                style="max-height: 6rem; max-width: 6rem; position: relative; border: 2px solid #d6df5D"
                                :src="
                                    githubProfile
                                        ? githubProfile.avatar_url
                                        : ''
                                "
                                v-if="githubProfile"
                            ></b-img>
                            <i v-else class="fas fa-user fa-fw fa-4x"></i>
                        </b-col>
                        <b-col class="ml-0 mr-0">
                            <h2 :class="darkMode ? 'text-light' : 'text-dark'">
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
                            </h2>
                            <hr
                                :class="darkMode ? 'theme-dark' : 'theme-light'"
                            />
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
                    </b-row>
                </b-col>
            </b-row>
            <br />
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
                                no-body
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
                                                        ?  githubProfile.bio : 'None'
                                                }}
                                            </p>
                                            <p>
                                                <small class="text-secondary"
                                                    >Location</small
                                                >
                                                <br />
                                                {{
                                                    githubProfile
                                                        ? githubProfile.location : 'None'
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
                                <datatree
                                    :node="data"
                                    select="directory"
                                    :class="
                                        darkMode ? 'theme-dark' : 'theme-light'
                                    "
                                ></datatree></b-card
                        ></b-tab>
                        <b-tab :title-link-class="tabLinkClass(2)">
                            <template v-slot:title>
                                <b :class="tabLinkClass(2)">Flows</b>
                            </template>
                            <b-card
                                :header-bg-variant="darkMode ? 'dark' : 'white'"
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :border-variant="darkMode ? 'dark' : 'white'"
                                :header-border-variant="
                                    darkMode ? 'dark' : 'white'
                                "
                                no-body
                            >
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
                                <flows
                                    class="m-1"
                                    v-else-if="githubProfile"
                                    :github-user="githubProfile.login"
                                    :github-token="
                                        currentUserDjangoProfile.profile
                                            .github_token
                                    "
                                >
                                </flows>
                            </b-card>
                        </b-tab>
                        <b-tab
                            v-if="djangoProfile"
                            :title-link-class="tabLinkClass(3)"
                        >
                            <template v-slot:title>
                                <b :class="tabLinkClass(3)">Runs</b>
                            </template>
                            <b-card
                                :header-bg-variant="darkMode ? 'dark' : 'white'"
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :border-variant="darkMode ? 'dark' : 'white'"
                                :header-border-variant="
                                    darkMode ? 'dark' : 'white'
                                "
                                no-body
                            >
                                <b-row align-v="left" align-h="left">
                                    <b-col align-self="end" class="text-left">
                                        <b-button
                                            v-if="!loadingRuns"
                                            :variant="
                                                darkMode
                                                    ? 'outline-light'
                                                    : 'success'
                                            "
                                            @click="loadRuns"
                                        >
                                            <i
                                                class="fas fa-sync-alt fa-fw"
                                            ></i>
                                            Refresh
                                        </b-button>
                                        <b-button
                                            v-if="!loadingRuns"
                                            :variant="
                                                darkMode
                                                    ? 'outline-light'
                                                    : 'success'
                                            "
                                            @click="clearRuns"
                                        >
                                            <i
                                                class="fas fa-sync-alt fa-fw"
                                            ></i>
                                            Clear
                                        </b-button>
                                        <b-spinner
                                            v-if="loadingRuns"
                                            type="grow"
                                            label="Loading..."
                                            :variant="
                                                darkMode
                                                    ? 'warning'
                                                    : 'outline-dark'
                                            "
                                        ></b-spinner>
                                    </b-col>
                                </b-row>
                                <br />
                                <b-table
                                    v-if="!loadingRuns"
                                    show-empty
                                    sticky-header="true"
                                    selectable
                                    hover
                                    small
                                    responsive="sm"
                                    sort-by.sync="date"
                                    sort-desc.sync="true"
                                    :items="runs"
                                    :fields="fields"
                                    borderless
                                    select-mode="single"
                                    :filter="filter"
                                    @row-selected="onRunSelected"
                                    :table-variant="darkMode ? 'dark' : 'white'"
                                >
                                    <template v-slot:cell(state)="run">
                                        <h4>
                                            <b-badge
                                                :variant="
                                                    run.item.state === 2
                                                        ? 'danger'
                                                        : 'success'
                                                "
                                                >{{
                                                    statusToString(
                                                        run.item.state
                                                    )
                                                }}
                                            </b-badge>
                                        </h4>
                                    </template>
                                </b-table>
                            </b-card>
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
            loadingUser: true,
            loadingRuns: false,
            fields: [
                {
                    key: 'id',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'state',
                    label: 'State'
                },
                {
                    key: 'created',
                    sortable: true,
                    formatter: value => {
                        return `${moment(value).fromNow()} (${moment(
                            value
                        ).format('MMMM Do YYYY, h:mm a')})`;
                    }
                },
                {
                    key: 'flow_name',
                    label: 'Workflow',
                    sortable: true
                }
            ]
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
        await this.loadRuns();
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
        },
        async loadRuns() {
            this.loadingRuns = true;
            return axios
                .get(
                    '/apis/v1/runs/' +
                        this.djangoProfile.username +
                        '/get_by_user/'
                )
                .then(response => {
                    this.runs = response.data;
                    this.loadingRuns = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async clearRuns() {}
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
