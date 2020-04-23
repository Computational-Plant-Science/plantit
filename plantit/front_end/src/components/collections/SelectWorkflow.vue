<template>
    <div class="w-100 pb-4">
        <b-card header-bg-variant="dark" border-variant="dark">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>Select Workflow...</h5>
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
            <b-row>
                <b-col>
                    <div
                        class="d-flex flex-wrap align-items-stretch row-eq-height"
                    >
                        <b-card
                            v-for="workflow in filtered"
                            :key="workflow.name"
                            border-variant="dark"
                            footer-bg-variant="dark"
                            class="m-1 workflow"
                        >
                            <div class="workflow-icon">
                                <b-img
                                    :src="workflow.icon_url"
                                >
                                </b-img>
                            </div>
                            <br />
                            <b-card-body class="m-1 p-1" :title="workflow.name">
                                {{ workflow.description }}
                            </b-card-body>
                            <template
                                v-slot:footer
                                style="background-color: white"
                            >
                                <b-row>
                                    <b-col>
                                        <b-button
                                            block
                                            variant="dark"
                                            title="Start a new job"
                                            v-b-tooltip.hover
                                            :to="{
                                                name: 'submit_workflow',
                                                query: {
                                                    collection_pk: workflow.pk,
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
                        </b-card>
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

.workflow
    width: 300px

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: #343a40
    border-radius: 50%
    padding: 25px

    img
        margin-top: 20px
        max-width: 140px
        max-height: 190px

.workflow-text
    background-color: $color-box-background
    padding: 10px
</style>

<style scoped lang="sass">
@import '../../scss/_colors.sass'

</style>
