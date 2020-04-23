<template>
    <div class="w-100">
        <b-card
            header-bg-variant="dark"
            footer-bg-variant="light"
            border-variant="dark"
        >
            <template v-slot:header style="background-color: white">
                <b-row>
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            <i class="fas fa-list-ul green"></i> Set Parameters
                        </h5>
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
                    </b-form>
                </b-col>
            </b-row>
            <template v-slot:footer>
                <b-row>
                    <b-col>
                        <b-button block variant="outline-danger"
                            >Cancel</b-button
                        >
                    </b-col>
                    <b-col>
                        <b-button block type="submit" variant="outline-dark" @click="onSubmit"
                            >Submit</b-button
                        >
                    </b-col>
                </b-row>
            </template>
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

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.green
    color: $color-button
</style>
