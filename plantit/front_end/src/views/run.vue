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
                            <b-row class="m-1">
                                <!-- CREATING -->
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="logs[0].state === 1"
                                    class="text-center ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Creating
                                </b-col>
                                <b-col
                                    md="auto"
                                    v-else
                                    class="text-center ml-0 mr-0"
                                    align-self="end"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Created
                                </b-col>
                                <b-col
                                    align-self="end"
                                    class="text-center mb-2"
                                >
                                    <b-progress
                                        height="0.3rem"
                                        :value="1"
                                        :max="1"
                                        :variant="
                                            logs[0].state === 1
                                                ? 'warning'
                                                : 'success'
                                        "
                                        :animated="logs[0].state === 1"
                                    ></b-progress>
                                </b-col>
                                <!-- PULLING -->
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="
                                        logs[0].state === 1 && flow.config.input
                                    "
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Pull Inputs
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="logs[0].state === 2"
                                    class="text-center ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Pulling Inputs
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-else-if="anyStatuses(2)"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Pulled Inputs
                                </b-col>
                                <b-col
                                    v-if="anyStatuses(2)"
                                    align-self="end"
                                    class="text-center mb-2"
                                >
                                    <b-progress
                                        height="0.3rem"
                                        :value="1"
                                        :max="1"
                                        :variant="
                                            logs[0].state === 2
                                                ? 'warning'
                                                : 'success'
                                        "
                                        :animated="logs[0].state === 2"
                                    ></b-progress>
                                </b-col>
                                <!-- RUNNING -->
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="
                                        logs[0].state === 2 ||
                                            (logs[0].state === 1 &&
                                                !flow.config.input)
                                    "
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Run container(s)
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="logs[0].state === 3"
                                    class="text-center ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Running container(s)
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-else-if="anyStatuses(3)"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Ran container(s)
                                </b-col>
                                <b-col
                                    v-if="anyStatuses(3)"
                                    align-self="end"
                                    class="text-center mb-2"
                                >
                                    <b-progress
                                        height="0.3rem"
                                        :value="1"
                                        :max="1"
                                        :variant="
                                            logs[0].state === 3
                                                ? 'warning'
                                                : 'success'
                                        "
                                        :animated="logs[0].state === 3"
                                    ></b-progress>
                                </b-col>
                                <!-- ZIPPING -->
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="
                                        logs[0].state === 3 &&
                                            flow.config.output
                                    "
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Zip Outputs
                                </b-col>
                                <b-col
                                    md="auto"
                                    v-if="logs[0].state === 4"
                                    class="text-center ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Zipping Outputs
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-else-if="anyStatuses(4)"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Zipped Outputs
                                </b-col>
                                <b-col
                                    v-if="anyStatuses(4)"
                                    align-self="end"
                                    class="text-center mb-2"
                                >
                                    <b-progress
                                        height="0.3rem"
                                        :value="1"
                                        :max="1"
                                        :variant="
                                            logs[0].state === 3
                                                ? 'warning'
                                                : 'success'
                                        "
                                        :animated="logs[0].state === 3"
                                    ></b-progress>
                                </b-col>
                                <!-- PUSHING -->
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="
                                        logs[0].state === 4 &&
                                            flow.config.output
                                    "
                                    class="text-center  ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Push Outputs
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="logs[0].state === 5"
                                    class="text-center  ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Pushing Outputs
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-else-if="anyStatuses(5)"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Pushed Outputs
                                </b-col>
                                <b-col
                                    v-if="anyStatuses(5)"
                                    align-self="end"
                                    class="text-center mb-2"
                                >
                                    <b-progress
                                        height="0.3rem"
                                        :value="1"
                                        :max="1"
                                        :variant="
                                            logs[0].state === 4
                                                ? 'warning'
                                                : 'success'
                                        "
                                        :animated="logs[0].state === 4"
                                    ></b-progress>
                                </b-col>
                                <!-- COMPLETION/FAILURE -->
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="anyStatuses(0)"
                                    class="text-center"
                                >
                                    <i
                                        class="far fa-times-circle text-danger"
                                    ></i>
                                    Failed
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-else-if="
                                        (logs[0].state === 3 &&
                                            !flow.config.output) ||
                                            (flow.config.output &&
                                                logs[0].state === 5)
                                    "
                                    class="text-center  ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Complete
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-else-if="logs[0].state === 6"
                                    class="text-center"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Complete
                                </b-col>
                            </b-row>
                            <br />
                            <b-row>
                                <b-col>
                                    <b-card
                                        :bg-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        :footer-bg-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        border-variant="default"
                                        :footer-border-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        style="min-height: 5rem;"
                                        class="overflow-hidden mt-0"
                                        no-body
                                    >
                                        <b-card-body
                                            class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
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
                                                <b-col
                                                    align-self="end"
                                                    class="m-0 p-0"
                                                >
                                                    <h5
                                                        :class="
                                                            darkMode
                                                                ? 'theme-dark'
                                                                : 'theme-light'
                                                        "
                                                    >
                                                        <b-badge
                                                            class="mr-2"
                                                            variant="secondary"
                                                            >{{
                                                                run.id
                                                            }}</b-badge
                                                        >
                                                        <b-badge
                                                            :variant="
                                                                logs[0]
                                                                    .state === 0
                                                                    ? 'danger'
                                                                    : logs[0]
                                                                          .state ===
                                                                      6
                                                                    ? 'success'
                                                                    : 'warning'
                                                            "
                                                            >{{
                                                                statusToString(
                                                                    anyStatuses(
                                                                        0
                                                                    )
                                                                        ? 0
                                                                        : logs[0]
                                                                              .state
                                                                )
                                                            }}
                                                        </b-badge>
                                                        <small> on </small>
                                                        <b-badge
                                                            variant="secondary"
                                                            class="mr-0"
                                                            >{{
                                                                run.target
                                                            }}</b-badge
                                                        >
                                                        <small>
                                                            {{
                                                                updatedFormatted
                                                            }}
                                                        </small>
                                                    </h5>
                                                    <small
                                                        v-if="
                                                            walltimeRemaining !==
                                                                null
                                                        "
                                                        >{{
                                                            this.anyStatuses(
                                                                0
                                                            ) ||
                                                            this.anyStatuses(6)
                                                                ? 'Ran'
                                                                : 'Running'
                                                        }}
                                                        for
                                                        {{
                                                            walltimeElapsed.humanize()
                                                        }}
                                                        <span
                                                            v-if="
                                                                !(
                                                                    this.anyStatuses(
                                                                        0
                                                                    ) ||
                                                                    this.anyStatuses(
                                                                        6
                                                                    )
                                                                )
                                                            "
                                                            >({{
                                                                walltimeRemaining.humanize()
                                                            }}
                                                            remaining)</span
                                                        ></small
                                                    >
                                                </b-col>
                                                <b-col md="auto" class="ml-0">
                                                    <b-alert
                                                        class="m-0 pt-1 pb-1"
                                                        :show="
                                                            reloadAlertDismissCountdown
                                                        "
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
                                                        title="Refresh"
                                                        @click="reloadRun(true)"
                                                    >
                                                        <i
                                                            class="fas fa-redo"
                                                        ></i>
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
                                                                ? 'Collapse Status Logs'
                                                                : 'Expand Status Logs'
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
                                                <hr />
                                                <div
                                                    v-for="log in logs"
                                                    v-bind:key="log.updated"
                                                >
                                                    <b-row>
                                                        <b-col
                                                            md="auto"
                                                            align-self="end"
                                                        >
                                                            <p
                                                                :class="
                                                                    darkMode
                                                                        ? 'theme-dark'
                                                                        : 'theme-light'
                                                                "
                                                            >
                                                                <b-badge
                                                                    class="mr-1"
                                                                    :variant="
                                                                        log.state ===
                                                                        0
                                                                            ? 'danger'
                                                                            : log.state ===
                                                                              6
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
                                                                    formatDate(
                                                                        log.date
                                                                    )
                                                                }}</small>
                                                                <br />
                                                                <small>
                                                                    {{
                                                                        log.description
                                                                    }}
                                                                </small>
                                                            </p>
                                                        </b-col>
                                                    </b-row>
                                                </div>
                                            </div>
                                        </b-card-body>
                                    </b-card>
                                    <b-card
                                        v-if="logsText !== ''"
                                        :bg-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        :footer-bg-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        border-variant="default"
                                        :footer-border-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        no-body
                                    >
                                        <b-card-header
                                            class="mr-2 mt-2 mb-2 ml-2 p-1 pt-2"
                                            :header-bg-variant="
                                                darkMode ? 'dark' : 'white'
                                            "
                                        >
                                            <b-row
                                                ><b-col>
                                                    <h4
                                                        :class="
                                                            darkMode
                                                                ? 'text-white'
                                                                : 'text-dark'
                                                        "
                                                    >
                                                        Container Logs
                                                    </h4>
                                                </b-col>
                                                <b-col md="auto">
                                                    <b-button
                                                        :variant="
                                                            darkMode
                                                                ? 'outline-light'
                                                                : 'outline-dark'
                                                        "
                                                        size="sm"
                                                        v-b-tooltip.hover
                                                        :title="
                                                            containerLogsExpanded
                                                                ? 'Collapse Container Logs'
                                                                : 'Expand Container Logs'
                                                        "
                                                        @click="
                                                            expandContainerLogs
                                                        "
                                                    >
                                                        <i
                                                            v-if="
                                                                containerLogsExpanded
                                                            "
                                                            class="fas fa-caret-down"
                                                        ></i>
                                                        <i
                                                            v-else
                                                            class="fas fa-caret-up"
                                                        ></i>
                                                    </b-button> </b-col
                                            ></b-row>
                                        </b-card-header>
                                        <b-card-body
                                            v-if="containerLogsExpanded"
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
                                                <b-col align-self="end">
                                                    <b-button
                                                        :variant="
                                                            darkMode
                                                                ? 'outline-light'
                                                                : 'outline-dark'
                                                        "
                                                        size="sm"
                                                        v-b-tooltip.hover
                                                        title="Download Container Log File"
                                                        @click="downloadLogs"
                                                    >
                                                        <i
                                                            class="fas fa-download"
                                                        ></i>
                                                        Download
                                                    </b-button>
                                                </b-col>
                                                <b-col
                                                    md="auto"
                                                    align-self="end"
                                                >
                                                    Showing last
                                                    <b-dropdown
                                                        class="m-1"
                                                        :text="
                                                            containerLogsPageSize
                                                        "
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
                                            </b-row>
                                        </b-card-body>
                                    </b-card>
                                    <b-card
                                        :bg-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        :footer-bg-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        border-variant="default"
                                        :footer-border-variant="
                                            darkMode ? 'dark' : 'white'
                                        "
                                        no-body
                                    >
                                        <b-card-header
                                            class="mr-2 mt-2 mb-2 ml-2 p-1 pt-2"
                                            :header-bg-variant="
                                                darkMode ? 'dark' : 'white'
                                            "
                                        >
                                            <b-row
                                                ><b-col>
                                                    <h4
                                                        :class="
                                                            darkMode
                                                                ? 'text-white'
                                                                : 'text-dark'
                                                        "
                                                    >
                                                        Output Files
                                                    </h4>
                                                </b-col>
                                                <b-col md="auto">
                                                    <b-button
                                                        :variant="
                                                            darkMode
                                                                ? 'outline-light'
                                                                : 'outline-dark'
                                                        "
                                                        size="sm"
                                                        v-b-tooltip.hover
                                                        :title="
                                                            outputFilesExpanded
                                                                ? 'Collapse Output Files'
                                                                : 'Expand Output Files'
                                                        "
                                                        @click="
                                                            expandOutputFiles
                                                        "
                                                    >
                                                        <i
                                                            v-if="
                                                                outputFilesExpanded
                                                            "
                                                            class="fas fa-caret-down"
                                                        ></i>
                                                        <i
                                                            v-else
                                                            class="fas fa-caret-up"
                                                        ></i>
                                                    </b-button> </b-col
                                            ></b-row>
                                        </b-card-header>
                                        <b-card-body
                                            v-if="
                                                outputFilesExpanded &&
                                                    (outputFiles.length > 0 ||
                                                        loadingOutputFiles)
                                            "
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
                                            <b-row>
                                                <b-col>
                                                    <b-pagination
                                                        v-model="outputFilePage"
                                                        pills
                                                        :total-rows="
                                                            outputFiles.length
                                                        "
                                                        :per-page="
                                                            outputPageSize
                                                        "
                                                        aria-controls="outputList"
                                                        variant
                                                    >
                                                        <template #first-text
                                                            ><span
                                                                >First</span
                                                            ></template
                                                        >
                                                        <template #prev-text
                                                            ><span
                                                                >Prev</span
                                                            ></template
                                                        >
                                                        <template #next-text
                                                            ><span
                                                                >Next</span
                                                            ></template
                                                        >
                                                        <template #last-text
                                                            ><span
                                                                >Last</span
                                                            ></template
                                                        >
                                                    </b-pagination>
                                                </b-col>
                                                <b-col
                                                    md="auto"
                                                    align-self="middle"
                                                >
                                                    Showing
                                                    <b-dropdown
                                                        class="m-1"
                                                        :text="outputPageSize"
                                                        variant="warning"
                                                        size="sm"
                                                    >
                                                        <b-dropdown-item
                                                            @click="
                                                                setOutputPageSize(
                                                                    10
                                                                )
                                                            "
                                                            >10</b-dropdown-item
                                                        >
                                                        <b-dropdown-item
                                                            @click="
                                                                setOutputPageSize(
                                                                    20
                                                                )
                                                            "
                                                            >20</b-dropdown-item
                                                        >
                                                        <b-dropdown-item
                                                            @click="
                                                                setOutputPageSize(
                                                                    50
                                                                )
                                                            "
                                                            >50</b-dropdown-item
                                                        >
                                                    </b-dropdown>
                                                    files
                                                </b-col>
                                            </b-row>
                                            <b-row
                                                id="outputList"
                                                v-for="file in outputList()"
                                                v-bind:key="file"
                                                class="p-1"
                                                style="border-top: 1px solid rgba(211, 211, 211, .5);"
                                            >
                                                <b-col
                                                    align-self="end"
                                                    md="auto"
                                                    v-if="
                                                        file.name
                                                            .toLowerCase()
                                                            .endsWith('txt') ||
                                                            file.name
                                                                .toLowerCase()
                                                                .endsWith('log')
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-file-alt fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    md="auto"
                                                    v-else-if="
                                                        file.name
                                                            .toLowerCase()
                                                            .endsWith('csv')
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-file-csv fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    md="auto"
                                                    v-else-if="
                                                        file.name
                                                            .toLowerCase()
                                                            .endsWith('zip')
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-file-archive fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    md="auto"
                                                    v-else-if="
                                                        file.name
                                                            .toLowerCase()
                                                            .endsWith('xlsx')
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-file-excel fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    md="auto"
                                                    v-else-if="
                                                        file.name
                                                            .toLowerCase()
                                                            .endsWith('pdf')
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-file-pdf fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    md="auto"
                                                    v-else-if="
                                                        file.name
                                                            .toLowerCase()
                                                            .includes('png') ||
                                                            file.name
                                                                .toLowerCase()
                                                                .includes(
                                                                    'jpg'
                                                                ) ||
                                                            file.name
                                                                .toLowerCase()
                                                                .includes(
                                                                    'jpeg'
                                                                )
                                                    "
                                                >
                                                    <i
                                                        class="far fa-file-image fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    md="auto"
                                                    v-else
                                                >
                                                    <i
                                                        class="fas fa-file fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    class="text-left"
                                                    style="position: relative; top: -5px; left: -40px"
                                                >
                                                    <b-spinner
                                                        class="m-0 p-0"
                                                        v-if="
                                                            !file.exists &&
                                                                logs[0]
                                                                    .state !==
                                                                    6 &&
                                                                logs[0]
                                                                    .state !== 0
                                                        "
                                                        type="grow"
                                                        small
                                                        variant="warning"
                                                    ></b-spinner>
                                                    <i
                                                        v-else-if="
                                                            !file.exists &&
                                                                (logs[0]
                                                                    .state ===
                                                                    6 ||
                                                                    logs[0]
                                                                        .state ===
                                                                        0)
                                                        "
                                                        class="far fa-times-circle text-danger fa-fw"
                                                    ></i>
                                                    <i
                                                        v-else
                                                        class="fas fa-check text-success fa-fw"
                                                    ></i>
                                                </b-col>
                                                <b-col
                                                    align-self="end"
                                                    class="text-left"
                                                >
                                                    {{ file.name }}
                                                </b-col>
                                                <b-col
                                                    md="auto"
                                                    align-self="end"
                                                >
                                                    <b-button
                                                        id="popover-reactive-1"
                                                        :disabled="
                                                            !file.exists ||
                                                                !(
                                                                    file.name
                                                                        .toLowerCase()
                                                                        .includes(
                                                                            'png'
                                                                        ) ||
                                                                    file.name
                                                                        .toLowerCase()
                                                                        .includes(
                                                                            'jpg'
                                                                        ) ||
                                                                    file.name
                                                                        .toLowerCase()
                                                                        .includes(
                                                                            'jpeg'
                                                                        )
                                                                )
                                                        "
                                                        :variant="
                                                            darkMode
                                                                ? 'outline-light'
                                                                : 'outline-dark'
                                                        "
                                                        size="sm"
                                                        v-b-tooltip.hover
                                                        :title="
                                                            'View ' + file.name
                                                        "
                                                        @click="
                                                            viewFile(file.name)
                                                        "
                                                    >
                                                        <i
                                                            class="fas fa-eye fa-fw"
                                                        ></i>
                                                        View
                                                    </b-button>
                                                </b-col>
                                                <b-col
                                                    md="auto"
                                                    align-self="end"
                                                >
                                                    <b-button
                                                        :disabled="!file.exists"
                                                        :variant="
                                                            darkMode
                                                                ? 'outline-light'
                                                                : 'outline-dark'
                                                        "
                                                        size="sm"
                                                        v-b-tooltip.hover
                                                        :title="
                                                            'Download ' +
                                                                file.name
                                                        "
                                                        @click="
                                                            downloadFile(
                                                                file.name
                                                            )
                                                        "
                                                    >
                                                        <i
                                                            class="fas fa-download fa-fw"
                                                        ></i>
                                                        Download
                                                    </b-button>
                                                </b-col>
                                            </b-row>
                                            <!--<b-row class="pl-1 pr-1 pb-1">
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
                                    </b-row>-->
                                        </b-card-body>
                                        <b-card-body
                                            v-else-if="
                                                outputFilesExpanded &&
                                                    flow.config.output
                                            "
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
                                                    Output files expected but
                                                    not found
                                                </b-col>
                                            </b-row>
                                            <b-row
                                                align-h="center"
                                                align-v="center"
                                            >
                                                <b-col>
                                                    <b
                                                        ><code
                                                            >{{
                                                                flow.config
                                                                    .output.path
                                                                    ? flow
                                                                          .config
                                                                          .output
                                                                          .path +
                                                                      '/'
                                                                    : ''
                                                            }}{{
                                                                flow.config
                                                                    .output
                                                                    .include
                                                                    ? (flow
                                                                          .config
                                                                          .output
                                                                          .exclude
                                                                          ? '+ '
                                                                          : '') +
                                                                      (flow
                                                                          .config
                                                                          .output
                                                                          .include
                                                                          .patterns
                                                                          ? '*.' +
                                                                            flow.config.output.include.patterns.join(
                                                                                ', *.'
                                                                            ) +
                                                                            ', '
                                                                          : []) +
                                                                      (flow
                                                                          .config
                                                                          .output
                                                                          .include
                                                                          .names
                                                                          ? flow.config.output.include.names.join(
                                                                                ', '
                                                                            )
                                                                          : [])
                                                                    : ''
                                                            }}{{
                                                                flow.config
                                                                    .output
                                                                    .exclude
                                                                    ? ' - ' +
                                                                      (flow
                                                                          .config
                                                                          .output
                                                                          .exclude
                                                                          .patterns
                                                                          ? '*.' +
                                                                            flow.config.output.exclude.patterns.join(
                                                                                ', *.'
                                                                            ) +
                                                                            ', '
                                                                          : []) +
                                                                      (flow
                                                                          .config
                                                                          .output
                                                                          .exclude
                                                                          .names
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
                                    <!--<b-card
                                    v-if="
                                        flow.config.output &&
                                            (run.state === 6 || run.state === 0)
                                    "
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :footer-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
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
                                </b-card>-->
                                </b-col>
                            </b-row>
                        </div>
                    </b-col>
                </b-row>
            </div>
        </b-container>
        <b-modal
            ok-only
            :body-bg-variant="darkMode ? 'dark' : 'light'"
            :header-bg-variant="darkMode ? 'dark' : 'light'"
            :footer-bg-variant="darkMode ? 'dark' : 'light'"
            :title-class="darkMode ? 'text-white' : 'text-dark'"
            :header-text-variant="darkMode ? 'white' : 'dark'"
            :body-text-variant="darkMode ? 'white' : 'dark'"
            header-border-variant="secondary"
            footer-border-variant="secondary"
            ok-variant="secondary"
            ok-title="Close"
            size="xl"
            centered
            :title="thumbnailTitle"
            id="thumbnail"
            class="overflow-hidden"
            @close="onThumbnailHidden"
        >
            <b-spinner
                v-if="thumbnailLoading"
                type="grow"
                label="Loading..."
                variant="warning"
            ></b-spinner>
            <b-img
                center
                :src="thumbnailUrl"
                style="width: 68rem"
                @load="thumbnailLoaded"
                v-show="thumbnailIsLoaded"
            >
            </b-img>
        </b-modal>
        <!--<b-popover
            target="popover-reactive-1"
            triggers="click"
            :show.sync="thumbnailUrl !== ''"
            placement="auto"
            @hidden="onThumbnailHidden"
        >
            <template #title>
                {{ thumbnailTitle }}
            </template>
            <b-img :src="thumbnailUrl" style="max-width: 70rem"> </b-img
        >
        </b-popover>-->
    </div>
</template>
<script>
import WorkflowBlurb from '@/components/flow-blurb.vue';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'run',
    components: {
        WorkflowBlurb
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
            containerLogsExpanded: false,
            outputFilesExpanded: false,
            logsText: '',
            outputFilePage: 1,
            outputPageSize: 10,
            outputFiles: [],
            thumbnailTitle: '',
            thumbnailUrl: '',
            thumbnailLoading: true,
            thumbnailIsLoaded: false,
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
                                case 0:
                                    return 'Failed';
                                case 1:
                                    return 'Creating';
                                case 2:
                                    return 'Pulling';
                                case 3:
                                    return 'Running';
                                case 4:
                                    return 'Zipping';
                                case 5:
                                    return 'Pushing';
                                case 6:
                                    return 'Completed';
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
        outputList() {
            return this.outputFiles.slice(
                (this.outputFilePage - 1) * this.outputPageSize,
                this.outputFilePage * this.outputPageSize
            );
        },
        setOutputPageSize(size) {
            this.outputPageSize = size;
            this.reloadOutput(false);
        },
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
        downloadZip() {
            this.downloadFile(`${this.$router.currentRoute.params.id}.zip`);
        },
        thumbnailLoaded() {
            this.thumbnailIsLoaded = true;
            this.thumbnailLoading = false;
        },
        onThumbnailHidden() {
            this.thumbnailUrl = '';
            this.thumbnailTitle = '';
            this.thumbnailIsLoaded = false;
            this.thumbnailLoading = true;
        },
        viewFile(file) {
            this.thumbnailUrl = `/apis/v1/runs/${this.$router.currentRoute.params.id}/thumbnail/${file}/`;
            this.thumbnailTitle = file;
            this.$bvModal.show('thumbnail');
        },
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
        expandContainerLogs() {
            this.containerLogsExpanded = !this.containerLogsExpanded;
        },
        expandOutputFiles() {
            this.outputFilesExpanded = !this.outputFilesExpanded;
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
                case 0:
                    return 'Failed';
                case 1:
                    return 'Creating';
                case 2:
                    return 'Pulling';
                case 3:
                    return 'Running';
                case 4:
                    return 'Zipping';
                case 5:
                    return 'Pushing';
                case 6:
                    return 'Completed';
            }
        },
        anyStatuses(state) {
            return this.logs.some(function(l) {
                return l.state === state;
            });
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
        walltimeElapsed() {
            if (!this.anyStatuses(2) && !this.anyStatuses(3)) return null;

            let start = moment(
                this.logs.find(s => s.state === 2 || s.state === 3).date
            );
            let end =
                this.anyStatuses(0) || this.anyStatuses(6)
                    ? moment(
                          this.logs.find(s => s.state === 0 || s.state === 6)
                              .date
                      )
                    : moment();
            let diff = end.diff(start);
            return moment.duration(diff);
        },
        walltimeRemaining() {
            if (!this.anyStatuses(2) && !this.anyStatuses(3)) return null;

            let start = moment(
                this.logs.find(s => s.state === 2 || s.state === 3).date
            );
            let walltimeSplit = this.flow.config.resources.time.split(':');
            if (walltimeSplit.length !== 3) throw 'Malformed walltime';
            let hours = parseInt(walltimeSplit[0]);
            let minutes = parseInt(walltimeSplit[1]);
            let seconds = parseInt(walltimeSplit[2]);
            let end = start.clone();
            end.add(hours, 'h')
                .add(minutes, 'm')
                .add(seconds, 's');
            let diff = end.diff(start);
            return moment.duration(diff);
        },
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
