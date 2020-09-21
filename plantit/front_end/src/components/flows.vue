<template>
    <b-row align-h="center">
      <b-col class="text-center" v-if="flows.length === 0">None to show.</b-col>
        <b-card-group columns class="justify-content-center">
            <b-card
                v-for="flow in flows"
                :key="flow.repository.name"
                bg-variant="white"
                footer-bg-variant="white"
                border-variant="default"
                footer-border-variant="white"
                style="min-width: 15rem; max-width: 40rem;"
                class="overflow-hidden mb-4"
            >
                <blurb
                    :showPublic="false"
                    :flow="flow"
                    selectable="Start"
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

export default {
    name: 'flows',
    components: {
        blurb
    },
    props: {
        githubUser: {
            required: true,
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
            login: false
        };
    },
    mounted: function() {
        this.loadFlows();
    },
    methods: {
        loadFlows() {
            axios
                .get(
                    `https://api.github.com/search/code?q=filename:plantit.yaml+user:${this.githubUser}`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken
                        }
                    }
                )
                .then(response => {
                    this.flows = response.data.items;
                })
                .catch(error => {
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
                    username: flow['repository']['owner']['login'],
                    name: flow['repository']['name']
                }
            });
        }
    }
};
</script>

<style scoped></style>
