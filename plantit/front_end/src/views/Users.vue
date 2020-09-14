<template>
    <div class="w-100 p-5 m-0">
        <br />
        <br />
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
                <template v-slot:header style="background-color: white">
                    <b-row align-v="center">
                        <b-col style="color: white">
                            <h1>{{ user.username }}</h1>
                        </b-col>
                        <b-col md="auto">
                            <b-button
                                class="text-left"
                                variant="success"
                                v-b-tooltip.hover
                                @click="userSelected(user)"
                            >
                                <i class="fas fa-terminal"></i>
                                View User
                            </b-button>
                        </b-col>
                    </b-row>
                </template>
            </b-card>
        </b-card-group>
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

<style scoped></style>
