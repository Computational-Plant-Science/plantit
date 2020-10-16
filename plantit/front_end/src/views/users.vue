<template>
    <div class="w-100 p-4">
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
            text-variant="dark"
        >
            <b-row v-if="currentUserGitHubProfile === null" align-v="center">
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
                    <b class="ml-0 pl-0">to load users.</b>
                </b-col>
            </b-row>
            <b-row align-v="center" v-else>
                <b-col>
                    <b-card-group columns>
                        <b-card
                            v-for="user in users"
                            :key="user.username"
                            bg-variant="white"
                            border-variant="default"
                            header-bg-variant="white"
                            style="min-width: 25rem"
                            class="overflow-hidden"
                        >
                            <b-row align-v="center">
                                <b-col
                                    style="color: white; cursor: pointer"
                                    @click="userSelected(user)"
                                >
                                    <h5>
                                        {{ user.first_name }}
                                        {{ user.last_name }}
                                    </h5>
                                </b-col>
                            </b-row>
                            <b-row align-v="center">
                                <b-col class="mr=3">
                                    {{
                                        user.github_profile
                                            ? user.github_profile.bio
                                            : ''
                                    }}
                                </b-col>
                            </b-row>
                            <br />
                            <b-row align-v="center">
                                <b-col>
                                    <b-link disabled>
                                        <b-img
                                            :src="
                                                require('../assets/sponsors/cyversebw-notext.png')
                                            "
                                            height="20px"
                                            alt="Cyverse"
                                            class="m-1"
                                        ></b-img>
                                        <small>{{
                                            user.username
                                        }}</small></b-link
                                    ></b-col
                                >
                            </b-row>
                            <b-row align-v="top">
                                <b-col md="auto">
                                    <b-link
                                        :href="
                                            'https://github.com/' +
                                                user.github_username
                                        "
                                    >
                                        <i
                                            class="fab fa-github fa-fw fa-1x mr-2 ml-1"
                                        ></i>
                                        <small>{{
                                            user.github_username
                                        }}</small>
                                    </b-link>
                                </b-col>
                                <b-col class="ml-0 mr-0" align-self="left">
                                    <b-img
                                        right
                                        rounded="circle"
                                        class="avatar card-img-right"
                                        style="max-height: 5rem; max-width: 5rem; opacity: 0.8; position: absolute; right: -15px; top: -25px; z-index:1"
                                        :src="
                                            user.github_profile
                                                ? user.github_profile.avatar_url
                                                : ''
                                        "
                                    ></b-img>
                                </b-col>
                            </b-row>
                        </b-card>
                    </b-card-group>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import router from '@/router';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
// import axios from 'axios';
// import * as Sentry from '@sentry/browser';

export default {
    name: 'Users',
    mounted() {
        this.loadAll();
        // this.$store.dispatch('loadAllUsers');
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn',
        'allUsers'
    ]),
    data: function() {
        return {
            users: []
        };
    },
    methods: {
        flows() {
            router.push({
                name: 'flows'
            });
        },
        loadAll() {
            axios
                .get('/apis/v1/users/get_all/')
                .then(response => {
                    this.users = response.data.users;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        userSelected(user) {
            router.push({
                name: 'user',
                params: {
                    username:
                        user.username === 'Computational-Plant-Science' ||
                        user.username === 'van-der-knaap-lab'
                            ? user.github_username
                            : user.username
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
