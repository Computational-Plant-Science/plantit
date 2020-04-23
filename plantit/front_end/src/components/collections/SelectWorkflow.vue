<template>
    <div class="w-100 pb-4">
        <b-card header-bg-variant="dark" border-variant="dark">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5><i class="fas fa-stream green"></i> Select Workflow</h5>
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
                            border-variant="white"
                            footer-bg-variant="dark"
                            class="workflow"
                        >
                            <div class="workflow-icon">
                                <b-img :src="workflow.icon_url"> </b-img>
                            </div>
                            <br />
                            <b-card-body class="m-1 p-1" :title="workflow.name">
                                {{ workflow.description }}
                                <br />
                                <br />
                                <b-button
                                    block
                                    variant="outline-dark"
                                    title="Start a new job"
                                    v-b-tooltip.hover
                                    :to="{
                                        name: 'submit_workflow',
                                        query: {
                                            collection_pk: workflow.pk,
                                            workflow_name: workflow.app_name
                                        }
                                    }"
                                >
                                    <i class="fas fa-terminal"></i>
                                </b-button>
                            </b-card-body>
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
@import "../../scss/main.sass"

.green
    color: $color-button

.workflow
    width: 300px

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: $secondary
    border-radius: 50%
    border: 4px solid $dark
    padding: 24px

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
