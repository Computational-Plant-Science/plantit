<template>
    <div class="w-100 p-4">
        <p>Select a <b>Workflow</b> to start a new <b>Job</b>.</p>
        <b-card header-bg-variant="light" border-variant="default">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            <i class="fas fa-stream text-dark"></i> Computational Plant Science Lab
                            Workflows
                        </h5>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="filter_cps_workflows_query"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!filter_cps_workflows_query"
                                    @click="filter_cps_workflows_query = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <div v-if="!filtered_cps_workflows.length">
                    None to show.
                </div>
                <b-card-group deck>
                    <b-card
                        v-for="workflow in filtered_cps_workflows"
                        :key="workflow.name"
                        class="overflow-hidden p-0 m-2"
                        style="min-width: 30rem"
                    >
                        <template slot="header">
                            <b-row>
                                <b-col>
                                    <h3>{{ workflow.name }}</h3>
                                </b-col>
                                <b-col md="auto">
                                    <b-button
                                        block
                                        variant="outline-dark"
                                        title="Start a new job"
                                        v-b-tooltip.hover
                                        @click="workflowSelected(workflow)"
                                    >
                                        <i class="fas fa-terminal"></i>
                                    </b-button>
                                </b-col>
                            </b-row>
                        </template>
                        <b-row no-gutters>
                            <b-col
                                md="auto"
                                style="min-width: 8em; max-width: 8rem; min-height: 8rem; max-height: 8rem"
                            >
                                <b-img
                                    v-if="workflow.icon_url"
                                    style="max-width: 8rem"
                                    :src="workflow.icon_url"
                                    right
                                >
                                </b-img>
                                <b-img
                                    v-else
                                    style="max-width: 8rem"
                                    :src="require('../assets/logo.png')"
                                    right
                                ></b-img>
                            </b-col>
                            <b-col>
                                <b-row>
                                    <b-col>
                                        <b-card-body>
                                            {{ workflow.description }}
                                        </b-card-body>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-card-group>
            </b-row>
        </b-card>
        <b-card header-bg-variant="light" border-variant="default" class="mt-3">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            <i class="fas fa-stream text-dark"></i> Your Public
                            Workflows
                        </h5>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="filter_public_user_workflows_query"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="
                                        !filter_public_user_workflows_query
                                    "
                                    @click="
                                        filter_public_user_workflows_query = ''
                                    "
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <div v-if="!filtered_public_user_workflows.length">
                    None to show.
                </div>
                <b-card-group deck class="pl-3 pr-3">
                    <b-card
                        v-for="workflow in filtered_public_user_workflows"
                        :key="workflow.name"
                        class="overflow-hidden p-0 m-2"
                        style="min-width: 30rem"
                    >
                        <template slot="header">
                            <b-row align-v="center">
                                <b-col>
                                    <h5>{{ workflow.name }}</h5>
                                </b-col>
                                <b-col md="auto">
                                    <b-button
                                        block
                                        variant="outline-dark"
                                        title="Start a new job"
                                        v-b-tooltip.hover
                                        @click="workflowSelected(workflow)"
                                    >
                                        <i class="fas fa-terminal"></i>
                                    </b-button>
                                </b-col>
                            </b-row>
                        </template>
                        <b-row no-gutters>
                            <b-col
                                md="auto"
                                style="min-width: 8em; max-width: 8rem; min-height: 8rem; max-height: 8rem"
                            >
                                <b-img
                                    v-if="workflow.icon_url"
                                    style="max-width: 8rem"
                                    :src="workflow.icon_url"
                                    right
                                >
                                </b-img>
                                <b-img
                                    v-else
                                    style="max-width: 8rem"
                                    :src="require('../assets/logo.png')"
                                    right
                                ></b-img>
                            </b-col>
                            <b-col>
                                <b-row>
                                    <b-col>
                                        <b-card-body>
                                            {{ workflow.description }}
                                        </b-card-body>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-card-group>
            </b-row>
        </b-card>
        <b-card header-bg-variant="light" border-variant="default" class="mt-3">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            <i class="fas fa-stream text-dark"></i> Your Private
                            Workflows
                        </h5>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="filter_private_user_workflows_query"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="
                                        !filter_private_user_workflows_query
                                    "
                                    @click="
                                        filter_private_user_workflows_query = ''
                                    "
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <div v-if="!filtered_private_user_workflows.length">
                    None to show.
                </div>
                <b-card-group deck class="pl-3 pr-3">
                    <b-card
                        v-for="workflow in filtered_private_user_workflows"
                        :key="workflow.name"
                        class="overflow-hidden p-0 m-2"
                        style="min-width: 30rem"
                    >
                        <template slot="header">
                            <b-row align-v="center">
                                <b-col>
                                    <h5>{{ workflow.name }}</h5>
                                </b-col>
                                <b-col md="auto">
                                    <b-button
                                        block
                                        variant="outline-dark"
                                        title="Start a new job"
                                        v-b-tooltip.hover
                                        @click="workflowSelected(workflow)"
                                    >
                                        <i class="fas fa-terminal"></i>
                                    </b-button>
                                </b-col>
                            </b-row>
                        </template>
                        <b-row no-gutters>
                            <b-col
                                md="auto"
                                style="min-width: 8em; max-width: 8rem; min-height: 8rem; max-height: 8rem"
                            >
                                <b-img
                                    v-if="workflow.icon_url"
                                    style="max-width: 8rem"
                                    :src="workflow.icon_url"
                                    right
                                >
                                </b-img>
                                <b-img
                                    v-else
                                    style="max-width: 8rem"
                                    :src="require('../assets/logo.png')"
                                    right
                                ></b-img>
                            </b-col>
                            <b-col>
                                <b-row>
                                    <b-col>
                                        <b-card-body>
                                            {{ workflow.description }}
                                        </b-card-body>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-card-group>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import UserApi from '@/services/apiV1/UserManager.js';

export default {
    name: 'ListWorkflows',
    components: {},
    data: function() {
        return {
            filter_cps_workflows_query: '',
            filter_public_user_workflows_query: '',
            filter_private_user_workflows_query: '',
            cps_workflows: [],
            public_user_workflows: [],
            private_user_workflows: []
        };
    },
    mounted: function() {
        WorkflowAPI.getWorkflows().then(data => {
            this.cps_workflows = data.workflows || [];
        });
        UserApi.getCurrentUserGithubRepos().then(workflows => {
            if (workflows == null) {
                this.public_user_workflows = [];
            } else {
                this.public_user_workflows = workflows.filter(
                    wf => wf['config']['public'] === true
                );
                this.private_user_workflows = workflows.filter(
                    wf => wf['config']['public'] === false
                );
            }
        });
    },
    computed: {
        filter_cps_workflows_text: function() {
            return this.filter_cps_workflows_query.toLowerCase();
        },
        filter_public_user_workflows_text: function() {
            return this.filter_public_user_workflows_query.toLowerCase();
        },
        filter_private_user_workflows_text: function() {
            return this.filter_private_user_workflows_query.toLowerCase();
        },
        filtered_cps_workflows: function() {
            if (this.filter_cps_workflows_text === '') {
                return this.cps_workflows;
            } else {
                return this.cps_workflows.filter(w => {
                    return (
                        w.name
                            .toLowerCase()
                            .includes(this.filter_cps_workflows_text) ||
                        w.description
                            .toLowerCase()
                            .includes(this.filter_cps_workflows_text)
                    );
                });
            }
        },
        filtered_public_user_workflows: function() {
            if (this.filter_public_user_workflows_text === '') {
                return this.public_user_workflows;
            } else {
                return this.public_user_workflows.filter(w => {
                    return (
                        w.name
                            .toLowerCase()
                            .includes(this.filter_public_user_workflows_text) ||
                        w.description
                            .toLowerCase()
                            .includes(this.filter_public_user_workflows_text)
                    );
                });
            }
        },
        filtered_private_user_workflows: function() {
            if (this.filter_private_user_workflows_text === '') {
                return this.private_user_workflows;
            } else {
                return this.private_user_workflows.filter(w => {
                    return (
                        w.name
                            .toLowerCase()
                            .includes(
                                this.filter_private_user_workflows_text
                            ) ||
                        w.description
                            .toLowerCase()
                            .includes(this.filter_private_user_workflows_text)
                    );
                });
            }
        }
    },
    methods: {
        workflowSelected: function(workflow) {
            this.$emit('workflowSelected', workflow);
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button

.workflow
    width: 300px

.workflow-text
    background-color: $color-box-background
    padding: 10px
</style>

<style scoped lang="sass">
@import '../scss/_colors.sass'
</style>
