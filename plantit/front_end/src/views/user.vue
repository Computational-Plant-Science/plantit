<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <b-card
            bg-variant="white"
            border-variant="white"
            header-border-variant="white"
            header-bg-variant="white"
            style="margin: 0 auto;"
        >
            <!--<template v-slot:header style="background-color: white">

            </template>-->
            <b-row align-v="start" align-h="start" class="mb-1">
                <b-col
                    md="auto"
                    style="color: white"
                    align-self="center"
                    class="ml-0 mr-0"
                >
                    <b-row>
                        <b-col>
                            <h2>
                                {{
                                    cyverseProfile
                                        ? `${cyverseProfile.first_name} (${djangoProfile.username})`
                                        : githubProfile
                                        ? githubProfile.login
                                        : ''
                                }}
                            </h2>
                        </b-col>
                    </b-row>
                    <b-row v-if="githubProfile">
                        <b-col md="auto" align-self="end" class="ml-0 mr-0">
                            <a
                                variant="outline-dark"
                                class="ml-0"
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
                <b-col md="auto" class="ml-0 mr-0" align-self="left">
                    <b-img
                        right
                        class="avatar "
                        rounded="circle"
                        style="max-height: 10rem; max-width: 10rem; position: relative;"
                        :src="githubProfile ? githubProfile.avatar_url : ''"
                    ></b-img>
                </b-col>
            </b-row>
            <b-tabs content-class="mt-0">
                <b-tab v-if="djangoProfile" title="Profile" active>
                    <b-card
                        header-bg-variant="white"
                        border-variant="white"
                        header-border-variant="white"
                    >
                        <b-row align-h="left">
                            <b-col md="auto">
                                <b-card-text v-if="cyverseProfile">
                                    <p>
                                        <b>Name</b>
                                        <br />
                                        {{ cyverseProfile.first_name }}
                                        {{ cyverseProfile.last_name }}
                                    </p>
                                    <p>
                                        <b>Email</b>
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
                                        <b>Affiliation</b>
                                        <br />
                                        {{
                                            cyverseProfile === undefined
                                                ? ''
                                                : cyverseProfile.institution
                                        }}
                                    </p>
                                    <p>
                                        <b>Bio</b>
                                        <br />
                                        {{
                                            githubProfile === undefined
                                                ? 'None'
                                                : githubProfile.bio
                                        }}
                                    </p>
                                    <p>
                                        <b>Location</b>
                                        <br />
                                        {{
                                            githubProfile === undefined
                                                ? 'None'
                                                : githubProfile.location
                                        }}
                                    </p>
                                </b-card-text>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-tab>
                <b-tab v-if="djangoProfile" title="Data">
                    <b-card border-variant="white">
                        <datatree :node="data"></datatree></b-card
                ></b-tab>
                <b-tab title="Flows">
                    <b-card
                        header-bg-variant="white"
                        border-variant="white"
                        header-border-variant="white"
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
                                <b class="text-center align-center ml-0 pl-0"
                                    >to load flows.</b
                                >
                            </b-col>
                        </b-row>
                        <flows
                            v-else
                            :github-user="githubProfile.login"
                            :github-token="
                                currentUserDjangoProfile.profile.github_token
                            "
                        >
                        </flows>
                    </b-card>
                </b-tab>
                <b-tab v-if="djangoProfile" title="Runs">
                    <b-card
                        header-bg-variant="white"
                        border-variant="white"
                        header-border-variant="white"
                    >
                        <b-row align-v="center" align-h="center">
                            <b-col align-self="end" class="text-center">
                                <b-button
                                    block
                                    v-if="!loadingRuns"
                                    variant="white"
                                    @click="loadRuns"
                                >
                                    <i class="fas fa-sync-alt fa-fw"></i>
                                    Refresh
                                </b-button>
                                <b-spinner
                                    v-if="loadingRuns"
                                    type="grow"
                                    label="Loading..."
                                    variant="dark"
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
                        >
                            <template v-slot:cell(state)="run">
                                <h4>
                                    <b-badge
                                        :variant="
                                            run.item.state === 2
                                                ? 'danger'
                                                : 'success'
                                        "
                                        >{{ statusToString(run.item.state) }}
                                    </b-badge>
                                </h4>
                            </template>
                        </b-table>
                    </b-card>
                </b-tab>
            </b-tabs>
        </b-card>
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
            data: {},
            flows: [],
            runs: [],
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
                    key: 'workflow_name',
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
        'loggedIn'
    ]),
    async mounted() {
        await this.loadUser();
        await this.loadDirectory(
            `/iplant/home/${this.currentUserDjangoProfile.username}/`,
            this.currentUserDjangoProfile.profile.cyverse_token
        );
        await this.loadRuns();
    },
    methods: {
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
        workflowSelected: function(workflow) {
            router.push({
                name: 'flow',
                params: {
                    owner: workflow['repo']['owner']['login'],
                    name: workflow['repo']['name']
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
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
