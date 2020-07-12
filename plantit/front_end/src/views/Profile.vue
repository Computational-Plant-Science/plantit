<template>
    <div class="w-100 p-5 m-0">
        <b-container>
            <div class="w-100 pb-4">
                <!-- :img-src="require('../assets/icons/default-user-small.png')" -->
                <b-card
                    bg-variant="white"
                    border-variant="dark"
                    header-border-variant="dark"
                    header-bg-variant="white"
                    img-alt="Image"
                    img-top
                    style="max-width: 30rem;margin: 0 auto;"
                >
                    <template
                        v-slot:header
                        style="background-color: white"
                        v-bind:info="this.info"
                    >
                        <b-row align-v="center">
                            <b-col align-self="center" class="mt-2" style="color:white">
                                <h2><b>{{ info.username }}</b></h2>
                            </b-col>
                            <b-col md="auto">
                                <b-button
                                    @click="$bvModal.show('editUserInfoModal')"
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
                        <h3>Profile</h3>
                        <br />
                        <p><b>Email Address:</b> {{ this.info.email }}</p>
                        <p><b>First Name:</b> {{ this.info.first_name }}</p>
                        <p><b>Last Name:</b> {{ this.info.last_name }}</p>
                        <p>
                            <b>Country:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.country
                            }}
                        </p>
                        <p>
                            <b>Continent:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.continent
                            }}
                        </p>
                        <p>
                            <b>Institution:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.institution
                            }}
                        </p>
                        <p>
                            <b>Institution Type:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.institution_type
                            }}
                        </p>
                        <p>
                            <b>Field of Study:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.field_of_study
                            }}
                        </p>
                        <br />
                        <h3>Github</h3>
                        <br />
                        <p>
                            <b>Username:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.github_username
                            }}
                        </p>
                        <p><b>Workflows:</b> {{ this.workflows }}</p>
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
            info: {},
            workflows: 0,
            loading: true
        };
    },
    methods: {
        reload() {
            UserApi.getCurrentUser().then(info => {
                this.info = info;
            });
            this.getRepos();
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
            continent,
            institution,
            institutionType,
            fieldOfStudy
        ) {
            UserApi.updateUserInfo(
                userName,
                firstName,
                lastName,
                country,
                continent,
                institution,
                institutionType,
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
