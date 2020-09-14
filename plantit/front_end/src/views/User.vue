<template>
    <div class="w-100 p-5 m-0">
        <br />
        <br />
        <b-card
            v-if="djangoProfile"
            bg-variant="white"
            border-variant="white"
            header-border-variant="default"
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
                            style="max-height: 2rem; max-width: 3rem; position: relative;"
                            :src="githubProfile ? githubProfile.avatar_url : ''"
                        ></b-img>
                    </b-col>
                    <b-col style="color: white" align-self="center">
                        <h1>
                            {{
                                currentUserCyVerseProfile
                                    ? `${currentUserCyVerseProfile.first_name} (${djangoProfile.username})`
                                    : currentUserDjangoProfile.username
                            }}
                        </h1>
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <b-col md="auto">
                    <b-card-text v-if="cyverseProfile">
                        <h3>CyVerse Profile</h3>
                        <br />
                        <p><b>Username:</b> {{ djangoProfile.username }}</p>
                        <p>
                            <b>Email:</b>
                            {{ cyverseProfile.email }}
                        </p>
                        <p>
                            <b>First Name:</b>
                            {{ cyverseProfile.first_name }}
                        </p>
                        <p>
                            <b>Last Name:</b>
                            {{ cyverseProfile.last_name }}
                        </p>
                        <p>
                            <b>Affiliation:</b>
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
                        <h3>Github Profile</h3>
                        <br />
                        <p>
                            <b>Username:</b>
                            {{
                                githubProfile === undefined ||
                                githubProfile.login === ''
                                    ? 'None'
                                    : this.githubProfile.login
                            }}
                        </p>
                        <p>
                            <b>Email:</b>
                            {{ githubProfile.email }}
                        </p>
                        <p>
                            <b>Bio:</b>
                            {{
                                githubProfile === undefined
                                    ? ''
                                    : githubProfile.bio
                            }}
                        </p>
                        <p>
                            <b>Location:</b>
                            {{
                                githubProfile === undefined
                                    ? ''
                                    : githubProfile.location
                            }}
                        </p>
                        <p>
                            <b>Affiliation:</b>
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
        </b-card>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'User',
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
        async loadData() {},
        async loadWorkflows() {},
        async loadRuns() {},
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
