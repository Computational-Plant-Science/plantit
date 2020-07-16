<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <div v-if="runNotFound">
            <b-row align-content="center">
                <b-col>
                    <h5 class="text-center">
                        This page does not exist.
                    </h5>
                </b-col>
            </b-row>
        </div>
        <div v-if="!runNotFound">
            <b-row>
                <b-col>
                    <b-card
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="white"
                        footer-border-variant="white"
                        header-border-variant="dark"
                        class="overflow-hidden"
                    >
                        <b-row align-h="center" v-if="loadingRun">
                            <b-spinner
                                type="grow"
                                label="Loading..."
                                variant="dark"
                            ></b-spinner>
                        </b-row>
                        <RunBlurb
                            v-else
                            :workflow="workflow"
                            :run="run"
                            :selectable="false"
                        ></RunBlurb>
                    </b-card>
                </b-col>
            </b-row>
            <br />
            <b-row>
                <b-col>
                    <b-card
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="white"
                        footer-border-variant="white"
                        header-border-variant="white"
                    >
                        <template slot="header">
                            <b-row>
                                <b-col md="auto" align-self="center" class="mr-0">
                                    <h2>Logs</h2>
                                </b-col>
                                <b-col md="auto" class="m-0">
                                    <b-button
                                        variant="outline-dark"
                                        v-b-tooltip.hover
                                        title="Refresh"
                                        @click="reloadRun(true)"
                                    >
                                        <i class="fas fa-redo"></i>
                                    </b-button>
                                </b-col><b-col md="auto" class="ml-0">
                                    <b-alert
                                        class="m-0 pt-2 pb-2"
                                        :show="reloadAlertDismissCountdown"
                                        variant="success"
                                        @dismissed="
                                            reloadAlertDismissCountdown = 0
                                        "
                                        @dismiss-count-down="countDownChanged"
                                    >
                                        Logs refreshed.
                                    </b-alert>
                                </b-col>
                            </b-row>
                        </template>
                        <b-row>
                            <b-col>
                                <b-table
                                    borderless
                                    responsive="sm"
                                    :items="logs ? logs : []"
                                    :fields="status_table.fields"
                                    :sort-by.sync="status_table.sortBy"
                                >
                                    <template v-slot:cell(location)="status">
                                        <h4>
                                            <b-badge
                                                v-if="
                                                    status.item.location ===
                                                        'PlantIT'
                                                "
                                                variant="dark"
                                                class="text-success"
                                                >{{
                                                    status.item.location
                                                }}</b-badge
                                            >
                                            <b-badge
                                                v-else
                                                variant="secondary"
                                                class="text-white"
                                                >{{
                                                    status.item.location
                                                }}</b-badge
                                            >
                                        </h4>
                                    </template>
                                    <template v-slot:cell(state)="status">
                                        <h4>
                                            <b-badge
                                                :variant="
                                                    status.item.state === 2
                                                        ? 'danger'
                                                        : 'success'
                                                "
                                                >{{ statusToString(status.item.state) }}
                                            </b-badge>
                                        </h4>
                                    </template>
                                    <span
                                        slot="description"
                                        slot-scope="data"
                                        v-html="data.value"
                                        class="align-left"
                                    ></span>
                                </b-table>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-col>
            </b-row>
        </div>
    </div>
</template>

<script>
import RunBlurb from '../components/RunBlurb';
import Workflows from '@/services/apiV1/WorkflowManager';
import Users from '@/services/apiV1/UserManager';
import Runs from '@/services/apiV1/RunManager.js';
import moment from 'moment';

export default {
    name: 'Run',
    components: {
        RunBlurb
    },
    data() {
        return {
            reloadAlertDismissSeconds: 2,
            reloadAlertDismissCountdown: 0,
            showReloadAlert: false,
            user: null,
            workflow: null,
            loadingRun: true,
            runNotFound: false,
            run: null,
            logs: null,
            status_table: {
                sortBy: 'date',
                sortDesc: true,
                fields: [
                    {
                        key: 'state',
                        label: 'State',
                        formatter: value => {
                            switch (value) {
                                case 1:
                                    return 'Completed';
                                case 2:
                                    return 'Failed';
                                case 3:
                                    return 'Running';
                                case 4:
                                    return 'Created';
                            }
                        }
                    },
                    {
                        key: 'location',
                        label: 'From'
                    },
                    {
                        key: 'date',
                        label: 'Timestamp',
                        sortable: true,
                        formatter: value => {
                            return `${moment(value).fromNow()} (${moment(
                                value
                            ).format('MMMM Do YYYY, h:mm a')})`;
                        }
                    },
                    {
                        key: 'description',
                        formatter: value => {
                            return value.replace(/(?:\r\n|\r|\n)/g, '<br>');
                        },
                        tdClass: 'table-td'
                    }
                ]
            }
        };
    },
    methods: {
        reloadRun(toast) {
            this.loadingRun = true;
            Runs.getRun(this.$router.currentRoute.params.id).then(run => {
                if (run.response && run.response.status === 404) {
                    this.runNotFound = true;
                } else {
                    this.runNotFound = false;
                    this.run = run;
                }
                this.reloadLogs(toast);
                Users.getCurrentUser().then(user => {
                    this.user = user;
                    Workflows.get(
                        this.run.workflow_owner,
                        this.run.workflow_name
                    ).then(workflow => {
                        this.workflow = workflow;
                        this.loadingRun = false;
                    });
                });
            });
        },
        reloadLogs(toast) {
            Runs.getStatus(this.$router.currentRoute.params.id).then(logs => {
                if (logs.response && logs.response.status === 404) {
                    return;
                }
                this.logs = logs;
                if (toast) this.showAlert();
            });
        },
        countDownChanged(dismissCountDown) {
            this.reloadAlertDismissCountdown = dismissCountDown;
        },
        showAlert() {
            this.reloadAlertDismissCountdown = this.reloadAlertDismissSeconds;
        },
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
        }
    },
    mounted: function() {
        this.reloadRun(false);
    },
    computed: {
        runStatus() {
            if (this.run.runstatus_set.length > 0) {
                return this.run.runstatus_set[0].state;
            } else {
                return 0;
            }
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY HH:mm');
        },
        resultsLink() {
            return Runs.resultsLink(this.pk);
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button

.red
    color: $red

.table-td
    text-align: left


#error-log > thead
    display: none !important

#error-count
    padding-top: 10px
    float: right
</style>
