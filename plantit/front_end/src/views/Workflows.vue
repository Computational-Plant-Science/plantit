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
                        <h1>Community Workflows</h1>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
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
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <b-row align-h="center" v-if="communityWorkflowsLoading">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="dark"
                    ></b-spinner>
                </b-row>
                <div
                    v-if="
                        !communityWorkflowsLoading &&
                            communityWorkflowsAfterFilter.length === 0
                    "
                >
                    None to show.
                </div>
                <b-card-group deck class="justify-content-center">
                    <b-card
                        v-for="workflow in communityWorkflowsAfterFilter"
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
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
            v-if="
                !userWorkflowsLoading && userWorkflowsAfterFilter.length !== 0
            "
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h1>Your Workflows</h1>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="userWorkflowsFilter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!userWorkflowsFilter"
                                    @click="userWorkflowsFilter = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <b-row align-h="center" v-if="userWorkflowsLoading">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="dark"
                    ></b-spinner>
                </b-row>
                <div
                    v-if="
                        !userWorkflowsLoading &&
                            userWorkflowsAfterFilter.length === 0
                    "
                >
                    None to show.
                </div>
                <b-card-group deck columns class="justify-content-center">
                    <b-card
                        v-for="workflow in userWorkflowsAfterFilter"
                        :key="workflow.repo.name"
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="white"
                        footer-border-variant="white"
                        header-border-variant="dark"
                        style="min-width: 30rem; max-width: 30rem; min-height: 5rem; max-height: 15rem;"
                        class="overflow-hidden mb-4"
                    >
                        <WorkflowBlurb
                            :showPublic="true"
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
import Workflows from '@/services/apiV1/Workflows';
import Users from '@/services/apiV1/Users.js';
import WorkflowBlurb from '@/components/WorkflowBlurb.vue';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'Pipelines',
    components: {
        WorkflowBlurb
    },
    data: function() {
        return {
            communityWorkflows: [],
            communityWorkflowsLoading: false,
            communityWorkflowsFilter: '',
            userWorkflows: [],
            userWorkflowsLoading: false,
            userWorkflowsFilter: ''
        };
    },
    mounted: function() {
        this.loadCommunityWorkflows();
        this.loadUserWorkflows();
    },
    computed: {
        communityWorkflowsFilterText: function() {
            return this.communityWorkflowsFilter.toLowerCase();
        },
        userWorkflowsFilterText: function() {
            return this.userWorkflowsFilter.toLowerCase();
        },
        communityWorkflowsAfterFilter: function() {
            if (this.communityWorkflowsFilterText === '') {
                return this.communityWorkflows;
            } else {
                return this.communityWorkflows.filter(workflow => {
                    return (
                        workflow.repo.name
                            .toLowerCase()
                            .includes(this.communityWorkflowsFilterText) ||
                        workflow.repo.description
                            .toLowerCase()
                            .includes(this.communityWorkflowsFilterText)
                    );
                });
            }
        },
        userWorkflowsAfterFilter: function() {
            if (this.userWorkflowsFilterText === '') {
                return this.userWorkflows;
            } else {
                return this.userWorkflows.filter(workflow => {
                    return (
                        workflow.repo.name
                            .toLowerCase()
                            .includes(this.userWorkflowsFilterText) ||
                        workflow.repo.description
                            .toLowerCase()
                            .includes(this.userWorkflowsFilterText)
                    );
                });
            }
        }
    },
    methods: {
        sortWorkflows(l, r) {
            if (l.config.name < r.config.name) return -1;
            if (l.config.name > r.config.name) return 1;
            return 0;
        },
        loadCommunityWorkflows() {
            this.communityWorkflowsLoading = true;
            Workflows.list().then(workflows => {
                if (workflows.pipelines == null) {
                    this.communityWorkflows = [];
                } else {
                    workflows.pipelines.sort(this.sortWorkflows);
                    this.communityWorkflows = workflows.pipelines;
                }
                this.communityWorkflowsLoading = false;
            });
        },
        loadUserWorkflows() {
            this.userWorkflowsLoading = true;
            Users.getCurrentUserGithubRepos().then(workflows => {
                if (workflows == null) {
                    this.userWorkflows = [];
                } else {
                    workflows.sort(this.sortWorkflows);
                    this.userWorkflows = workflows;
                }
                this.userWorkflowsLoading = false;
            });
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
