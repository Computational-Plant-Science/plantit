<template>
    <b-row align-v="center" align-h="center" v-if="loading">
        <b-col align-self="end" class="text-center">
            <b-spinner
                type="grow"
                label="Loading..."
                variant="warning"
            ></b-spinner>
        </b-col>
    </b-row>
    <b-row align-h="center" v-else>
        <b-col
            :class="darkMode ? 'text-light' : 'text-dark'"
            v-if="flows.length === 0 && !loading"
            >No flows to show!</b-col
        >
        <b-card-group deck columns class="justify-content-center">
            <b-card
                v-for="flow in flows"
                :key="flow.repo.name"
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
                    :flow="flow"
                    v-on:flowSelected="flowSelected"
                ></blurb>
            </b-card>
        </b-card-group>
    </b-row>
</template>

<script>
import axios from 'axios';
import blurb from '@/components/flow-blurb.vue';
import router from '@/router';
import { mapGetters } from 'vuex';

export default {
    name: 'flows',
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
            flows: [],
            login: false,
            loading: true
        };
    },
    mounted: function() {
        this.loadFlows();
    },
    methods: {
        loadFlows() {
            let url = (this.githubUser !== undefined && this.githubUser !== null && this.githubUser !== '') ? `/apis/v1/flows/${this.githubUser}/` : '/apis/v1/flows/list_all/'
            axios
                .get(url)
                .then(response => {
                    this.flows = response.data.flows
                    this.loading = false;
                })
                .catch(error => {
                    this.loading = false;
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        sortFlows(l, r) {
            if (l.config.name < r.config.name) return -1;
            if (l.config.name > r.config.name) return 1;
            return 0;
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
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn',
        'darkMode'
    ])
};
</script>
<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
</style>
