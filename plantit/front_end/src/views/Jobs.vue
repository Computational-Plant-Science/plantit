<template>
    <div class="m-0 p-0">
        <b-container>
            <p>
                The <i>job</i> is PlantIT's fundamental unit of execution. Each job submits a workflow and an associated collection to a cluster, then returns results.
            </p>
            <p>
                To start a new job, go to the <b-link href="/user/workflows">workflows</b-link> page or click the <i class="fas fa-plus"></i>  icon below to select a workflow. Select an existing job to view logs and results.
            </p>
            <SelectJob filterable="true"></SelectJob>
        </b-container>
    </div>
</template>

<script>
    import SelectJob from '@/components/SelectJob.vue';

    export default {
        name: 'Jobs',
        components: {
            SelectJob,
        }
    };
</script>
