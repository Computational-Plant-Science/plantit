<template>
    <div class="w-100 p-5 m-0">
        <br />
        <br />
        <b-container>
            <div class="w-100 pb-4">
                <b-card
                    bg-variant="white"
                    border-variant="white"
                    header-border-variant="white"
                    header-bg-variant="white"
                    :img-src="this.githubUser ? this.githubUser.avatar_url : ''"
                    img-alt="Image"
                    img-top
                    style="max-width: 30rem;margin: 0 auto;"
                >
                    <template
                        v-slot:header
                        style="background-color: white"
                        v-bind:info="this.user"
                    >
                        <b-row align-v="center">
                            <b-col align-self="center" class="mt-2" style="color:white">
                                <h2><b>{{ user.username }}</b></h2>
                            </b-col>
                            <b-col md="auto">
                                <b-button
                                    @click="$bvModal.show('editUserInfoModalNav')"
                                    variant="outline-dark"
                                    v-b-tooltip.hover
                                    title="Edit profile."
                                >
                                    <i class="far fa-edit fa-2x"></i>
                                </b-button>
                            </b-col>
                        </b-row>
                    </template>
                    <b-card-text v-if="!loading">
                        <h4>Profile</h4>
                        <br />
                        <p><b>Email Address:</b> {{ this.user.email }}</p>
                        <p><b>First Name:</b> {{ this.user.first_name }}</p>
                        <p><b>Last Name:</b> {{ this.user.last_name }}</p>
                        <p>
                            <b>Country:</b>
                            {{
                            this.user.profile === undefined
                            ? ''
                            : this.user.profile.country
                            }}
                        </p>
                        <p>
                            <b>Institution:</b>
                            {{
                            this.user.profile === undefined
                            ? ''
                            : this.user.profile.institution
                            }}
                        </p>
                        <p>
                            <b>Field of Study:</b>
                            {{
                            this.user.profile === undefined
                            ? ''
                            : this.user.profile.field_of_study
                            }}
                        </p>
                        <br />
                        <h4>Github</h4>
                        <br />
                        <p>
                            <b>Username:</b>
                            {{
                            this.user.profile === undefined || this.user.profile.github_username === ''
                            ? 'None'
                            : this.user.profile.github_username
                            }}
                        </p>
                        <p><b>Workflows:</b> {{ this.user.profile === undefined || this.user.profile.github_username ===
                            ''
                            ? 'None' : this.workflows }}</p>
                    </b-card-text>
                </b-card>
            </div>
        </b-container>
    </div>
</template>

<script>
import UserApi from '@/services/apiV1/UserManager.js';

export default {
    name: 'UserInfo',
    components: {},
    data() {
        return {
            user: null,
            workflows: 0,
            loading: true,
            githubUser: null
        };
    },
    methods: {
        reload() {
            this.loading = true;
            UserApi.getCurrentUser().then(info => {
                this.user = info;
                UserApi.getCurrentUserGithubUser().then(user => {
                    this.githubUser = user;
                    this.getRepos();
                    this.loading = false;
                });
            });
        },
        getRepos() {
            UserApi.getCurrentUserGithubRepos().then(repos => {
                this.workflows = repos.length;
            });
        },
        saveUserInfo(
            userName,
            firstName,
            lastName,
            country,
            institution,
            fieldOfStudy
        ) {
            UserApi.updateUserInfo(
                userName,
                firstName,
                lastName,
                country,
                institution,
                fieldOfStudy
            ).then(() => {
                this.reload();
            });
        },
        cancel() {
            this.reload();
        }
    },
    created: function() {
        this.reload();
        this.loading = false;
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
