<template>
    <div class="w-100 p-2 pb-4">
        <b-container class="justify-content-md-center">
            <b-card>
                <b-row>
                    <b-col>
                        <h3>Select Workflow</h3>
                    </b-col>
                    <b-col md="auto">
                        <b-form-group label-cols-sm="2" style="width: 400px">
                            <b-input-group>
                                <b-form-input
                                    v-model="filter_query"
                                    placeholder="Type to Filter"
                                ></b-form-input>
                                <b-input-group-append>
                                    <b-button
                                        :disabled="!filter_query"
                                        @click="filter_query = ''"
                                        >Clear
                                    </b-button>
                                </b-input-group-append>
                            </b-input-group>
                        </b-form-group>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <div
                            class="d-flex flex-wrap justify-content-center align-items-stretch row-eq-height"
                        >
                            <div
                                v-for="workflow in filtered"
                                :key="workflow.name"
                                class="p-3 m-3 workflow"
                            >
                                <div class="workflow-icon">
                                    <b-img :src="workflow.icon_url"></b-img>
                                </div>
                                <div>
                                    <b-link
                                        :to="{
                                            name: 'submit_workflow',
                                            query: {
                                                collection_pk: pk,
                                                workflow_name: workflow.app_name
                                            }
                                        }"
                                    >
                                        {{ workflow.name }}
                                    </b-link>
                                    <hr />
                                    {{ workflow.description }}
                                </div>
                            </div>
                        </div>
                    </b-col>
                </b-row>
            </b-card>
        </b-container>
    </div>
</template>

<script>
import WorkflowAPI from '@/services/apiV1/WorkflowManager';

export default {
    name: 'Analyze',
    components: {},
    props: {
        pk: {
            required: true
        }
    },
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
@import "../scss/_colors.sass"

.workflow
    width: 300px

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: $color-disabled
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
