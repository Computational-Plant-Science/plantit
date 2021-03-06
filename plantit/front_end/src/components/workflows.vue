<template>
    <b-row align-h="center">
        <b-card-group deck columns class="justify-content-center">
            <b-card
                v-for="workflow in workflows"
                :key="workflow.repo.name"
                :bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                border-variant="default"
                :header-border-variant="
                    profile.darkMode ? 'secondary' : 'default'
                "
                :text-variant="profile.darkMode ? 'white' : 'dark'"
                style="min-width: 30rem; max-width: 34rem;"
                class="overflow-hidden mb-4"
            >
                <workflowblurb
                    :showPublic="false"
                    :workflow="workflow"
                    v-on:flowSelected="workflowSelected"
                ></workflowblurb>
            </b-card>
        </b-card-group>
    </b-row>
</template>

<script>
import workflowblurb from '@/components/workflow-blurb.vue';
import router from '@/router';
import { mapGetters } from 'vuex';

export default {
    name: 'workflows',
    components: {
        workflowblurb
    },
    props: {
        workflows: {
            required: true,
            type: Array
        }
    },
    data: function() {
        return {
            login: false
        };
    },
    methods: {
        workflowSelected: function(workflow) {
            router.push({
                name: 'workflow',
                params: {
                    username: workflow['repo']['owner']['login'],
                    name: workflow['repo']['name']
                }
            });
        },
        sortWorkflows(left, right) {
            if (left.config.name < right.config.name) return -1;
            if (left.config.name > right.config.name) return 1;
            return 0;
        }
    },
    computed: mapGetters(['profile'])
};
</script>
<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
</style>
