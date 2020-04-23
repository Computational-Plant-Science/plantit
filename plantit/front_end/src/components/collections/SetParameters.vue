<template>
    <div class="w-100">
        <b-card header-bg-variant="dark" border-variant="dark">
            <template v-slot:header style="background-color: white">
                <b-row>
                    <b-col class="mt-2" style="color: white">
                        <h5>Set Parameters...</h5>
                    </b-col>
                </b-row>
            </template>
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
                        <hr />
                        <b-button type="submit" variant="primary" class="m-2"
                            >Submit</b-button
                        >
                        <b-button variant="danger" class="m-2">Cancel</b-button>
                    </b-form>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import FormGroup from '@/components/FormGroup';

export default {
    name: 'ListParameters',
    components: {
        FormGroup
    },
    props: {
        workflow_name: {
            required: true
        }
    },
    data: function() {
        return {
            params: [],
            values: {}
        };
    },
    mounted: function() {
        WorkflowAPI.getWorkflow(this.workflow_name).then(wf => {
            this.params = wf.parameters;
        });
    },
    methods: {
        onSubmit(evt) {
            evt.preventDefault();
            this.$emit('submit', this.values);
        },
        onChange(group, values) {
            // Make values reactive
            this.values[group] = values;
        }
    }
};
</script>

<style scoped></style>
