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
                        <h5
                            :class="
                                darkMode
                                    ? 'text-center text-white'
                                    : 'text-center text-dark'
                            "
                        >
                            This run does not exist.
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
                            <h5 v-if="run.tags.length > 0">
                                <b-badge
                                    v-for="tag in run.tags"
                                    v-bind:key="tag"
                                    class="mr-2"
                                    variant="warning"
                                    >{{ tag }}</b-badge
                                >
                            </h5>
                            <b-row class="m-0 p-0 mb-2">
                                <b-col align-self="end" class="m-0 p-0">
                                    <h5
                                        :class="
                                            darkMode
                                                ? 'theme-dark'
                                                : 'theme-light'
                                        "
                                    >
                                        <b-badge
                                            class="mr-1"
                                            variant="secondary"
                                            >{{ run.id }}</b-badge
                                        >
                                        <small
                                            v-if="runComplete"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                        >
                                            {{
                                                runComplete
                                                    ? 'ran'
                                                    : 'has been running'
                                            }}
                                            for
                                            {{ walltimeTotal.humanize() }}
                                        </small>
                                        <!--<small
                                                        v-if="
                                                            walltimeRemaining !==
                                                                null &&
                                                                walltimeRemaining >
                                                                    0 &&
                                                                run
                                                        "
                                                        :class="
                                                            walltimeRemaining.minutes() >
                                                            5
                                                                ? 'text-secondary'
                                                                : 'text-danger'
                                                        "
                                                        >{{
                                                            walltimeRemaining.hours()
                                                        }}
                                                        hours,
                                                        {{
                                                            walltimeRemaining.minutes()
                                                        }}
                                                        minutes,
                                                        {{
                                                            walltimeRemaining.seconds()
                                                        }}
                                                        seconds remaining before
                                                        timeout</small
                                                    >
                                                    <small
                                                        v-else-if="
                                                            walltimeRemaining !==
                                                                null
                                                        "
                                                        class="text-danger"
                                                        >Exceeded time
                                                        allocation ({{
                                                            parseSeconds(
                                                                run.timeout
                                                            ).hours()
                                                        }}
                                                        hours,
                                                        {{
                                                            parseSeconds(
                                                                run.timeout
                                                            ).minutes()
                                                        }}
                                                        minutes,
                                                        {{
                                                            parseSeconds(
                                                                run.timeout
                                                            ).seconds()
                                                        }}
                                                        seconds)</small
                                                    >-->
                                        <!--<b-badge
                                            :variant="
                                                run.state === FAILURE
                                                    ? 'danger'
                                                    : run.state === SUCCESS
                                                    ? 'success'
                                                    : 'warning'
                                            "
                                            >{{ run.state }}
                                        </b-badge>-->
                                        <small> on </small>
                                        <b-badge
                                            variant="secondary"
                                            class="mr-0"
                                            >{{ run.target }}</b-badge
                                        >
                                        <small>
                                            {{ updatedFormatted }}
                                        </small>
                                    </h5>
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
                                            refreshedCountdownChanged
                                        "
                                    >
                                        Logs refreshed.
                                    </b-alert>
                                </b-col>
                                <b-col md="auto" class="m-0" align-self="start">
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
                                        <i class="fas fa-redo"></i>
                                    </b-button>
                                </b-col>
                            </b-row>
                            <!--<b-row class="m-1 mb-3">
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    class="text-center ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Creating
                                </b-col>
                                <b-col
                                    md="auto"
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
                                        variant="warning"
                                        :animated="true"
                                    ></b-progress>
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Submit container(s)
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    class="text-center ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Submitting container(s)
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Submitted container(s)
                                </b-col>
                                <b-col
                                    align-self="end"
                                    class="text-center mb-2"
                                >
                                    <b-progress
                                        height="0.3rem"
                                        :value="1"
                                        :max="1"
                                        variant="warning"
                                        :animated="true"
                                    ></b-progress>
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Run container(s)
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    class="text-center ml-0 mr-0"
                                >
                                    <b-spinner small variant="warning">
                                    </b-spinner>
                                    Running container(s)
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    class="text-center ml-0 mr-0"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Ran container(s)
                                </b-col>
                                <b-col
                                    align-self="end"
                                    class="text-center mb-2"
                                >
                                    <b-progress
                                        height="0.3rem"
                                        :value="1"
                                        :max="1"
                                        variant="warning"
                                        :animated="true"
                                    ></b-progress>
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="run.is_failed"
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
                                    v-else-if="!run.is_complete"
                                    class="text-center  ml-0 mr-0"
                                >
                                    <i class="far fa-circle text-secondary"></i>
                                    Next: Complete
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-else-if="run.is_success"
                                    class="text-center"
                                >
                                    <i class="fas fa-check text-success"></i>
                                    Complete
                                </b-col>
                            </b-row>-->
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
                                        </b-card-body>
                                    </b-card>
                                    <b-row class="m-0 p-0">
                                        <b-col class="m-0 p-0"
                                            ><b-card
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
                                                        darkMode
                                                            ? 'dark'
                                                            : 'white'
                                                    "
                                                >
                                                    <b-row>
                                                        <b-col>
                                                            <h4
                                                                :class="
                                                                    darkMode
                                                                        ? 'text-white'
                                                                        : 'text-dark'
                                                                "
                                                            >
                                                                Status Logs
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
                                                                    localLogsExpanded
                                                                        ? 'Collapse Container Logs'
                                                                        : 'Expand Container Logs'
                                                                "
                                                                @click="
                                                                    expandLocalLogs
                                                                "
                                                            >
                                                                <i
                                                                    v-if="
                                                                        localLogsExpanded
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
                                                    v-if="localLogsExpanded"
                                                    :class="
                                                        darkMode
                                                            ? 'theme-container-dark mt-0 pt-0'
                                                            : 'theme-container-light mt-0 pt-0'
                                                    "
                                                >
                                                    <b-row
                                                        align-h="center"
                                                        v-if="loadingLocalLogs"
                                                    >
                                                        <b-spinner
                                                            class="mt-3"
                                                            type="grow"
                                                            label="Loading..."
                                                            variant="warning"
                                                        ></b-spinner>
                                                    </b-row>
                                                    <b-row
                                                        v-else-if="
                                                            localLogsText !== ''
                                                        "
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
                                                            {{ localLogsText }}
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
                                                                title="Download PlantIT Log File"
                                                                @click="
                                                                    downloadLocalLogs
                                                                "
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
                                                                    localLogsPageSize
                                                                "
                                                                variant="warning"
                                                                size="sm"
                                                            >
                                                                <b-dropdown-item
                                                                    @click="
                                                                        setLocalLogsPageSize(
                                                                            10
                                                                        )
                                                                    "
                                                                    >10</b-dropdown-item
                                                                >
                                                                <b-dropdown-item
                                                                    @click="
                                                                        setLocalLogsPageSize(
                                                                            20
                                                                        )
                                                                    "
                                                                    >20</b-dropdown-item
                                                                >
                                                                <b-dropdown-item
                                                                    @click="
                                                                        setLocalLogsPageSize(
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
                                            </b-card></b-col
                                        >
                                        <b-col class="m-0 p-0"
                                            ><b-card
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
                                                        darkMode
                                                            ? 'dark'
                                                            : 'white'
                                                    "
                                                >
                                                    <b-row>
                                                        <b-col>
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
                                                                    targetLogsExpanded
                                                                        ? 'Collapse Container Logs'
                                                                        : 'Expand Container Logs'
                                                                "
                                                                @click="
                                                                    expandTargetLogs
                                                                "
                                                            >
                                                                <i
                                                                    v-if="
                                                                        targetLogsExpanded
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
                                                    v-if="targetLogsExpanded"
                                                    :class="
                                                        darkMode
                                                            ? 'theme-container-dark mt-0 pt-0'
                                                            : 'theme-container-light mt-0 pt-0'
                                                    "
                                                >
                                                    <b-row
                                                        align-h="center"
                                                        v-if="loadingTargetLogs"
                                                    >
                                                        <b-spinner
                                                            class="mt-3"
                                                            type="grow"
                                                            label="Loading..."
                                                            variant="warning"
                                                        ></b-spinner>
                                                    </b-row>
                                                    <b-row
                                                        v-if="
                                                            !loadingTargetLogs &&
                                                                targetLogsText ===
                                                                    ''
                                                        "
                                                        ><b-col
                                                            class="text-center"
                                                            ><br />
                                                            Nothing
                                                            here...<b-img
                                                                center
                                                                width="100rem"
                                                                src="https://i.pinimg.com/originals/bf/ec/5c/bfec5cfd86fca6de0b4574d7c73f7930.jpg"
                                                            ></b-img></b-col
                                                    ></b-row>
                                                    <b-row
                                                        v-if="
                                                            targetLogsText !==
                                                                ''
                                                        "
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
                                                            {{ targetLogsText }}
                                                        </b-col>
                                                    </b-row>
                                                    <b-row
                                                        v-if="
                                                            targetLogsText !==
                                                                ''
                                                        "
                                                    >
                                                        <b-col align-self="end">
                                                            <b-button
                                                                :variant="
                                                                    darkMode
                                                                        ? 'outline-light'
                                                                        : 'outline-dark'
                                                                "
                                                                size="sm"
                                                                v-b-tooltip.hover
                                                                :title="
                                                                    'Download ' +
                                                                        run.target +
                                                                        ' Log File'
                                                                "
                                                                @click="
                                                                    downloadTargetLogs
                                                                "
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
                                                                    targetLogsPageSize
                                                                "
                                                                variant="warning"
                                                                size="sm"
                                                            >
                                                                <b-dropdown-item
                                                                    @click="
                                                                        setTargetLogsPageSize(
                                                                            10
                                                                        )
                                                                    "
                                                                    >10</b-dropdown-item
                                                                >
                                                                <b-dropdown-item
                                                                    @click="
                                                                        setTargetLogsPageSize(
                                                                            20
                                                                        )
                                                                    "
                                                                    >20</b-dropdown-item
                                                                >
                                                                <b-dropdown-item
                                                                    @click="
                                                                        setTargetLogsPageSize(
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
                                            </b-card></b-col
                                        >
                                    </b-row>
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
                                                                setOutputFilesPageSize(
                                                                    10
                                                                )
                                                            "
                                                            >10</b-dropdown-item
                                                        >
                                                        <b-dropdown-item
                                                            @click="
                                                                setOutputFilesPageSize(
                                                                    20
                                                                )
                                                            "
                                                            >20</b-dropdown-item
                                                        >
                                                        <b-dropdown-item
                                                            @click="
                                                                setOutputFilesPageSize(
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
                                                v-for="file in listOutputFiles()"
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
                                                                !runComplete
                                                        "
                                                        type="grow"
                                                        small
                                                        variant="warning"
                                                    ></b-spinner>
                                                    <i
                                                        v-else-if="
                                                            !file.exists &&
                                                                runComplete
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
                                                                (!fileIsImage(
                                                                    file
                                                                ) &&
                                                                    !fileIsText(
                                                                        file
                                                                    ))
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
                                                    flow.config.output &&
                                                    !runComplete
                                            "
                                            class="mt-0 pt-0"
                                        >
                                            <b-row
                                                align-h="center"
                                                align-v="center"
                                                class="mt-2 text-center"
                                            >
                                                <b-col>
                                                    Output files expected:
                                                </b-col>
                                            </b-row>
                                            <b-row
                                                align-h="center"
                                                align-v="center"
                                                class="text-center"
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
                                                    <br />
                                                    <br />
                                                    <b-spinner
                                                        type="grow"
                                                        variant="warning"
                                                    ></b-spinner>
                                                </b-col>
                                            </b-row>
                                            <br />
                                        </b-card-body>
                                        <b-card-body
                                            v-else-if="
                                                outputFilesExpanded &&
                                                    flow.config.output &&
                                                    runComplete
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
                v-if="loadingThumbnail"
                type="grow"
                label="Loading..."
                variant="warning"
            ></b-spinner>
            <b-img
                center
                :src="thumbnailUrl"
                style="width: 68rem"
                @load="thumbnailLoaded"
                v-show="thumbnailDoneLoading"
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
            // run status constants
            PENDING: 'PENDING',
            STARTED: 'STARTED',
            SUCCESS: 'SUCCESS',
            FAILURE: 'FAILURE',
            REVOKED: 'REVOKED',
            // user data
            userData: null,
            reloadAlertDismissSeconds: 2,
            reloadAlertDismissCountdown: 0,
            showReloadAlert: false,
            // flow
            flow: null,
            // run
            loadingRun: true,
            run: null,
            runNotFound: false,
            // walltime
            walltimeTotal: null,
            walltimeRemaining: null,
            runtimeUpdateInterval: null,
            // PlantIT logs
            loadingLocalLogs: false,
            localLogsText: '',
            localLogsExpanded: false,
            localLogsPageSize: 10,
            // deployment target logs
            loadingTargetLogs: false,
            targetLogsText: '',
            targetLogsExpanded: false,
            targetLogsPageSize: 10,
            // output files
            loadingOutputFiles: false,
            outputFiles: [],
            outputFilesExpanded: false,
            outputFilePage: 1,
            outputPageSize: 10,
            // thumbnail view
            loadingThumbnail: true,
            thumbnailUrl: '',
            thumbnailTitle: '',
            thumbnailDoneLoading: false
        };
    },
    methods: {
        fileIsImage(file) {
            return (
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'png' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpg' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpeg'
            );
        },
        fileIsText(file) {
            return (
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'txt' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'csv' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'tsv' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yml' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yaml'
            );
        },
        fileIsViewable(file) {
            return (
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'png' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpg' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpeg' ||
                file.name
                    .toLowerCase()
                    .split('.')
                    .pop() === 'txt'
            );
        },
        parseSeconds(seconds) {
            return moment.utc(seconds * 1000);
        },
        setLocalLogsPageSize(size) {
            this.localLogsPageSize = size;
            this.reloadLocalLogs(false);
        },
        setTargetLogsPageSize(size) {
            this.targetLogsPageSize = size;
            this.reloadTargetLogs(false);
        },
        listOutputFiles() {
            return this.outputFiles.slice(
                (this.outputFilePage - 1) * this.outputPageSize,
                this.outputFilePage * this.outputPageSize
            );
        },
        setOutputFilesPageSize(size) {
            this.outputPageSize = size;
            this.reloadTargetLogs(false);
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
                    if (this.run.updated === null) return;
                    this.reloadLocalLogs(toast);
                    this.reloadTargetLogs(toast);
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
                            this.loadingRun = false;
                        })
                        .catch(error => {
                            Sentry.captureException(error);
                            throw error;
                        });
                })
                .catch(error => {
                    this.runNotFound = true;
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
            this.thumbnailDoneLoading = true;
            this.loadingThumbnail = false;
        },
        onThumbnailHidden() {
            this.thumbnailUrl = '';
            this.thumbnailTitle = '';
            this.thumbnailDoneLoading = false;
            this.loadingThumbnail = true;
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
        downloadLocalLogs() {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/local_logs/`
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
                    link.setAttribute('download', this.localLogFileName);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        reloadLocalLogs(toast) {
            this.loadingLocalLogs = true;
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/local_logs_text/${this.localLogsPageSize}/`
                )
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }
                    this.localLogsText = response.data;
                    this.loadingLocalLogs = false;
                    if (toast) this.showRefreshedAlert();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.loadingLocalLogs = false;
                    return error;
                });
        },
        downloadTargetLogs() {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/target_logs/`
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
                    link.setAttribute('download', this.targetLogFileName);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        reloadTargetLogs(toast) {
            this.loadingTargetLogs = true;
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/target_logs_text/${this.targetLogsPageSize}/`
                )
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }
                    this.targetLogsText = response.data;
                    this.loadingTargetLogs = false;
                    if (toast) this.showRefreshedAlert();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.loadingTargetLogs = false;
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
                    this.loadingOutputFiles = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.loadingOutputFiles = false;
                    return error;
                });
        },
        expandLocalLogs() {
            this.localLogsExpanded = !this.localLogsExpanded;
        },
        expandTargetLogs() {
            this.targetLogsExpanded = !this.targetLogsExpanded;
        },
        expandOutputFiles() {
            this.outputFilesExpanded = !this.outputFilesExpanded;
        },
        refreshedCountdownChanged(dismissCountDown) {
            this.reloadAlertDismissCountdown = dismissCountDown;
        },
        showRefreshedAlert() {
            this.reloadAlertDismissCountdown = this.reloadAlertDismissSeconds;
        },
        updateWalltime() {
            if (this.run === null || this.run.created === null) return null;
            let complete =
                this.run.state === this.SUCCESS ||
                this.run.state === this.FAILURE;
            if (complete) clearInterval(this.runtimeUpdateInterval);

            let started = moment(this.run.created);
            let updated = moment(this.run.updated);
            let timeout = started.clone();
            timeout.add(this.run.timeout, 's');
            this.walltimeTotal = moment.duration(
                (complete ? updated : moment()).diff(started)
            );
            this.walltimeRemaining = moment.duration(timeout.diff(moment()));
        }
    },
    async mounted() {
        await this.reloadRun(false);
        this.runtimeUpdateInterval = setInterval(this.updateWalltime, 1000);
    },
    computed: {
        localLogFileName() {
            return `${this.$router.currentRoute.params.id}.plantit.log`;
        },
        targetLogFileName() {
            return `${
                this.$router.currentRoute.params.id
            }.${this.run.target.toLowerCase()}.log`;
        },
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserCyVerseProfile',
            'currentUserGitHubProfile',
            'loggedIn',
            'darkMode'
        ]),
        runComplete() {
            return (
                this.run.state === this.SUCCESS ||
                this.run.state === this.FAILURE ||
                this.run.state === this.REVOKED
            );
        },
        updatedFormatted() {
            return `${moment(this.run.updated).fromNow()}`;
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
