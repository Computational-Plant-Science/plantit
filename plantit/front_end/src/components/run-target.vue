<template>
    <div>
        <b-row><b-col>Select a deployment target for this flow.</b-col></b-row>
        <br />
        <b-table
            :items="targets"
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
        </b-table>
        <b-row align-h="center" v-if="targetsLoading">
            <b-spinner
                type="grow"
                label="Loading..."
                variant="darkMode ? 'warning' : 'dark'"
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
                    key: 'max_walltime',
                    label: 'Max Walltime',
                    formatter: value => value + ' (minutes)'
                },
                {
                    key: 'max_mem',
                    label: 'Max Memory',
                    formatter: value => value + ' (gigabytes)'
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
