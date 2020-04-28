<template>
    <div class="w-100 pb-4">
        <b-card header-bg-variant="dark" border-variant="white">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            <i class="fas fa-stream green"></i> Workflows
                        </h5>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="filter_query"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!filter_query"
                                    @click="filter_query = ''"
                                    variant="dark"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <p>
                Select a workflow to start analyzing data.
            </p>
            <b-row>
                <b-col>
                    <div
                        class="d-flex flex-wrap align-items-stretch row-eq-height"
                    >
                        <b-card-group>
                            <b-card
                                v-for="workflow in filtered"
                                :key="workflow.name"
                                border-variant="white"
                                footer-bg-variant="dark"
                                header-bg-variant="white"
                                header-border-variant="dark"
                                class="overflow-hidden p-2 m-2"
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
                                                :to="{
                                                    name: 'submit_workflow',
                                                    query: {
                                                        collection_pk:
                                                            workflow.pk,
                                                        workflow_name:
                                                            workflow.app_name
                                                    }
                                                }"
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
                                            :src="
                                                require('../../assets/logo.png')
                                            "
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
                    </div>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import WorkflowAPI from '@/services/apiV1/WorkflowManager';

export default {
    name: 'ListWorkflows',
    components: {},
    data: function() {
        return {
            filter_query: '',
            workflows: []
        };
    },
    mounted: function() {
        WorkflowAPI.getWorkflows().then(workflows => {
            this.workflows = workflows;
        });
    },
    computed: {
        filter_text: function() {
            return this.filter_query.toLowerCase();
        },
        filtered: function() {
            if (this.filter_text === '') {
                return this.workflows;
            } else {
                return this.workflows.filter(w => {
                    return (
                        w.name.toLowerCase().includes(this.filter_text) ||
                        w.description.toLowerCase().includes(this.filter_text)
                    );
                });
            }
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.green
    color: $color-button

.workflow
    width: 300px

.workflow-text
    background-color: $color-box-background
    padding: 10px
</style>

<style scoped lang="sass">
@import '../../scss/_colors.sass'
</style>
