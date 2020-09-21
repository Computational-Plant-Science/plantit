<template>
    <div class="w-100 p-5 m-0">
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
            text-variant="dark"
        >
            <b-row align-v="center">
                <b-col style="color: white">
                    <p class="text-dark">
                        Explore users here. To explore curated flows,
                        <a class="hvr" @click="flows()">see the flows page</a>
                        .
                    </p>
                </b-col>
            </b-row>
            <b-row align-v="center">
                <b-col>
                    <b-card-group columns>
                        <b-card
                            v-for="user in users"
                            :key="user.username"
                            bg-variant="white"
                            border-variant="default"
                            header-bg-variant="white"
                            style="margin: 0 auto; min-width: 25rem"
                        >
                            <b-row align-v="center">
                                <b-col
                                    style="color: white; cursor: pointer"
                                    @click="userSelected(user)"
                                >
                                    <h5>{{ user.username }}</h5>
                                </b-col>
                            </b-row>
                            <b-row align-v="center">
                                <b-col>
                                    <b-link
                                        :href="
                                            'https://github.com/' +
                                                user.github_username
                                        "
                                    >
                                        <i
                                            class="fab fa-github fa-fw fa-1x mr-1"
                                        ></i>
                                        <small>{{
                                            user.github_username
                                        }}</small>
                                    </b-link>
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
