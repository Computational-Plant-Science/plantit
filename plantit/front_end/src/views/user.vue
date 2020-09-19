<template>
    <div class="w-100 p-5 m-0">
        <br />
        <br />
        <b-card
            v-if="djangoProfile"
            bg-variant="white"
            border-variant="white"
            header-border-variant="white"
            header-bg-variant="white"
            style="margin: 0 auto;"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center" align-h="start">
                    <b-col md="auto" class="mr-0 pr-0" align-self="center">
                        <b-img
                            right
                            class="avatar "
                            rounded="circle"
                            style="max-height: 7rem; max-width: 7rem; position: relative;"
                            :src="githubProfile ? githubProfile.avatar_url : ''"
                        ></b-img>
                    </b-col>
                    <b-col style="color: white" align-self="end">
                        <h2>
                            {{
                                currentUserCyVerseProfile
                                    ? `${currentUserCyVerseProfile.first_name} (${djangoProfile.username})`
                                    : currentUserDjangoProfile.username
                            }}
                        </h2>
                    </b-col>
                </b-row>
            </template>
            <b-tabs content-class="mt-3">
                <b-tab title="Profile" active>
                    <b-row align-h="center">
                        <b-col md="auto">
                            <b-card-text v-if="cyverseProfile">
                                <h5>
                                    <b-img
                                        :src="
                                            require('../assets/sponsors/cyversebw-notext.png')
                                        "
                                        height="29px"
                                        alt="Cyverse"
                                    ></b-img>
                                    <a
                                        href="https://de.cyverse.org/de/"
                                        title="CyVerse Discovery Environment"
                                    >
                                        CyVerse
                                    </a>
                                </h5>
                                <br />
                                <p>
                                    <b>username:</b>
                                    {{ djangoProfile.username }}
                                </p>
                                <p>
                                    <b>email:</b>
                                    {{ cyverseProfile.email }}
                                </p>
                                <p>
                                    <b>first name:</b>
                                    {{ cyverseProfile.first_name }}
                                </p>
                                <p>
                                    <b>last name:</b>
                                    {{ cyverseProfile.last_name }}
                                </p>
                                <p>
                                    <b>affiliation:</b>
                                    {{
                                        cyverseProfile === undefined
                                            ? ''
                                            : cyverseProfile.institution
                                    }}
                                </p>
                                <br />
                            </b-card-text>
                        </b-col>
                        <b-col>
                            <b-card-text v-if="githubProfile">
                                <h4>
                                    <a
                                        :href="
                                            'https://github.com/' +
                                                githubProfile.login
                                        "
                                    >
                                        <i
                                            class="fab fa-github-alt fa-1x fa-fw"
                                        ></i>
                                        GitHub
                                    </a>
                                </h4>
                                <br />
                                <p>
                                    <b>username:</b>
                                    {{
                                        githubProfile === undefined ||
                                        githubProfile.login === ''
                                            ? 'None'
                                            : this.githubProfile.login
                                    }}
                                </p>
                                <p>
                                    <b>email:</b>
                                    {{ githubProfile.email }}
                                </p>
                                <p>
                                    <b>bio:</b>
                                    {{
                                        githubProfile === undefined
                                            ? ''
                                            : githubProfile.bio
                                    }}
                                </p>
                                <p>
                                    <b>location:</b>
                                    {{
                                        githubProfile === undefined
                                            ? ''
                                            : githubProfile.location
                                    }}
                                </p>
                                <p>
                                    <b>affiliation:</b>
                                    {{
                                        githubProfile === undefined
                                            ? ''
                                            : githubProfile.company
                                    }}
                                </p>
                                <br />
                            </b-card-text>
                        </b-col>
                    </b-row>
                </b-tab>
                <b-tab title="Data"><p>I'm the second tab</p></b-tab>
                <b-tab title="Flows">
                    <b-row
                        v-if="currentUserGitHubProfile === null"
                        align-v="center"
                        align-h="center"
                    >
                        <b-col md="auto">
                            <b-button
                                variant="success"
                                href="/apis/v1/users/github_request_identity/"
                                class="mr-0"
                            >
                                <i class="fab fa-github"></i>
                                Login to GitHub
                            </b-button>
                        </b-col>
                        <b-col md="auto" class="ml-0 pl-0">
                            <b class="text-center align-center ml-0 pl-0"
                                >to load flows</b
                            >
                        </b-col>
                    </b-row>
                    <flows
                        v-else
                        :github-user="currentUserGitHubProfile.login"
                        :github-token="
                            currentUserDjangoProfile.profile.github_token
                        "
                    >
                    </flows>
                </b-tab>
                <b-tab title="runs"><p>I'm a disabled tab!</p></b-tab>
            </b-tabs>
        </b-card>
    </div>
</template>

<script>
import router from '../router';
import { mapGetters } from 'vuex';
import flows from '@/components/flows.vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'User',
    components: {
        flows
    },
    data: function() {
        return {
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
            data: {},
            workflows: [],
            runs: []
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
    },
    methods: {
        async loadUser() {
            return axios
                .get(
                    `/apis/v1/users/get_by_username/?username=${this.$router.currentRoute.params.username}`
                )
                .then(response => {
                    this.djangoProfile = response.data.django_profile;
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
                name: 'workflow',
                params: {
                    owner: workflow['repo']['owner']['login'],
                    name: workflow['repo']['name']
                }
            });
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
