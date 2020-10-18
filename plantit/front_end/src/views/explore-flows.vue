<template>
    <div class="w-100 p-3">
        <br />
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
            text-variant="dark"
        >
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
                    <b class="ml-0 pl-0">to load flows.</b>
                </b-col>
            </b-row>
            <b-row v-else align-v="center" align-h="center">
                <b-col>
                    <b-tabs>
                        <b-tab title="Computational Plant Science Lab" active>
                            <p class="text-dark mt-3">
                                Select a flow, go to the
                                <a
                                    class="hvr"
                                    href="https://computational-plant-science.org"
                                    ><i
                                        class="fas fa-vial fa-fw"
                                        style="z-index: 1000"
                                    ></i>
                                    Computational Plant Science Lab's website</a
                                >,
                                or check out the code on
                                <a
                                    class="hvr"
                                    href="https://github.com/Computational-Plant-Science/"
                                    ><i class="fab fa-github fa-fw"></i
                                    >GitHub</a
                                >
                                .
                            </p>
                            <b-card-text class="m-3">
                                <flows
                                    github-user="computational-plant-science"
                                    :github-token="
                                        currentUserDjangoProfile.profile
                                            .github_token
                                    "
                                >
                                </flows>
                            </b-card-text>
                        </b-tab>
                        <b-tab title="van der Knaap Lab">
                            <p class="text-dark mt-3">
                                Select a flow, go to the
                                <a
                                    class="hvr"
                                    href="http://vanderknaaplab.uga.edu/index.html"
                                    ><i
                                        class="fas fa-vial fa-fw"
                                        style="z-index: 1000"
                                    ></i>
                                    van der Knaap Lab's website</a
                                >,
                                or check out the code on
                                <a
                                    class="hvr"
                                    href="https://github.com/van-der-knaap-lab/"
                                    ><i class="fab fa-github fa-fw"></i
                                    >GitHub</a
                                >
                                .
                            </p>
                            <b-card-text class="m-3">
                                <flows
                                    github-user="van-der-knaap-lab"
                                    :github-token="
                                        currentUserDjangoProfile.profile
                                            .github_token
                                    "
                                >
                                </flows>
                            </b-card-text>
                        </b-tab>
                        <b-tab title="Burke Lab">
                            <p class="text-dark mt-3">
                                Select a flow, go to the
                                <a
                                    class="hvr"
                                    href="http://www.theburkelab.org/"
                                    ><i
                                        class="fas fa-vial fa-fw"
                                        style="z-index: 1000"
                                    ></i>
                                    Burke Lab's website</a
                                >,
                                or check out the code on
                                <a
                                    class="hvr"
                                    href="https://github.com/burkelab/"
                                    ><i class="fab fa-github fa-fw"></i
                                    >GitHub</a
                                >
                                .
                            </p>
                            <b-card-text class="m-">
                                <flows
                                    github-user="burke-lab"
                                    :github-token="
                                        currentUserDjangoProfile.profile
                                            .github_token
                                    "
                                >
                                </flows>
                            </b-card-text>
                        </b-tab>
                        <!--<b-tab title="Community">
                            <br />
                            <b-card-text class="m-3">
                                <flows
                                    github-user=""
                                    :github-token="
                                        currentUserDjangoProfile.profile
                                            .github_token
                                    "
                                >
                                </flows>
                            </b-card-text>
                        </b-tab>-->
                    </b-tabs>
                </b-col>
            </b-row>
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
