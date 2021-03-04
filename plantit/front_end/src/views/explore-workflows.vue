<template>
    <div
        class="w-100 h-100 pl-3 pt-3 pr-0 m-0"
        :style="
            profile.darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <b-container class="pl-3 pt-3 mr-3" fluid>
            <b-row align-v="center" align-h="center" v-if="workflowsLoading">
                <b-col align-self="end" class="text-center">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </b-col>
            </b-row>
            <b-row
                align-v="center"
                align-h="center"
                v-if="workflows.length === 0 && !workflowsLoading"
                ><b-col :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    >No workflows to show!</b-col
                ></b-row
            >
            <b-row
                v-if="profile.githubProfile === null"
                align-v="center"
                align-h="center"
                class="p-2 text-center"
            >
                <b-col class="mr-2 pr-0 text-right">
                    <b-button
                        variant="success"
                        href="/apis/v1/users/github_request_identity/"
                        class="mr-0"
                    >
                        <i class="fab fa-github"></i>
                        Log in to GitHub
                    </b-button>
                </b-col>
                <b-col class="ml-0 pl-0 text-left">
                    <b class="ml-0 pl-0">to load workflows.</b>
                </b-col>
            </b-row>
            <b-row v-else align-v="center" align-h="center">
                <workflows
                    :github-token="profile.djangoProfile.github_token"
                    :workflows="publicWorkflows"
                >
                </workflows>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import { mapGetters } from 'vuex';
import workflows from '@/components/workflows.vue';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'explore-workflows',
    data() {
        return {
            currentTab: 0
        };
    },
    components: {
        workflows
    },
    async mounted() {
        await this.$store.dispatch('loadWorkflows');
    },
    computed: {
        ...mapGetters(['profile', 'workflows', 'workflowsLoading']),
        publicWorkflows() {
            if (this.workflowsLoading) return [];
            return this.workflows.filter(wf => wf.config.public);
        }
    },
    methods: {
        tabLinkClass(idx) {
            if (this.currentTab === idx) {
                return this.profile.darkMode ? '' : 'text-dark';
            } else {
                return this.profile.darkMode
                    ? 'background-dark text-light'
                    : 'text-dark';
            }
        },
        users() {
            router.push({
                name: 'users'
            });
        },
        workflowSelected: function(flow) {
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
