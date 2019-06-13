<template>
    <div style="text-align:center">
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
                <b-nav-item to="/user/jobs">Jobs</b-nav-item>
            </template>
            <template v-slot:buttons> </template>
        </PageNavigation>

        <b-container class="content-box center-container">
            <h1>Workflow Parameters</h1>
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
                <b-button type="submit" variant="primary" class="m-2"
                    >Submit</b-button
                >
                <b-button variant="danger" class="m-2">Cancel</b-button>
            </b-form>
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import PageNavigation from '@/components/PageNavigation.vue';
import FormGroup from '@/components/FormGroup';
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import * as Sentry from '@sentry/browser';

export default {
    name: 'SubmitWorkflow',
    components: {
        PageNavigation,
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
                if (result.status == 200) {
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
