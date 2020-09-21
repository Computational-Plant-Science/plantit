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
                    <b-card-group columns deck>
                        <b-card
                            v-for="user in allUsers"
                            :key="user.username"
                            bg-variant="white"
                            border-variant="white"
                            header-border-variant="default"
                            header-bg-variant="white"
                            style="margin: 0 auto;"
                        >
                            <template
                                v-slot:header
                                style="background-color: white"
                            >
                                <b-row align-v="center">
                                    <b-col style="color: white">
                                        <h3>{{ user.username }}</h3>
                                    </b-col>
                                    <b-col md="auto">
                                        <b-button
                                            class="text-left"
                                            variant="outline-dark"
                                            v-b-tooltip.hover
                                            @click="userSelected(user)"
                                        >
                                            <i class="far fa-user"></i>
                                            view
                                        </b-button>
                                    </b-col>
                                </b-row>
                            </template>
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
// import axios from 'axios';
// import * as Sentry from '@sentry/browser';

export default {
    name: 'Users',
    created() {
        this.$store.dispatch('loadAllUsers');
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn',
        'allUsers'
    ]),
    methods: {
        flows() {
            router.push({
                name: 'flows'
            });
        },
        userSelected(user) {
            router.push({
                name: 'user',
                params: {
                    username: user.username
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
