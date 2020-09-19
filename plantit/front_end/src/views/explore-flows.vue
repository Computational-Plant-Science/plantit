<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
            text-variant="dark"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <p class="text-dark">
                            Flows curated by the Computational Plant
                            Science lab. To explore user flows, <a class="hvr" @click="users()">see the user page</a> .
                        </p>
                    </b-col>
                    <!--<b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="communityWorkflowsFilter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!communityWorkflowsFilter"
                                    @click="communityWorkflowsFilter = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>-->
                </b-row>
            </template>
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
                github-user="computational-plant-science"
                :github-token="currentUserDjangoProfile.profile.github_token"
            >
            </flows>
        </b-card>
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
    components: {
        flows
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn'
    ]),
    methods: {
        users() {
          router.push({
            name: 'users'
          })
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

.pipeline
  width: 300px

.hvr:hover
  text-decoration: underline
  text-underline-color: $dark
  cursor: pointer

.workflow-text
  background-color: $color-box-background
  padding: 10px
</style>

<style scoped lang="sass">
@import '../scss/_colors.sass'
</style>
