<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h1>Workflows</h1>
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
            <b-row align-h="center">
                <b-row
                    v-if="githubProfile === null"
                    align-v="center"
                    align-h="center"
                >
                    <b-col>
                        <b-button
                            block
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
                            >to load workflows</b
                        >
                    </b-col>
                </b-row>
                <b-card-group deck class="justify-content-center" v-else>
                    <b-card
                        v-for="workflow in workflows"
                        :key="workflow.repo.name"
                        bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="dark"
                        footer-border-variant="white"
                        style="min-width: 30rem; max-width: 30rem; min-height: 5rem; max-height: 15rem;"
                        class="overflow-hidden mb-4"
                    >
                        <WorkflowBlurb
                            :showPublic="false"
                            :workflow="workflow"
                            :selectable="true"
                            v-on:workflowSelected="workflowSelected"
                        ></WorkflowBlurb>
                    </b-card>
                </b-card-group>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import router from '../router';
import { mapGetters } from 'vuex';
import WorkflowBlurb from '@/components/WorkflowBlurb.vue';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'Workflows',
    components: {
        WorkflowBlurb
    },
    data: function() {
        return {
            workflows: []
        };
    },
    created: function() {
        this.$store.dispatch('loadWorkflows');
    },
    computed: mapGetters([
        'user',
        'githubProfile',
        'cyverseProfile',
        'loggedIn',
        'workflows'
    ]),
    methods: {
        sortWorkflows(l, r) {
            if (l.config.name < r.config.name) return -1;
            if (l.config.name > r.config.name) return 1;
            return 0;
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

.workflow-text
  background-color: $color-box-background
  padding: 10px
</style>

<style scoped lang="sass">
@import '../scss/_colors.sass'
</style>
