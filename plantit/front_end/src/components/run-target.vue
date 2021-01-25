<template>
    <div>
        <b :class="darkMode ? 'text-white' : 'text-dark'">
            Select a cluster or server to submit this run to.
        </b>
        <br />
        <b-table
            :items="targets.filter(target => !target.disabled)"
            :fields="fields"
            responsive="sm"
            borderless
            small
            selectable
            select-mode="single"
            @row-selected="rowSelected"
            sticky-header="true"
            caption-top
            :table-variant="darkMode ? 'dark' : 'white'"
        >
            <template v-slot:cell(name)="target">
                {{ target.item.name }}
            </template>
            <template v-slot:cell(host)="target">
                {{ target.item.host }}
            </template>
            <template v-slot:cell(host)="target">
                {{ target.item.max_cores }}
            </template>
            <template v-slot:cell(host)="target">
                {{ target.item.max_processes }}
            </template>
            <template v-slot:cell(host)="target">
                {{ target.item.max_mem }}
            </template>
            <template v-slot:cell(gpu)="target">
                <i
                    :class="target.item.gpu ? 'text-success' : 'text-danger'"
                    v-if="target.item.gpu"
                    class="far fa-check-circle"
                ></i>
                <i
                    :class="target.item.gpu ? 'text-success' : 'text-danger'"
                    v-else
                    class="far fa-times-circle"
                ></i>
            </template>
        </b-table>
        <b-row align-h="center" v-if="targetsLoading">
            <b-spinner
                type="grow"
                label="Loading..."
                variant="success"
            ></b-spinner>
        </b-row>
        <b-row
            align-h="center"
            class="text-center"
            v-if="!targetsLoading && targets.length === 0"
        >
            <b-col>
                None to show.
            </b-col>
        </b-row>
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
export default {
    name: 'run-target',
    props: {
        selected: {
            type: Object,
            required: false
        }
    },
    data: function() {
        return {
            fields: [
                {
                    key: 'name',
                    label: 'Name'
                },
                {
                    key: 'description',
                    label: 'Description'
                },
                {
                    key: 'max_cores',
                    label: 'Max Cores'
                },
                {
                    key: 'max_processes',
                    label: 'Max Processes'
                },
                {
                    key: 'max_mem',
                    label: 'Max Memory'
                },
                {
                    key: 'gpu',
                    label: 'GPU'
                }
            ],
            targets: [],
            targetsLoading: false
        };
    },
    mounted: function() {
        this.loadTargets();
    },
    methods: {
        loadTargets: function() {
            this.targetsLoading = true;
            return axios
                .get('/apis/v1/targets/')
                .then(response => {
                    this.targets = response.data;
                    this.targetsLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        rowSelected: function(items) {
            this.$emit('targetSelected', items[0]);
        }
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
            'loggedIn',
            'darkMode'
        ])
    }
};
</script>
<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: white
    padding: 24px

    img
        margin-top: 20px
        max-width: 140px
        max-height: 190px
</style>
