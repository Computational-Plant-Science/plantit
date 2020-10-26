<template>
    <div
        class="w-100 h-100 p-3"
        :style="
            darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <b-container class="p-3">
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
                        <b-row align-h="center" v-if="loadingRun">
                            <b-spinner
                                type="grow"
                                label="Loading..."
                                variant="dark"
                            ></b-spinner>
                        </b-row>
                        <RunBlurb v-else :flow="flow" :run="run"></RunBlurb>
                    </b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col md="auto" align-self="end" class="mr-0">
                        <h5 :class="darkMode ? 'text-light' : 'text-dark'">
                            Logs
                        </h5>
                    </b-col>
                    <b-col md="auto" class="m-0">
                        <b-button
                            :variant="
                                darkMode ? 'outline-light' : 'outline-dark'
                            "
                            v-b-tooltip.hover
                            title="Refresh Logs"
                            @click="reloadRun(true)"
                        >
                            <i class="fas fa-redo"></i>
                        </b-button> </b-col
                    ><b-col md="auto" class="ml-0">
                        <b-alert
                            class="m-0 pt-1 pb-1"
                            :show="reloadAlertDismissCountdown"
                            variant="success"
                            @dismissed="reloadAlertDismissCountdown = 0"
                            @dismiss-count-down="countDownChanged"
                        >
                            Logs refreshed.
                        </b-alert>
                    </b-col>
                </b-row>
                <hr :class="darkMode ? 'theme-secondary' : 'theme-light'" />
                <b-row>
                    <b-col>
                        <b-table
                            borderless
                            small
                            responsive="sm"
                            :items="logs ? logs : []"
                            :fields="status_table.fields"
                            :sort-by.sync="status_table.sortBy"
                            :table-variant="darkMode ? 'dark' : 'light'"
                        >
                            <template v-slot:cell(location)="status">
                                <h4>
                                    <b-badge
                                        v-if="
                                            status.item.location === 'PlantIT'
                                        "
                                        variant="dark"
                                        class="text-success"
                                        >{{ status.item.location }}</b-badge
                                    >
                                    <b-badge
                                        v-else
                                        variant="secondary"
                                        class="text-white"
                                        >{{ status.item.location }}</b-badge
                                    >
                                </h4>
                            </template>
                            <template v-slot:cell(state)="status">
                                <h4>
                                    <b-badge
                                        :variant="
                                            status.item.state === 2
                                                ? 'danger'
                                                : status.item.state === 1
                                                ? 'success'
                                                : 'warning'
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
                <b-row v-if="flow.config.to && (run.state === 2 || run.state === 1)">
                    <b-col md="auto" align-self="end" class="mr-0">
                        <h5 :class="darkMode ? 'text-light' : 'text-dark'">
                            Output
                        </h5>
                    </b-col>
                </b-row>
                <hr :class="darkMode ? 'theme-secondary' : 'theme-light'" />
            </div>
        </b-container>
    </div>
</template>
<script>
import RunBlurb from '../components/run-blurb';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'run',
    components: {
        RunBlurb
    },
    data() {
        return {
            reloadAlertDismissSeconds: 2,
            reloadAlertDismissCountdown: 0,
            showReloadAlert: false,
            flow: null,
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
            axios
                .get(`/apis/v1/runs/${this.$router.currentRoute.params.id}/`)
                .then(response => {
                    if (response && response.status === 404) {
                        this.runNotFound = true;
                    } else {
                        this.runNotFound = false;
                        this.run = response.data;
                    }
                    this.reloadLogs(toast);
                    this.loadFlow(
                        response.data.workflow_owner,
                        response.data.workflow_name
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        loadFlow(owner, name) {
            this.loadingRun = true;
            axios
                .get(`/apis/v1/flows/${owner}/${name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flow = response.data;
                    this.loadingRun = false;
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        reloadLogs(toast) {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/status/`
                )
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }
                    this.logs = response.data;
                    if (toast) this.showAlert();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
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
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserCyVerseProfile',
            'currentUserGitHubProfile',
            'loggedIn',
            'darkMode'
        ]),
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
        }
        // resultsLink() {
        //     return Runs.resultsLink(this.pk);
        // }
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
