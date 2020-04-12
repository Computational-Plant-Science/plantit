<template>
    <div class="w-100 p-2 pb-4">
        <b-container>
            <b-card>
                <b-row>
                    <b-col>
                        <h3>Workflow Parameters</h3>
                    </b-col>
                </b-row>
                <hr />
                <b-row>
                    <b-col>
                        <b-form
                            @submit="onSubmit"
                            style="text-align: left;"
                            ref="form"
                            id="my-form"
                        >
                            <FormGroup
                                v-for="group in params"
                                :key="group.id"
                                :group="group"
                                @onChange="onChange"
                            >
                            </FormGroup>
                            <hr>
                            <b-button
                                type="submit"
                                variant="primary"
                                class="m-2"
                                >Submit</b-button
                            >
                            <b-button variant="danger" class="m-2"
                                >Cancel</b-button
                            >
                        </b-form>
                    </b-col>
                </b-row>
            </b-card>
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import FormGroup from '@/components/FormGroup';
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import * as Sentry from '@sentry/browser';

export default {
    name: 'SubmitWorkflow',
    components: {
        FormGroup
    },
    props: {
        collection_pk: {
            // the pk of the collection to analyze
            required: true
        },
        workflow_name: {
            // the app_name of the selected workflow
            required: true
        }
    },
    data: function() {
        return {
            // Paramaters for the workflow
            params: [],
            // The values of the paramaters
            // values is automatically updated as users select options, and
            // is reactive.
            values: {}
        };
    },
    mounted: function() {
        WorkflowAPI.getParameters(this.workflow_name).then(params => {
            this.params = params;
        });
    },
    methods: {
        onChange(group, values) {
            // Make values reactive
            this.values[group] = values;
        },
        onSubmit(evt) {
            evt.preventDefault();
            WorkflowAPI.submitJob(
                this.workflow_name,
                this.collection_pk,
                this.values
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
