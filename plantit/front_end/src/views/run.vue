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
        <b-container class="p-3 vl">
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
                                <h5 v-if="run.tags.length > 0">
                                    <b-badge
                                        v-for="tag in run.tags"
                                        v-bind:key="tag"
                                        class="mr-2"
                                        variant="warning"
                                        >{{ tag }}</b-badge
                                    >
                                </h5>
                                <b-row class="m-0 p-0">
                                    <b-col align-self="end" class="m-0 p-0">
                                        <h4
                                            :class="
                                                darkMode
                                                    ? 'theme-dark'
                                                    : 'theme-light'
                                            "
                                        >
                                            Run
                                            <b-badge
                                                class="mr-2"
                                                variant="secondary"
                                                >{{ run.id }}</b-badge
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
                                                :variant="
                                                    darkMode ? 'light' : 'dark'
                                                "
                                                class="mr-0"
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
                                        Container Logs
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
                                            class="mt-3"
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
                                                Download
                                            </b-button>
                                        </b-col>
                                    </b-row>
                                </b-card-body>
                            </b-card>
                            <b-card
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
                                        Output Files
                                    </h5></b-card-header
                                >
                                <b-card-body
                                    v-if="
                                        outputFiles.length > 0 ||
                                            loadingOutputFiles
                                    "
                                    class="mt-0 pt-0"
                                >
                                    <b-row
                                        class="pl-1 pr-1 pb-1"
                                        align-h="center"
                                        v-if="loadingOutputFiles"
                                    >
                                        <b-spinner
                                            type="grow"
                                            label="Loading..."
                                            variant="warning"
                                        ></b-spinner>
                                    </b-row>
                                    <b-row
                                        v-for="file in outputFiles"
                                        v-bind:key="file"
                                        class="pl-1 pr-1 pb-1"
                                        style="border-top: 1px solid rgba(211, 211, 211, .5);"
                                    >
                                        <b-col
                                            md="auto"
                                            v-if="
                                                file.name
                                                    .toLowerCase()
                                                    .endsWith('txt') ||
                                                    file.name
                                                        .toLowerCase()
                                                        .endsWith('log')
                                            "
                                            align-self="end"
                                        >
                                            <i class="fas fa-file-alt"></i>
                                        </b-col>
                                        <b-col
                                            md="auto"
                                            v-else-if="
                                                file.name
                                                    .toLowerCase()
                                                    .endsWith('csv')
                                            "
                                            align-self="end"
                                        >
                                            <i class="fas fa-file-csv"></i>
                                        </b-col>
                                        <b-col
                                            md="auto"
                                            v-else-if="
                                                file.name
                                                    .toLowerCase()
                                                    .endsWith('xlsx')
                                            "
                                            align-self="end"
                                        >
                                            <i class="fas fa-file-excel"></i>
                                        </b-col>
                                        <b-col
                                            md="auto"
                                            v-else-if="
                                                file.name
                                                    .toLowerCase()
                                                    .endsWith('pdf')
                                            "
                                            align-self="end"
                                        >
                                            <i class="fas fa-file-pdf"></i>
                                        </b-col>
                                        <b-col
                                            md="auto"
                                            v-if="
                                                file.name
                                                    .toLowerCase()
                                                    .includes('png') ||
                                                    file.name
                                                        .toLowerCase()
                                                        .includes('jpg') ||
                                                    file.name
                                                        .toLowerCase()
                                                        .includes('jpeg')
                                            "
                                            align-self="end"
                                        >
                                            <b-img
                                                right
                                                fluid
                                                :src="thumbnailUrl(file.name)"
                                                :alt="
                                                    require('@/assets/loading_spinner.gif')
                                                "
                                                rounded
                                            ></b-img>
                                        </b-col>
                                        <b-col
                                            align-self="end"
                                            class="text-left"
                                            style="white-space: pre-line;"
                                        >
                                            {{ file.name }}
                                        </b-col>
                                        <b-col
                                            align-self="end"
                                            v-if="
                                                (run.status === 1 ||
                                                    run.status === 2) &&
                                                    !file.exists
                                            "
                                        >
                                            <i
                                                class="far fa-times-circle fa-fw text-danger"
                                            ></i>
                                        </b-col>
                                        <b-col
                                            align-self="end"
                                            v-else-if="!file.exists"
                                        >
                                            <b-spinner
                                                small
                                                variant="warning"
                                            ></b-spinner>
                                        </b-col>
                                        <b-col md="auto" align-self="end">
                                            <b-button
                                                :disabled="!file.exists"
                                                :variant="
                                                    darkMode
                                                        ? 'outline-light'
                                                        : 'outline-dark'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                :title="'Download ' + file.name"
                                                @click="downloadFile(file.name)"
                                            >
                                                <i class="fas fa-download"></i>
                                                Download
                                            </b-button>
                                        </b-col>
                                    </b-row>
                                    <br />
                                    <b-row class="pl-1 pr-1 pb-1">
                                        <b-col
                                            class="text-right"
                                            align-self="end"
                                            ><b-button
                                                :variant="
                                                    darkMode
                                                        ? 'outline-light'
                                                        : 'outline-dark'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                title="Download zip file"
                                                @click="downloadZip"
                                            >
                                                <i
                                                    class="fas fa-file-archive fa-fw"
                                                ></i>
                                                Download All
                                            </b-button></b-col
                                        >
                                    </b-row>
                                </b-card-body>
                                <b-card-body
                                    v-else-if="flow.config.output"
                                    class="mt-0 pt-0"
                                >
                                    <b-row
                                        align-h="center"
                                        align-v="center"
                                        class="mt-2"
                                    >
                                        <b-col>
                                            <i
                                                class="fas fa-exclamation-triangle text-danger fa-fw"
                                            ></i>
                                            Output files expected but not found
                                        </b-col>
                                    </b-row>
                                    <b-row align-h="center" align-v="center">
                                        <b-col>
                                            <b
                                                ><code
                                                    >{{
                                                        flow.config.output.path
                                                            ? flow.config.output
                                                                  .path + '/'
                                                            : ''
                                                    }}{{
                                                        flow.config.output
                                                            .include
                                                            ? (flow.config
                                                                  .output
                                                                  .exclude
                                                                  ? '+ '
                                                                  : '') +
                                                              (flow.config
                                                                  .output
                                                                  .include
                                                                  .patterns
                                                                  ? '*.' +
                                                                    flow.config.output.include.patterns.join(
                                                                        ', *.'
                                                                    ) +
                                                                    ', '
                                                                  : []) +
                                                              (flow.config
                                                                  .output
                                                                  .include.names
                                                                  ? flow.config.output.include.names.join(
                                                                        ', '
                                                                    )
                                                                  : [])
                                                            : ''
                                                    }}{{
                                                        flow.config.output
                                                            .exclude
                                                            ? ' - ' +
                                                              (flow.config
                                                                  .output
                                                                  .exclude
                                                                  .patterns
                                                                  ? '*.' +
                                                                    flow.config.output.exclude.patterns.join(
                                                                        ', *.'
                                                                    ) +
                                                                    ', '
                                                                  : []) +
                                                              (flow.config
                                                                  .output
                                                                  .exclude.names
                                                                  ? flow.config.output.exclude.names.join(
                                                                        ', '
                                                                    )
                                                                  : [])
                                                            : ''
                                                    }}
                                                </code></b
                                            >
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
            loadingOutputFiles: false,
            runNotFound: false,
            run: null,
            logs: null,
            logsExpanded: false,
            logsText: '',
            outputFiles: [],
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
                    this.reloadOutputFiles();
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
        thumbnailUrl(file) {
            return `/apis/v1/runs/${this.$router.currentRoute.params.id}/thumbnail/${file}/`;
        },
        downloadZip() {},
        downloadFile(file) {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/output/${file}/`,
                    { responseType: 'blob' }
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
                    link.setAttribute('download', file);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
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
        reloadOutputFiles() {
            this.loadingOutputFiles = true;
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/outputs/`
                )
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }
                    this.outputFiles = response.data.outputs;
                    //var promises = [];
                    //for (let i = 0; i < this.outputFiles.length; i++) {
                    //    let name = response.data.outputs[i]['name'];
                    //    if (
                    //        name.toLowerCase().includes('png') ||
                    //        name.toLowerCase().includes('jpg') ||
                    //        name.toLowerCase().includes('jpeg')
                    //    )
                    //        promises.push(this.getThumbnail(name));
                    //}
                    //Promise.all([...promises]);
                    this.loadingOutputFiles = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.loadingOutputFiles = false;
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
