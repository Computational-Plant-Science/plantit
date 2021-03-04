<template>
    <b-row align-v="center" align-h="center" v-if="loading">
        <b-col align-self="end" class="text-center">
            <b-spinner
                type="grow"
                label="Loading..."
                variant="secondary"
            ></b-spinner>
        </b-col>
    </b-row>
    <b-row align-h="center" v-else>
        <b-col
            :class="darkMode ? 'text-light' : 'text-dark'"
            v-if="workflows.length === 0 && !loading"
            >No workflows to show!</b-col
        >
        <b-card-group deck columns class="justify-content-center">
            <b-card
                v-for="workflow in workflows"
                :key="workflow.repo.name"
                :bg-variant="darkMode ? 'dark' : 'white'"
                :header-bg-variant="darkMode ? 'dark' : 'white'"
                border-variant="default"
                :header-border-variant="darkMode ? 'secondary' : 'default'"
                :text-variant="darkMode ? 'white' : 'dark'"
                style="min-width: 40rem; max-width: 40rem;"
                class="overflow-hidden mb-4"
            >
                <blurb
                    :showPublic="false"
                    :workflow="workflow"
                    v-on:flowSelected="workflowSelected"
                ></blurb>
            </b-card>
        </b-card-group>
    </b-row>
</template>

<script>
import blurb from '@/components/workflow-blurb.vue';
import router from '@/router';
import { mapGetters } from 'vuex';

export default {
    name: 'workflows',
    components: {
        blurb
    },
    props: {
        githubUser: {
            required: false,
            type: String
        },
        githubToken: {
            required: true,
            type: String
        }
    },
    data: function() {
        return {
            login: false,
            loading: true
        };
    },
    mounted: function() {
        this.loadWorkflows();
    },
    methods: {
        sortWorkflows(left, right) {
            if (left.config.name < right.config.name) return -1;
            if (left.config.name > right.config.name) return 1;
            return 0;
        },
        workflowSelected: function(workflow) {
            router.push({
                name: 'workflow',
                params: {
                    username: workflow['repo']['owner']['login'],
                    name: workflow['repo']['name']
                }
            });
        }
    },
    computed: mapGetters(['workflows', 'profile', 'loggedIn', 'darkMode'])
};
</script>
<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
</style>
