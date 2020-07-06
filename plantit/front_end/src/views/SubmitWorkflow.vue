<template>
    <div class="w-100 p-4">
        <b-card header-bg-variant="light" border-variant="default" class="mb-4">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Description
                        </h5>
                    </b-col>
                </b-row>
            </template>
            <b-card-body>
                {{ workflow.repo.description }}
            </b-card-body>
        </b-card>
        <b-card header-bg-variant="light" border-variant="default" class="mb-4">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Parameters
                        </h5>
                    </b-col>
                </b-row>
            </template>
            <b-card-body>
                <EditParameters :params="params"></EditParameters>
            </b-card-body>
            <!--<b-card-body>
                <vue-json-editor v-model="params" :show-btns="true" :expandedOnStart="true" @json-change="onJsonChange"></vue-json-editor>
            </b-card-body>-->
        </b-card>
        <b-card header-bg-variant="light" border-variant="default" class="mb-4">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Target
                        </h5>
                    </b-col>
                </b-row>
            </template>
            <b-card-body>
                <SelectTarget :selected="target" v-on:targetSelected="targetSelected"></SelectTarget>
            </b-card-body>
            <template v-slot:footer style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Selected: {{ target.name }}
                        </h5>
                    </b-col>
                </b-row>
            </template>
        </b-card>
    </div>
    <!--<NewCollection>

        </NewCollection>
        <SelectCollection
            class="pb-4"
            selectable="true"
            filterable="true"
            per-page="4"
            v-on:selected="onSelected"
        ></SelectCollection>
        <SetParameters
            class="pb-4"
            :workflow_name="this.name"
            v-on:submit="onSubmit"
        ></SetParameters>-->
</template>

<script>
// import vueJsonEditor from 'vue-json-editor'
import EditParameters from "../components/EditParameters";
import SelectTarget from "../components/SelectTarget";
// import NewCollection from '@/views/NewCollection.vue';
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
// import SelectCollection from '@/components/collections/SelectCollection.vue';
import * as Sentry from '@sentry/browser';
// import SetParameters from '../components/collections/SetParameters';

export default {
    name: 'SubmitWorkflow',
    components: {
        // NewCollection,
        // SetParameters,
        // SelectCollection,
        EditParameters,
        SelectTarget
    },
    props: {
        owner: {
            required: true
        },
        name: {
            required: true
        }
    },
    data: function() {
        return {
            collection_pk: null,
            workflow: null,
            params: [],
            values: {},
            target: {
                name: 'None'
            }
        };
    },
    mounted: function() {
        WorkflowAPI.getWorkflow(this.owner, this.name).then(workflow => {
            this.workflow = workflow;
            this.params = workflow.config.params.map(function(param) {
                return {
                    key: param,
                    value: ''
                };
            });
        });
    },
    methods: {
        onChange(group, values) {
            // Make values reactive
            this.values[group] = values;
        },
        onSelected(collection) {
            this.collection_pk = collection.pk;
        },
        targetSelected(target) {
            this.target = target;
        },
        onSubmit(values) {
            WorkflowAPI.submitJob(this.name, this.collection_pk, values).then(
                result => {
                    if (result.status === 200) {
                        this.$emit('workflowSubmitted', result.data.job_id);
                    } else {
                        //TODO: Replace this with something to alerts the user.
                        Sentry.captureMessage('Submission Failed:' + result);
                    }
                }
            );
        },
        saveMetadata() {
            // TODO update job
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: white
    padding: 24px

    img
        margin-top: 20px
        max-width: 140px
        max-height: 190px

.workflow-text
    background-color: $dark
    padding: 10px
</style>
