<template>
    <div
        class="w-100 h-100 p-3"
        :style="
            darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <b-container class="p-3">
            <p :class="darkMode ? 'text-light' : 'text-dark'">
                Explore users here. To explore curated flows, see the
                <b-link
                    :class="darkMode ? 'text-warning' : 'text-dark'"
                    to="/flows"
                    >Flows page</b-link
                >.
            </p>
            <b-row align-v="center">
                <b-col>
                    <b-card-group columns>
                        <b-card
                            v-for="user in users"
                            :key="user.username"
                            :bg-variant="darkMode ? 'dark' : 'white'"
                            :header-bg-variant="darkMode ? 'dark' : 'white'"
                            :border-variant="darkMode ? 'secondary' : 'default'"
                            :header-border-variant="
                                darkMode ? 'secondary' : 'default'
                            "
                            :text-variant="darkMode ? 'white' : 'dark'"
                            style="min-width: 15rem; max-width: 40rem;"
                            class="overflow-hidden mb-4"
                        >
                            <b-row align-v="center">
                                <b-col
                                    style="color: white; cursor: pointer"
                                    @click="userSelected(user)"
                                >
                                    <h5
                                        :class="
                                            darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        {{ user.first_name }}
                                        {{ user.last_name }}
                                        <small
                                            :class="
                                                darkMode
                                                    ? 'text-warning'
                                                    : 'text-dark'
                                            "
                                            >({{ user.username }})</small
                                        >
                                    </h5>
                                </b-col>
                            </b-row>
                            <b-row align-v="center">
                                <b-col
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    {{
                                        user.github_profile
                                            ? user.github_profile.bio
                                            : ''
                                    }}
                                </b-col>
                            </b-row>
                            <br />
                            <b-row v-if="user.github_username === null" align-v="center">
                                <b-col>
                                    <b-link
                                        :class="
                                            darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        :href="
                                            'https://github.com/' +
                                                user.github_username
                                        "
                                    >
                                        <i
                                            class="fab fa-github fa-fw fa-1x mr-2 ml-1 pl-1"
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
                                        style="max-height: 6rem; max-width: 6rem; opacity: 0.9; position: absolute; right: -25px; top: -40px; z-index:1;"
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
        </b-container>
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
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn',
        'allUsers',
        'darkMode'
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
