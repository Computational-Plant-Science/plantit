<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
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
                                variant="warning"
                            ></b-spinner>
                        </b-row>
                        <div v-else-if="flow.config">
                            <b-card
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :footer-bg-variant="darkMode ? 'dark' : 'white'"
                                border-variant="default"
                                :footer-border-variant="
                                    darkMode ? 'dark' : 'white'
                                "
                                style="min-height: 5rem;"
                                class="overflow-hidden mt-0"
                            >
                                <WorkflowBlurb
                                    :showPublic="false"
                                    :flow="flow"
                                    selectable="Restart"
                                ></WorkflowBlurb>
                                <br />
                                {{ run.id }}
                                <br />
                                <b-badge
                                    v-for="tag in run.tags"
                                    v-bind:key="tag"
                                    class="mr-1"
                                    variant="warning"
                                    >{{ tag }}</b-badge
                                >
                                <br />
                                <b-row class="m-0 p-0">
                                    <b-col align-self="end" class="m-0 p-0">
                                        <h4
                                            :class="
                                                darkMode
                                                    ? 'theme-dark'
                                                    : 'theme-light'
                                            "
                                        >
                                            <b-badge
                                                :variant="
                                                    run.state === 2
                                                        ? 'danger'
                                                        : run.state === 1
                                                        ? 'success'
                                                        : 'warning'
                                                "
                                                >{{ statusToString(run.state) }}
                                            </b-badge>
                                            <small> on </small>
                                            <b-badge
                                                variant="secondary"
                                                class="text-white mr-0"
                                                >{{ run.target }}</b-badge
                                            >
                                            <small>
                                                {{ updatedFormatted }}
                                            </small>
                                        </h4>
                                    </b-col>
                                    <b-col md="auto" class="ml-0">
                                        <b-alert
                                            class="m-0 pt-1 pb-1"
                                            :show="reloadAlertDismissCountdown"
                                            variant="success"
                                            @dismissed="
                                                reloadAlertDismissCountdown = 0
                                            "
                                            @dismiss-count-down="
                                                countDownChanged
                                            "
                                        >
                                            Logs refreshed.
                                        </b-alert>
                                    </b-col>
                                    <!--<b-col md="auto" class="mt-1">
                                        {{ run.description }} {{ updatedFormatted }}
                                    </b-col>-->
                                    <b-col
                                        md="auto"
                                        class="m-0"
                                        align-self="start"
                                    >
                                        <b-button
                                            :variant="
                                                darkMode
                                                    ? 'outline-light'
                                                    : 'outline-dark'
                                            "
                                            size="sm"
                                            v-b-tooltip.hover
                                            title="Refresh Logs"
                                            @click="reloadRun(true)"
                                        >
                                            <i class="fas fa-redo"></i>
                                        </b-button>
                                    </b-col>
                                    <b-col
                                        md="auto"
                                        class="m-0"
                                        align-self="start"
                                    >
                                        <b-button
                                            :variant="
                                                darkMode
                                                    ? 'outline-light'
                                                    : 'outline-dark'
                                            "
                                            size="sm"
                                            v-b-tooltip.hover
                                            :title="
                                                logsExpanded
                                                    ? 'Collapse Logs'
                                                    : 'Expand Logs'
                                            "
                                            @click="expandLogs"
                                        >
                                            <i
                                                v-if="logsExpanded"
                                                class="fas fa-caret-down"
                                            ></i>
                                            <i
                                                v-else
                                                class="fas fa-caret-up"
                                            ></i>
                                        </b-button>
                                    </b-col>
                                </b-row>
                                <div v-if="logsExpanded">
                                    <div
                                        v-for="log in logs.slice(1)"
                                        v-bind:key="log.updated"
                                    >
                                        <hr />
                                        <b-row>
                                            <b-col md="auto" align-self="end">
                                                <h5
                                                    :class="
                                                        darkMode
                                                            ? 'theme-dark'
                                                            : 'theme-light'
                                                    "
                                                >
                                                    <b-badge
                                                        class="mr-1"
                                                        :variant="
                                                            log.state === 2
                                                                ? 'danger'
                                                                : log.state ===
                                                                  1
                                                                ? 'success'
                                                                : 'warning'
                                                        "
                                                        >{{
                                                            statusToString(
                                                                log.state
                                                            )
                                                        }}
                                                    </b-badge>
                                                    <small>{{
                                                        formatDate(log.date)
                                                    }}</small>
                                                </h5>
                                                <small>
                                                    {{ log.description }}
                                                </small>
                                            </b-col>
                                        </b-row>
                                    </div>
                                </div>
                            </b-card>
                            <b-card
                                v-if="logsText !== ''"
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :footer-bg-variant="darkMode ? 'dark' : 'white'"
                                border-variant="default"
                                :footer-border-variant="
                                    darkMode ? 'dark' : 'white'
                                "
                                no-body
                            >
                                <b-card-header
                                    class="mt-1"
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    ><h5
                                        :class="
                                            darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        Container Output
                                    </h5></b-card-header
                                >
                                <b-card-body
                                    :class="
                                        darkMode
                                            ? 'theme-container-dark mt-0 pt-0'
                                            : 'theme-container-light mt-0 pt-0'
                                    "
                                >
                                    <b-row
                                        align-h="center"
                                        v-if="loadingContainerLogs"
                                    >
                                        <b-spinner
                                            type="grow"
                                            label="Loading..."
                                            variant="warning"
                                        ></b-spinner>
                                    </b-row>
                                    <b-row
                                        v-else-if="logsText !== ''"
                                        :class="
                                            darkMode
                                                ? 'theme-container-dark mt-0 pt-0'
                                                : 'theme-container-light mt-0 pt-0'
                                        "
                                    >
                                        <b-col
                                            class="pl-3 pr-3 pb-1"
                                            style="white-space: pre-line;"
                                        >
                                            {{ logsText }}
                                        </b-col>
                                    </b-row>
                                    <b-row>
                                        <!--<b-col align-self="end" class="mr-0">
                                    <h5
                                        :class="
                                            darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        Container Output
                                    </h5>
                                </b-col>-->
                                        <b-col></b-col>
                                        <b-col md="auto" align-self="middle">
                                            Showing last
                                            <b-dropdown
                                                class="m-1"
                                                :text="containerLogsPageSize"
                                                variant="warning"
                                                size="sm"
                                            >
                                                <b-dropdown-item
                                                    @click="
                                                        setContainerLogsPageSize(
                                                            10
                                                        )
                                                    "
                                                    >10</b-dropdown-item
                                                >
                                                <b-dropdown-item
                                                    @click="
                                                        setContainerLogsPageSize(
                                                            20
                                                        )
                                                    "
                                                    >20</b-dropdown-item
                                                >
                                                <b-dropdown-item
                                                    @click="
                                                        setContainerLogsPageSize(
                                                            50
                                                        )
                                                    "
                                                    >50</b-dropdown-item
                                                >
                                            </b-dropdown>
                                            lines
                                        </b-col>
                                        <b-col md="auto" align-self="middle">
                                            <b-button
                                                :variant="
                                                    darkMode
                                                        ? 'outline-light'
                                                        : 'outline-dark'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                title="Download Container Output"
                                                @click="downloadLogs"
                                            >
                                                <i class="fas fa-download"></i>
                                            </b-button>
                                        </b-col>
                                    </b-row>
                                </b-card-body>
                            </b-card>
                            <b-card
                                v-if="
                                    flow.config.output &&
                                        (run.state === 2 || run.state === 1)
                                "
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :footer-bg-variant="darkMode ? 'dark' : 'white'"
                                border-variant="default"
                                :footer-border-variant="
                                    darkMode ? 'dark' : 'white'
                                "
                                no-body
                            >
                                <b-card-header
                                    class="mt-1"
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    ><h5
                                        :class="
                                            darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        CyVerse Data Store
                                    </h5></b-card-header
                                >
                                <b-card-body>
                                    <b-row>
                                        <b-col>
                                            <datatree
                                                :upload="false"
                                                :download="true"
                                                :node="userData"
                                            ></datatree></b-col
                                    ></b-row>
                                </b-card-body>
                            </b-card>
                        </div>
                    </b-col>
                </b-row>
            </div>
        </b-container>
    </div>
</template>
<script>
import WorkflowBlurb from '@/components/flow-blurb.vue';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import datatree from '@/components/data-tree.vue';
import * as Sentry from '@sentry/browser';

export default {
    name: 'run',
    components: {
        WorkflowBlurb,
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
            loadingContainerLogs: false,
            runNotFound: false,
            run: null,
            logs: null,
            logsExpanded: false,
            logsText: '',
            containerLogsPageSize: 10,
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
        setContainerLogsPageSize(size) {
            this.containerLogsPageSize = size;
            this.reloadOutput(false);
        },
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
                    this.reloadOutput(toast);
                    this.reloadLogs(toast);
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
        downloadLogs() {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/logs/`
                )
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }

                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute(
                        'download',
                        `${this.$router.currentRoute.params.id}.logs`
                    );
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        reloadOutput(toast) {
            this.loadingContainerLogs = true;
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/logs_text/${this.containerLogsPageSize}/`
                )
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }
                    this.logsText = response.data;
                    this.loadingContainerLogs = false;
                    if (toast) this.showAlert();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.loadingContainerLogs = false;
                    return error;
                });
        },
        expandLogs() {
            this.logsExpanded = !this.logsExpanded;
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
        formatDate(date) {
            return `${moment(date).fromNow()}`;
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
        },
        updatedFormatted() {
            return `${moment(this.run.updated).fromNow()}`;
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
