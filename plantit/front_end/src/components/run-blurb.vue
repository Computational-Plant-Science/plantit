<template>
    <div v-if="flow.config">
        <b-row>
            <b-col align-self="end">
                <b-badge variant="white"
                    ><i class="fas fa-terminal fa-1x fa-fw"></i> Run</b-badge
                >
                <h3 :class="darkMode ? 'theme-dark' : 'theme-light'">
                    {{ run.id }}
                </h3>
            </b-col>
            <b-col md="auto" align-self="end" class="mb-2">
                <h4 :class="darkMode ? 'theme-dark' : 'theme-light'">
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
                        run.target
                    }}</b-badge>
                </h4>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <b-card
                    :bg-variant="darkMode ? 'dark' : 'white'"
                    :footer-bg-variant="darkMode ? 'dark' : 'white'"
                    border-variant="secondary"
                    :footer-border-variant="darkMode ? 'dark' : 'white'"
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
                    username: flow['repository']['owner']['login'],
                    name: flow['repository']['name']
                }
            });
        }
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserCyVerseProfile',
            'currentUserGitHubProfile',
            'loggedIn',
            'darkMode'
        ])
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
</style>
