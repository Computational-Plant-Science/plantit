<template>
    <div
        class="w-100 h-100 pl-3 pt-3 pr-0 m-0"
        :style="
            darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <b-container class="pl-3 pt-3 mr-3" fluid>
            <b-row
                v-if="currentUserGitHubProfile === null"
                align-v="center"
                class="p-2"
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
                    <b class="ml-0 pl-0">to load flows.</b>
                </b-col>
            </b-row>
            <b-row v-else align-v="center" align-h="center">
                <flows
                    :github-token="
                        currentUserDjangoProfile.profile.github_token
                    "
                >
                </flows>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import { mapGetters } from 'vuex';
import flows from '@/components/flows.vue';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'explore-flows',
    data() {
        return {
            currentTab: 0
        };
    },
    components: {
        flows
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn',
        'darkMode'
    ]),
    methods: {
        tabLinkClass(idx) {
            if (this.currentTab === idx) {
                // return this.darkMode
                //     ? 'background-dark text-success'
                //     : 'bg-light text-dark';
                return this.darkMode ? '' : 'text-dark';
            } else {
                return this.darkMode
                    ? 'background-dark text-light'
                    : 'text-dark';
            }
        },
        users() {
            router.push({
                name: 'users'
            });
        },
        flowSelected: function(flow) {
            router.push({
                name: 'flow',
                params: {
                    username: flow['repository']['owner']['login'],
                    name: flow['repository']['name']
                }
            });
        }
    }
};
</script>

<style lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.pipeline
  width: 300px

.hvr:hover
  text-decoration: underline
  text-underline-color: $dark
  cursor: pointer

.background-dark
  background-color: $dark !important
  color: $light

.background-success
  background-color: $success !important
  color: $dark !important
</style>
