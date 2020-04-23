<template>
    <div class="w-100">
        <b-container>
            <h3><i class="fas fa-play"></i> Start Workflow</h3>
            <hr />
            <div class="mb-4 pt-4">
                <div class="workflow-icon">
                    <b-img :src="workflow.workflow.icon_url"> </b-img>
                </div>
                <br />
                <h4>{{ workflow.workflow.name }}</h4>
                <p>
                    {{ workflow.workflow.description }}
                </p>
            </div>
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
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import SelectCollection from '@/components/collections/SelectCollection.vue';
import * as Sentry from '@sentry/browser';
import SetParameters from '../components/collections/SetParameters';

export default {
    name: 'SubmitWorkflow',
    components: {
        SetParameters,
        SelectCollection
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
                    router.push({
                        name: 'job',
                        query: { pk: result.data.job_id }
                    });
                } else {
                    //TODO: Replace this with something to alerts the user.
                    Sentry.captureMessage('Submission Failed:' + result);
                }
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"

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
