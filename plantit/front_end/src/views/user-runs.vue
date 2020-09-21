<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
        >
            <b-row align-v="center">
                <b-col style="color: white" align-self="end">
                    <p class="text-dark">
                        Your flow runs are shown here.
                    </p>
                </b-col>
                <b-col align-self="end" md="auto">
                    <b-button
                        :disabled="loadingRuns"
                        variant="white"
                        @click="loadRuns"
                    >
                        <i class="fas fa-sync-alt fa-fw"></i>
                        Refresh
                    </b-button>
                </b-col>
            </b-row>
            <b-row align-h="center" v-if="loadingRuns">
                <b-col>
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="dark"
                    ></b-spinner>
                </b-col>
            </b-row>
            <br />
            <b-row align-h="center">
                <b-col>
                    <b-table
                        show-empty
                        sticky-header="true"
                        selectable
                        hover
                        small
                        responsive="sm"
                        sort-by.sync="date"
                        sort-desc.sync="true"
                        :items="runs"
                        :fields="fields"
                        borderless
                        select-mode="single"
                        :filter="filter"
                        @row-selected="onRunSelected"
                    >
                        <template v-slot:cell(state)="run">
                            <h4>
                                <b-badge
                                    :variant="
                                        run.item.state === 2
                                            ? 'danger'
                                            : run.item.state === 1
                                            ? 'success'
                                            : 'warning'
                                    "
                                    >{{ statusToString(run.item.state) }}
                                </b-badge>
                            </h4>
                        </template>
                    </b-table>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import Runs from '@/services/Runs.js';
import moment from 'moment';
import router from '../router';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'Runs',
    components: {},
    props: {
        perPage: {
            default: 50
        },
        filterable: {
            default: false
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
        onRunSelected: function(items) {
            router.push({
                name: 'run',
                params: {
                    id: items[0].id
                }
            });
        },
        togglePin(pk, item) {
            Runs.pin(pk, !item.pinned).then(success => {
                if (success) {
                    item.pinned = !item.pinned;
                }
            });
        },
        delete(pk) {
            this.$bvModal
                .msgBoxConfirm(`Delete this run?`, {
                    title: 'Delete Run',
                    centered: true
                })
                .then(value => {
                    if (value === true) {
                        Runs.delete(pk).then(value => {
                            if (value === true) {
                                this.runs = this.runs.filter(obj => {
                                    return obj.pk !== pk;
                                });
                            }
                        });
                    }
                });
        },
        async loadRuns() {
            this.loadingRuns = true;
            return axios
                .get('/apis/v1/runs/')
                .then(response => {
                    this.runs = response.data;
                    this.loadingRuns = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    },
    data() {
        return {
            fields: [
                {
                    key: 'id',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'state',
                    label: 'State'
                },
                {
                    key: 'created',
                    sortable: true,
                    formatter: value => {
                        return `${moment(value).fromNow()} (${moment(
                            value
                        ).format('MMMM Do YYYY, h:mm a')})`;
                    }
                },
                {
                    key: 'workflow_name',
                    label: 'Workflow',
                    sortable: true
                }
            ],
            loadingRuns: false,
            runs: []
        };
    },
    async mounted() {
        await this.loadRuns();
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
