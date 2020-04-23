<template>
    <div class="w-100 m-0 p-0">
        <b-container>
            <h3><i class="fas fa-stream"></i> Workflows</h3>
            <hr />
            <p>
                A <i>workflow</i> represents a self-contained analysis pipeline.
                Select a workflow below to start analyzing data.
            </p>
            <SelectWorkflow filterable="true"></SelectWorkflow>
        </b-container>
    </div>
</template>

<script>
import SelectWorkflow from '@/components/collections/SelectWorkflow.vue';

export default {
    name: 'Workflows',
    components: {
        SelectWorkflow
    }
};
</script>

<style scoped></style>
