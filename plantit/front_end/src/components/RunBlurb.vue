<template>
    <div v-if="workflow.config">
        <b-row>
            <b-col>
                <h1>
                    Run
                    <b
                        ><small>{{ run.id }}</small></b
                    >
                </h1>
                <h2>
                    <b-badge :variant="run.state === 2 ? 'danger' : 'success'"
                        >{{ statusToString(run.state) }}
                    </b-badge>
                    on
                    <b-badge variant="secondary" class="text-white">{{
                        run.cluster
                    }}</b-badge>
                </h2>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col>
                <b-card
                    bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="dark"
                    footer-border-variant="white"
                    style="min-height: 5rem; max-height: 15rem;"
                    class="overflow-hidden"
                >
                    <WorkflowBlurb
                        :showPublic="false"
                        :workflow="workflow"
                        :selectable="false"
                    ></WorkflowBlurb>
                </b-card>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import WorkflowBlurb from '@/components/WorkflowBlurb.vue';

export default {
    name: 'RunBlurb',
    components: {
        WorkflowBlurb
    },
    props: {
        workflow: {
            type: Object,
            required: true
        },
        run: {
            type: Object,
            required: true
        },
        selectable: {
            type: Boolean,
            required: true
        }
    },
    methods: {
        statusToString(status) {
            switch (status) {
                case 1:
                    return 'Completed';
                case 2:
                    return 'Failed';
                case 3:
                    return 'Running';
                case 4:
                    return 'Created';
            }
        }
    }
};
</script>

<style scoped></style>
