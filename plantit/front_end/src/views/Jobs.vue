<template>
    <div class="m-0 p-0">
        <b-container>
            <h3>
                <i class="fas fa-terminal"></i> Jobs
            </h3>
            <hr>
            <p>
                The <i>job</i> is PlantIT's fundamental unit of execution. Each job is associated with a data <i>collection</i>,
                an analysis <i>workflow</i>, and a resource <i>cluster</i>.
            </p>
            <p>
                To start a new job, go to the <b-link href="/user/workflows">workflows</b-link> page. Alternatively, click the <i class="fas fa-plus"></i>  icon below and select a workflow. Select an existing job to view logs and results.
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
