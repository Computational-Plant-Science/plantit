<template>
    <div>
        <div class="mb-4 pt-4">
            <div class="workflow-icon">
                <b-img :src="workflow ? workflow.workflow.icon_url ? workflow.workflow.icon_url : require('../assets/logo.png') : require('../assets/logo.png')"> </b-img>
            </div>
            <br />
            <br />
            <h4>{{ workflow ? workflow.workflow.name : 'Loading...' }}</h4>
            <p>
                {{ workflow ? workflow.workflow.description : 'Loading...' }}
            </p>
        </div>
        <NewCollection>

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
            :workflow_name="this.workflow_name"
            v-on:submit="onSubmit"
        ></SetParameters>
    </div>
</template>

<script>
import NewCollection from '@/views/NewCollection.vue';
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import SelectCollection from '@/components/collections/SelectCollection.vue';
import * as Sentry from '@sentry/browser';
import SetParameters from '../components/collections/SetParameters';

export default {
    name: 'SubmitWorkflow',
    components: {
        NewCollection,
        SetParameters,
        SelectCollection,
    },
    props: {
        workflow_name: {
            required: true
        }
    },
    data: function() {
        return {
            collection_pk: null,
            workflow: null,
            params: [],
            values: {}
        };
    },
    mounted: function() {
        WorkflowAPI.getWorkflow(this.workflow_name).then(wf => {
            this.workflow = wf;
            this.params = wf.parameters;
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
        onSubmit(values) {
            WorkflowAPI.submitJob(
                this.workflow_name,
                this.collection_pk,
                values
            ).then(result => {
                if (result.status === 200) {
                    this.$emit('workflowSubmitted', result.data.job_id);
                } else {
                    //TODO: Replace this with something to alerts the user.
                    Sentry.captureMessage('Submission Failed:' + result);
                }
            });
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
