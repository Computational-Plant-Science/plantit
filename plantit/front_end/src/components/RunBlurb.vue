<template>
    <div v-if="flow.config">
        <b-row>
            <b-col>
                <h3>
                    <b>{{ run.id }}</b>
                </h3>
            </b-col>
            <b-col md="auto">
                <h4>
                    <b-badge
                        :variant="
                            run.state === 2
                                ? 'danger'
                                : run.state === 1
                                ? 'success'
                                : 'warning'
                        "
                        >{{ statusToString(run.state) }}
                    </b-badge>
                    on
                    <b-badge variant="secondary" class="text-white">{{
                        run.cluster
                    }}</b-badge>
                </h4>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <b-card
                    bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="dark"
                    footer-border-variant="white"
                    style="min-height: 5rem;"
                    class="overflow-hidden"
                >
                    <WorkflowBlurb
                        :showPublic="false"
                        :flow="flow"
                        selectable="Restart"
                    ></WorkflowBlurb>
                </b-card>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import WorkflowBlurb from '@/components/flow-blurb.vue';
import router from '@/router';

export default {
    name: 'RunBlurb',
    components: {
        WorkflowBlurb
    },
    props: {
        flow: {
            type: Object,
            required: true
        },
        run: {
            type: Object,
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
        },
        flowSelected: function(flow) {
            router.push({
                name: 'flow',
                params: {
                    username: flow['repository']['owner']['login'],
                    name: flow['repository']['name']
                }
            });
        }
    }
};
</script>

<style scoped></style>
