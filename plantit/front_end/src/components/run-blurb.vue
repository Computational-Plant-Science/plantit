<template>
    <div v-if="flow.config">
        <!--<b-row class="mb-0">
            <b-col class="mb-0" align-self="end" md="auto">
                <h5 :class="profile.darkMode ? 'theme-dark' : 'theme-light'">
                    {{ run.id }}
                </h5>
            </b-col>
        </b-row>-->
        <b-row class="mt-0">
            <b-col class="mt-0">
                <b-card
                    :bg-variant="profile.darkMode ? 'dark' : 'white'"
                    :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
                    border-variant="default"
                    :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
                    style="min-height: 5rem;"
                    class="overflow-hidden mt-0"
                >
                    <WorkflowBlurb
                        :showPublic="false"
                        workflow="flow"
                    ></WorkflowBlurb>
                </b-card>
            </b-col>
        </b-row>
      <!--<b-row class="mt-1">
            <b-col align-self="end">
                <h4 :class="profile.darkMode ? 'theme-dark' : 'theme-light'">
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
            <b-col md="auto" align-self="start">
                {{ run.description }}
            </b-col>
        <b-col md="auto" align-self="start">

        </b-col>
        </b-row>-->
    </div>
</template>

<script>
import WorkflowBlurb from '@/components/workflow-blurb.vue';
import router from '@/router';
import { mapGetters } from 'vuex';

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
                    username: flow['repo']['owner']['login'],
                    name: flow['repo']['name']
                }
            });
        }
    },
    computed: {
        ...mapGetters('user', [
            'profile',
        ])
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
</style>
