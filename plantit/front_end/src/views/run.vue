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
        <b-container class="p-3 vl" fluid>
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
                <div
                    v-if="
                        flow.config.output &&
                            (run.state === 2 || run.state === 1)
                    "
                >
                    <b-row>
                        <b-col md="auto" align-self="end" class="mr-0">
                            <h4 :class="darkMode ? 'text-light' : 'text-dark'">
                                Data
                            </h4>
                        </b-col>
                    </b-row>
                    <hr :class="darkMode ? 'theme-secondary' : 'theme-light'" />
                    <b-row>
                        <b-col>
                            <datatree
                                :upload="false"
                                :download="true"
                                :node="userData"
                            ></datatree></b-col
                    ></b-row>
                </div>
                <br />
                <b-row>
                    <b-col md="auto" align-self="end" class="mr-0">
                        <h4 :class="darkMode ? 'text-light' : 'text-dark'">
                            Logs
                        </h4>
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
                        {{ logsText }}
                    </b-col>
                </b-row>
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
                                <h5>
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
                                </h5>
                            </template>
                            <template v-slot:cell(state)="status">
                                <h5>
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
                                </h5>
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
            </div>
        </b-container>
    </div>
</template>
<script>
import RunBlurb from '../components/run-blurb';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import datatree from '@/components/data-tree.vue';
import * as Sentry from '@sentry/browser';

export default {
    name: 'run',
    components: {
        RunBlurb,
        datatree
    },
    data() {
        return {
            userData: null,
            reloadAlertDismissSeconds: 2,
            reloadAlertDismissCountdown: 0,
            showReloadAlert: false,
            flow: null,
            loadingRun: true,
            runNotFound: false,
            run: null,
            logs: null,
            logsText: '',
            status_table: {
                sortBy: 'date',
                sortDesc: true,
                fields: [
                    {
                        key: 'state',
                        label: 'Status',
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
                        label: 'When',
                        sortable: true,
                        formatter: value => {
                            // return `${moment(value).fromNow()} (${moment(
                            //     value
                            // ).format('MMMM Do YYYY, h:mm a')})`;

                            return `${moment(value).fromNow()}`;
                        }
                    },
                    {
                        key: 'description',
                        label: 'Message',
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
                    this.reloadLogsText(toast);
                    // this.reloadLogs(toast);
                    this.loadFlow(
                        response.data.flow_owner,
                        response.data.flow_name
                    );
                    axios
                        .get(
                            `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/${this.currentUserDjangoProfile.username}/`,
                            {
                                headers: {
                                    Authorization:
                                        'Bearer ' +
                                        this.currentUserDjangoProfile.profile
                                            .cyverse_token
                                }
                            }
                        )
                        .then(response => {
                            this.userData = response.data;
                        })
                        .catch(error => {
                            Sentry.captureException(error);
                            throw error;
                        });
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
        reloadLogsText(toast) {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/logs_text/`
                )
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }
                    this.logsText = response.data;
                    if (toast) this.showAlert();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
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
    async mounted() {
        await this.reloadRun(false);
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
