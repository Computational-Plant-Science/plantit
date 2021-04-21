<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            profile.darkMode
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
                        <p
                            :class="
                                profile.darkMode
                                    ? 'text-center text-white'
                                    : 'text-center text-dark'
                            "
                        >
                            <i
                                class="fas fa-exclamation-circle fa-3x fa-fw"
                            ></i>
                            <br />
                            <br />
                            This run does not exist.
                            <br />
                            It may have been cleaned up.
                        </p>
                    </b-col>
                </b-row>
            </div>
            <div v-else>
                <b-row>
                    <b-col>
                        <b-row align-h="center" v-if="loadingRun">
                            <b-spinner
                                type="grow"
                                label="Loading..."
                                variant="secondary"
                            ></b-spinner>
                        </b-row>
                        <div v-else-if="getWorkflow.config">
                            <b-row class="m-0 p-0">
                                <b-col v-if="showCanceledAlert" class="m-0 p-0">
                                    <b-alert
                                        :show="showCanceledAlert"
                                        :variant="
                                            canceledAlertMessage.includes(
                                                'no longer running'
                                            )
                                                ? 'success'
                                                : 'warning'
                                        "
                                        dismissible
                                        @dismissed="showCanceledAlert = false"
                                    >
                                        {{ canceledAlertMessage }}
                                    </b-alert>
                                </b-col>
                                <b-col
                                    v-if="showFailedToCancelAlert"
                                    class="m-0 p-0"
                                >
                                    <b-alert
                                        :show="showFailedToCancelAlert"
                                        variant="danger"
                                        dismissible
                                        @dismissed="
                                            showFailedToCancelAlert = false
                                        "
                                    >
                                        Failed to cancel run {{ getRun.id }}.
                                    </b-alert>
                                </b-col>
                            </b-row>
                            <b-row class="m-0 p-0">
                                <b-col align-self="end" class="m-0 p-0">
                                    <h4>
                                        <b-badge
                                            v-for="tag in getRun.tags"
                                            v-bind:key="tag"
                                            class="mr-2"
                                            variant="secondary"
                                            >{{ tag }}</b-badge
                                        >
                                    </h4>
                                </b-col>
                            </b-row>
                            <b-row class="m-0 p-0">
                                <b-col align-self="end" class="m-0 p-0">
                                    <h5
                                        :class="
                                            profile.darkMode
                                                ? 'theme-dark'
                                                : 'theme-light'
                                        "
                                    >
                                        <b-spinner
                                            class="mb-1 mr-1"
                                            small
                                            v-if="!getRun.is_complete"
                                            :variant="
                                                profile.darkMode
                                                    ? 'light'
                                                    : 'dark'
                                            "
                                        >
                                        </b-spinner>
                                        <b class="ml-1 mr-0">{{ getRun.id }}</b>
                                        <small> on </small>
                                        <b class="mr-0">{{ getRun.cluster }}</b>
                                        <b-badge
                                            :variant="
                                                getRun.is_failure ||
                                                getRun.is_timeout
                                                    ? 'danger'
                                                    : getRun.is_success
                                                    ? 'success' : getRun.is_cancelled ? 'secondary'
                                                    : 'warning'
                                            "
                                            class="ml-2 mr-2"
                                            >{{ getRun.job_status }}</b-badge
                                        >
                                    </h5>
                                </b-col>
                                <b-col
                                    v-if="
                                        getRun.is_complete && getRun.can_restart
                                    "
                                    md="auto"
                                    class="m-0 mb-2"
                                    align-self="start"
                                >
                                    <b-button
                                        :disabled="resubmitted"
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        size="sm"
                                        v-b-tooltip.hover
                                        :title="'Restart this run'"
                                        @click="onRestart"
                                    >
                                        <i class="fas fa-level-up-alt"></i>
                                        Restart
                                        <b-spinner
                                            small
                                            v-if="resubmitted"
                                            label="Loading..."
                                            :variant="
                                                profile.darkMode
                                                    ? 'light'
                                                    : 'dark'
                                            "
                                            style="width: 0.7rem; height: 0.7rem;"
                                        ></b-spinner>
                                    </b-button>
                                </b-col>
                                <b-col
                                    v-if="!getRun.is_complete"
                                    md="auto"
                                    class="m-0 mb-2"
                                    align-self="start"
                                >
                                    <b-button
                                        :disabled="cancelled"
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        size="sm"
                                        v-b-tooltip.hover
                                        title="Cancel Run"
                                        @click="onCancel"
                                    >
                                        <i class="fas fa-times"></i>
                                        Cancel<b-spinner
                                            small
                                            v-if="cancelled"
                                            label="Loading..."
                                            :variant="
                                                profile.darkMode
                                                    ? 'light'
                                                    : 'dark'
                                            "
                                            class="ml-2 mb-1"
                                        ></b-spinner>
                                    </b-button>
                                </b-col>
                                <b-col
                                    md="auto"
                                    class="m-0 mb-2"
                                    align-self="start"
                                >
                                    <b-button
                                        v-if="getRun.is_complete"
                                        :disabled="loadingRun"
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        size="sm"
                                        v-b-tooltip.hover
                                        title="Refresh Run"
                                        @click="refreshRun"
                                    >
                                        <i class="fas fa-redo"></i>
                                        Refresh
                                        <b-spinner
                                            small
                                            v-if="loadingRun"
                                            label="Loading..."
                                            :variant="
                                                profile.darkMode
                                                    ? 'light'
                                                    : 'dark'
                                            "
                                            class="ml-2 mb-1"
                                        ></b-spinner>
                                    </b-button>
                                </b-col>
                                <b-col
                                    v-if="getRun.is_complete"
                                    md="auto"
                                    class="m-0 mb-2"
                                    align-self="start"
                                >
                                    <b-button
                                        variant="outline-danger"
                                        size="sm"
                                        v-b-tooltip.hover
                                        title="Delete Run"
                                        @click="showDeletePrompt"
                                    >
                                        <i class="fas fa-trash"></i>
                                        Delete
                                    </b-button>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <b-card
                                        :bg-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        :footer-bg-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        border-variant="default"
                                        :footer-border-variant="
                                            profile.darkMode ? 'dark' : 'white'
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
                                                :workflow="getWorkflow"
                                            ></WorkflowBlurb>
                                        </b-card-body>
                                    </b-card>
                                    <b-row class="m-0 p-0 mt-1">
                                        <b-col class="m-0 p-0">
                                            <small>
                                                Created
                                                {{ prettify(getRun.created) }}
                                            </small>
                                        </b-col>
                                        <b-col class="m-0 p-0" md="auto">
                                            <small>
                                                Last updated
                                                {{ prettify(getRun.updated) }}
                                            </small>
                                        </b-col>
                                    </b-row>
                                    <b-row class="m-0 p-0 mt-2">
                                        <b-col class="m-0 p-1">
                                            <div
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-container-dark m-0 p-1'
                                                        : 'theme-container-light m-0 p-1'
                                                "
                                            >
                                                <div>
                                                    <b-row
                                                        align-h="center"
                                                        v-if="loadingRun"
                                                    >
                                                        <b-spinner
                                                            class="mt-3"
                                                            type="grow"
                                                            label="Loading..."
                                                            variant="secondary"
                                                        ></b-spinner>
                                                    </b-row>
                                                    <b-row class="m-0">
                                                        <b-col
                                                            v-if="
                                                                getRun
                                                                    .submission_logs
                                                                    .length > 0
                                                            "
                                                            class="m-0 p-0 pl-3 pr-3 pt-1"
                                                            style="white-space: pre-line;"
                                                        >
                                                            <span
                                                                v-for="log in submissionLogs"
                                                                v-bind:key="log"
                                                                >{{
                                                                    log + '\n'
                                                                }}</span
                                                            >
                                                        </b-col>
                                                    </b-row>
                                                </div>
                                            </div>
                                            <div
                                                class="m-3"
                                                v-if="getRun.is_complete"
                                            >
                                                <b-row
                                                    align-h="center"
                                                    align-v="center"
                                                    class="mt-2"
                                                >
                                                    <b-col class="text-left">
                                                        <span
                                                            v-if="
                                                                !loadingOutputFiles
                                                            "
                                                            >{{
                                                                outputFiles.length
                                                            }}</span
                                                        >
                                                        result(s)
                                                        <br />
                                                        <b
                                                            v-if="
                                                                getWorkflow
                                                                    .config
                                                                    .output
                                                            "
                                                            ><code
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'theme-dark'
                                                                        : 'theme-light'
                                                                "
                                                                >{{
                                                                    getWorkflow
                                                                        .config
                                                                        .output
                                                                        .path
                                                                        ? getWorkflow
                                                                              .config
                                                                              .output
                                                                              .path +
                                                                          '/'
                                                                        : ''
                                                                }}{{
                                                                    (getWorkflow
                                                                        .config
                                                                        .output
                                                                        .include
                                                                        ? (getWorkflow
                                                                              .config
                                                                              .output
                                                                              .exclude
                                                                              ? '+ '
                                                                              : '') +
                                                                          (getWorkflow
                                                                              .config
                                                                              .output
                                                                              .include
                                                                              .patterns
                                                                              ? '*.' +
                                                                                getWorkflow.config.output.include.patterns.join(
                                                                                    ', *.'
                                                                                )
                                                                              : []) +
                                                                          (getWorkflow
                                                                              .config
                                                                              .output
                                                                              .include
                                                                              .names
                                                                              ? ', ' +
                                                                                getWorkflow.config.output.include.names.join(
                                                                                    ', '
                                                                                )
                                                                              : [])
                                                                        : '') +
                                                                        `, ${getRun.id}.zip`
                                                                }}{{
                                                                    getWorkflow
                                                                        .config
                                                                        .output
                                                                        .exclude
                                                                        ? ' - ' +
                                                                          (getWorkflow
                                                                              .config
                                                                              .output
                                                                              .exclude
                                                                              .patterns
                                                                              ? '*.' +
                                                                                getWorkflow.config.output.exclude.patterns.join(
                                                                                    ', *.'
                                                                                )
                                                                              : []) +
                                                                          (getWorkflow
                                                                              .config
                                                                              .output
                                                                              .exclude
                                                                              .names
                                                                              ? ', ' +
                                                                                getWorkflow.config.output.exclude.names.join(
                                                                                    ', '
                                                                                )
                                                                              : [])
                                                                        : ''
                                                                }}
                                                            </code></b
                                                        >
                                                    </b-col>
                                                    <b-col
                                                        md="auto"
                                                        align-self="end"
                                                    >
                                                        <b-dropdown
                                                            :disabled="
                                                                outputFiles !==
                                                                    null &&
                                                                    outputFiles.length ===
                                                                        0
                                                            "
                                                            class="text-right"
                                                            :text="
                                                                outputPageSize
                                                            "
                                                            dropleft
                                                            :title="
                                                                'Showing ' +
                                                                    outputPageSize +
                                                                    ' files per page'
                                                            "
                                                            v-b-tooltip.hover
                                                            :variant="
                                                                profile.darkMode
                                                                    ? 'outline-light'
                                                                    : 'white'
                                                            "
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
                                                    </b-col>
                                                    <b-col
                                                        md="auto"
                                                        align-self="end"
                                                        ><b-dropdown
                                                            :disabled="
                                                                outputFiles !==
                                                                    null &&
                                                                    outputFiles.length ===
                                                                        0
                                                            "
                                                            v-b-tooltip.hover
                                                            :title="
                                                                'Using ' +
                                                                    viewMode +
                                                                    ' view'
                                                            "
                                                            dropleft
                                                            :variant="
                                                                profile.darkMode
                                                                    ? 'outline-light'
                                                                    : 'white'
                                                            "
                                                            class="text-right"
                                                        >
                                                            <template
                                                                #button-content
                                                            >
                                                                {{ viewMode }}
                                                            </template>
                                                            <b-dropdown-item
                                                                @click="
                                                                    setViewMode(
                                                                        'List'
                                                                    )
                                                                "
                                                                >List</b-dropdown-item
                                                            >
                                                            <b-dropdown-item
                                                                @click="
                                                                    setViewMode(
                                                                        'Grid'
                                                                    )
                                                                "
                                                                >Grid</b-dropdown-item
                                                            >
                                                            <b-dropdown-item
                                                                @click="
                                                                    setViewMode(
                                                                        'Carousel'
                                                                    )
                                                                "
                                                                >Carousel</b-dropdown-item
                                                            >
                                                        </b-dropdown></b-col
                                                    >
                                                    <br />
                                                    <br />
                                                </b-row>
                                                <b-row
                                                    v-show="
                                                        viewMode !== 'Carousel'
                                                    "
                                                >
                                                    <b-col
                                                        md="auto"
                                                        align-self="end"
                                                    >
                                                        <b-pagination
                                                            v-model="
                                                                outputFilePage
                                                            "
                                                            pills
                                                            class="mt-3"
                                                            size="md"
                                                            :total-rows="
                                                                outputFiles.length
                                                            "
                                                            :per-page="
                                                                outputPageSize
                                                            "
                                                            aria-controls="outputList"
                                                        >
                                                            <template
                                                                class="theme-dark"
                                                                #page="{ page, active }"
                                                            >
                                                                <b
                                                                    v-if="
                                                                        active
                                                                    "
                                                                    >{{
                                                                        page
                                                                    }}</b
                                                                >
                                                                <i v-else>{{
                                                                    page
                                                                }}</i>
                                                            </template>
                                                        </b-pagination>
                                                    </b-col>
                                                    <b-col align-self="middle"
                                                        ><b-input-group
                                                            class="mt-3"
                                                            style="top: 2px"
                                                            size="sm"
                                                            ><template #prepend>
                                                                <b-input-group-text
                                                                    ><i
                                                                        class="fas fa-search"
                                                                    ></i
                                                                ></b-input-group-text> </template
                                                            ><b-form-input
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'theme-search-dark'
                                                                        : 'theme-search-light'
                                                                "
                                                                size="lg"
                                                                type="search"
                                                                v-model="
                                                                    resultSearchText
                                                                "
                                                            ></b-form-input>
                                                        </b-input-group>
                                                    </b-col>
                                                </b-row>
                                                <b-row
                                                    class="pl-1 pr-1 pb-1"
                                                    align-h="center"
                                                    v-if="loadingOutputFiles"
                                                >
                                                    <b-spinner
                                                        type="grow"
                                                        label="Loading..."
                                                        variant="secondary"
                                                    ></b-spinner>
                                                </b-row>
                                                <b-overlay
                                                    :show="downloading"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'dark'
                                                            : 'light'
                                                    "
                                                    rounded="sm"
                                                >
                                                    <div>
                                                        <div
                                                            v-if="
                                                                viewMode ===
                                                                    'List'
                                                            "
                                                        >
                                                            <b-row
                                                                id="outputList"
                                                                v-for="file in filteredResults"
                                                                v-bind:key="
                                                                    file.name
                                                                "
                                                                class="p-1"
                                                                style="border-top: 1px solid rgba(211, 211, 211, .5);"
                                                            >
                                                                <b-col
                                                                    align-self="end"
                                                                    md="auto"
                                                                    v-if="
                                                                        file.name
                                                                            .toLowerCase()
                                                                            .endsWith(
                                                                                'txt'
                                                                            ) ||
                                                                            file.name
                                                                                .toLowerCase()
                                                                                .endsWith(
                                                                                    'log'
                                                                                )
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
                                                                            .endsWith(
                                                                                'csv'
                                                                            )
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
                                                                            .endsWith(
                                                                                'zip'
                                                                            )
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
                                                                            .endsWith(
                                                                                'xlsx'
                                                                            )
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
                                                                            .endsWith(
                                                                                'pdf'
                                                                            )
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
                                                                    md="auto"
                                                                    align-self="end"
                                                                    class="text-left"
                                                                    style="position: relative; top: -5px; left: -40px"
                                                                >
                                                                    <b-spinner
                                                                        class="m-0 p-0"
                                                                        v-if="
                                                                            !file.exists &&
                                                                                !getRun.is_complete
                                                                        "
                                                                        type="grow"
                                                                        small
                                                                        variant="warning"
                                                                    ></b-spinner>
                                                                    <i
                                                                        v-else-if="
                                                                            !file.exists &&
                                                                                getRun.is_complete
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
                                                                    {{
                                                                        file.name
                                                                    }}
                                                                </b-col>
                                                                <b-col
                                                                    md="auto"
                                                                    align-self="end"
                                                                >
                                                                    <b-button
                                                                        :disabled="
                                                                            !file.exists ||
                                                                                downloading
                                                                        "
                                                                        :variant="
                                                                            profile.darkMode
                                                                                ? 'outline-light'
                                                                                : 'white'
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
                                                        </div>
                                                        <b-card-group
                                                            v-else-if="
                                                                viewMode ===
                                                                    'Grid'
                                                            "
                                                            columns
                                                        >
                                                            <b-card
                                                                v-for="file in filteredResults"
                                                                v-bind:key="
                                                                    file.name
                                                                "
                                                                style="min-width: 20rem;"
                                                                class="overflow-hidden mb-4 mr-4 text-left"
                                                                :bg-variant="
                                                                    profile.darkMode
                                                                        ? 'dark'
                                                                        : 'white'
                                                                "
                                                                :header-bg-variant="
                                                                    profile.darkMode
                                                                        ? 'dark'
                                                                        : 'white'
                                                                "
                                                                border-variant="default"
                                                                :header-border-variant="
                                                                    profile.darkMode
                                                                        ? 'secondary'
                                                                        : 'default'
                                                                "
                                                                :text-variant="
                                                                    profile.darkMode
                                                                        ? 'white'
                                                                        : 'dark'
                                                                "
                                                            >
                                                                <template
                                                                    #header
                                                                    ><b-img-lazy
                                                                        v-if="
                                                                            viewMode ===
                                                                                'Grid'
                                                                        "
                                                                        fluid-grow
                                                                        style="min-width: 20rem;"
                                                                        :src="
                                                                            fileIs3dModel(
                                                                                file.name
                                                                            ) ||
                                                                            (!fileIsText(
                                                                                file.name
                                                                            ) &&
                                                                                !fileIsImage(
                                                                                    file.name
                                                                                ))
                                                                                ? require('../assets/no_preview_thumbnail.png')
                                                                                : thumbnailFor(
                                                                                      file.path
                                                                                  )
                                                                        "
                                                                    ></b-img-lazy
                                                                ></template>
                                                                <p
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-light'
                                                                            : 'text-dark'
                                                                    "
                                                                >
                                                                    <b>{{
                                                                        file.name
                                                                    }}</b>
                                                                    <br />
                                                                </p>
                                                                <hr />
                                                                <b-button
                                                                    :title="
                                                                        `Download ${file.name}`
                                                                    "
                                                                    v-b-tooltip.hover
                                                                    :variant="
                                                                        profile.darkMode
                                                                            ? 'outline-light'
                                                                            : 'white'
                                                                    "
                                                                    class="text-left m-0"
                                                                    @click="
                                                                        downloadFile(
                                                                            file.name
                                                                        )
                                                                    "
                                                                >
                                                                    <i
                                                                        class="fas fa-download fa-fw"
                                                                    ></i>
                                                                </b-button>
                                                            </b-card>
                                                        </b-card-group>
                                                        <b-carousel
                                                            v-if="
                                                                viewMode ===
                                                                    'Carousel'
                                                            "
                                                            v-model="
                                                                currentCarouselSlide
                                                            "
                                                            controls
                                                            :interval="0"
                                                            @sliding-start="
                                                                slide =>
                                                                    getTextFile(
                                                                        outputFiles[
                                                                            slide
                                                                        ]
                                                                    )
                                                            "
                                                            @sliding-end="
                                                                slide =>
                                                                    renderPreview(
                                                                        outputFiles[
                                                                            slide
                                                                        ]
                                                                    )
                                                            "
                                                        >
                                                            <b-carousel-slide
                                                                v-for="file in outputFiles"
                                                                v-bind:key="
                                                                    file.name
                                                                "
                                                                :img-src="
                                                                    fileIsImage(
                                                                        file.name
                                                                    )
                                                                        ? thumbnailFor(
                                                                              file.path
                                                                          )
                                                                        : ''
                                                                "
                                                                ><template
                                                                    #img
                                                                    v-if="
                                                                        fileIsText(
                                                                            file.name
                                                                        )
                                                                    "
                                                                >
                                                                    <div
                                                                        :class="
                                                                            profile.darkMode
                                                                                ? 'theme-container-dark'
                                                                                : 'theme-container-light'
                                                                        "
                                                                        style="min-height: 50rem;white-space: pre-line;"
                                                                    >
                                                                        <b-row
                                                                            class="m-0"
                                                                        >
                                                                            <b-col
                                                                                v-if="
                                                                                    textContent.length >
                                                                                        0
                                                                                "
                                                                                class="m-0 p-0 pl-3 pr-3 pt-1"
                                                                                style="white-space: pre-line;"
                                                                            >
                                                                                <span
                                                                                    v-for="line in textContent"
                                                                                    v-bind:key="
                                                                                        line
                                                                                    "
                                                                                    >{{
                                                                                        line +
                                                                                            '\n'
                                                                                    }}</span
                                                                                >
                                                                            </b-col>
                                                                        </b-row>
                                                                    </div>
                                                                </template>
                                                                <template
                                                                    v-else-if="
                                                                        fileIs3dModel(
                                                                            file.name
                                                                        )
                                                                    "
                                                                    #img
                                                                    ><div
                                                                        :id="
                                                                            file.id
                                                                        "
                                                                        :class="
                                                                            profile.darkMode
                                                                                ? 'theme-container-dark'
                                                                                : 'theme-container-light'
                                                                        "
                                                                        style="min-height: 50rem;white-space: pre-line;"
                                                                    ></div
                                                                ></template>
                                                                <template
                                                                    v-else-if="
                                                                        !fileIsImage(
                                                                            file.name
                                                                        )
                                                                    "
                                                                    #img
                                                                    ><div
                                                                        :class="
                                                                            profile.darkMode
                                                                                ? 'theme-container-dark'
                                                                                : 'theme-container-light'
                                                                        "
                                                                        style="min-height: 50rem;white-space: pre-line;"
                                                                    >
                                                                        <b-img
                                                                            :src="
                                                                                require('../assets/no_preview_thumbnail.png')
                                                                            "
                                                                        ></b-img></div
                                                                ></template>
                                                                <template
                                                                    #default
                                                                    ><b-row
                                                                        :class="
                                                                            profile.darkMode
                                                                                ? 'theme-container-dark p-3'
                                                                                : 'theme-container-light p-3'
                                                                        "
                                                                        style="opacity: 0.9;"
                                                                    >
                                                                        <b-col
                                                                            class="text-left"
                                                                        >
                                                                            <h5
                                                                                :class="
                                                                                    profile.darkMode
                                                                                        ? 'text-light'
                                                                                        : 'text-dark'
                                                                                "
                                                                            >
                                                                                {{
                                                                                    file.name
                                                                                }}
                                                                            </h5>
                                                                        </b-col>
                                                                        <b-col
                                                                            md="auto"
                                                                            align-self="end"
                                                                        >
                                                                            <b-button
                                                                                :title="
                                                                                    `Download ${file.name}`
                                                                                "
                                                                                :variant="
                                                                                    profile.darkMode
                                                                                        ? 'outline-light'
                                                                                        : 'white'
                                                                                "
                                                                                class="text-right m-0"
                                                                                @click="
                                                                                    downloadFile(
                                                                                        file.name
                                                                                    )
                                                                                "
                                                                            >
                                                                                <i
                                                                                    class="fas fa-download fa-fw"
                                                                                ></i>
                                                                            </b-button>
                                                                        </b-col> </b-row></template
                                                            ></b-carousel-slide>
                                                        </b-carousel>
                                                    </div>
                                                </b-overlay>
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
                                            </div>
                                            <!--<div
                                                        v-else-if="
                                                            flow.config
                                                                .output &&
                                                                getRun.is_complete
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
                                                                Output files
                                                                expected but not
                                                                found
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
                                                                            flow
                                                                                .config
                                                                                .output
                                                                                .path
                                                                                ? flow
                                                                                      .config
                                                                                      .output
                                                                                      .path +
                                                                                  '/'
                                                                                : ''
                                                                        }}{{
                                                                            flow
                                                                                .config
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
                                                                            flow
                                                                                .config
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
                                                    </div>-->
                                        </b-col>
                                    </b-row>

                                    <!--<b-card
                                    v-if="
                                        flow.config.output &&
                                            (getRun.state === 6 || getRun.state === 0)
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
            id="delete"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            ok-variant="outline-danger"
            title="Delete this run?"
            @ok="onDelete"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                This cannot be undone.
            </p>
        </b-modal>
        <b-modal
            ok-only
            :body-bg-variant="profile.darkMode ? 'dark' : 'light'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'light'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'light'"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :body-text-variant="profile.darkMode ? 'white' : 'dark'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
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
                v-if="fileIsImage(thumbnailName)"
                center
                :src="thumbnailUrl"
                style="width: 68rem"
                @load="thumbnailLoaded"
                v-show="thumbnailDoneLoading"
            >
            </b-img>
            <b-embed
                @load="thumbnailLoaded"
                v-else-if="fileIsText(thumbnailName)"
                type="iframe"
                :src="thumbnailUrl"
            ></b-embed>
        </b-modal>
    </div>
</template>
<script>
import WorkflowBlurb from '@/components/workflow-blurb.vue';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

export default {
    name: 'run',
    components: {
        WorkflowBlurb
    },
    data() {
        return {
            textContent: [],
            currentCarouselSlide: 0,
            viewMode: 'List',
            resultSearchText: '',
            downloading: false,
            resubmitted: false,
            cancelled: false,
            // run status constants
            PENDING: 'PENDING',
            STARTED: 'STARTED',
            SUCCESS: 'SUCCESS',
            FAILURE: 'FAILURE',
            REVOKED: 'REVOKED',
            // user data
            userData: null,
            // run
            loadingRun: true,
            // walltime
            walltimeTotal: null,
            runtimeUpdateInterval: null,
            // output files
            loadingOutputFiles: false,
            outputFiles: [],
            outputFilePage: 1,
            outputPageSize: 10,
            // thumbnail view
            loadingThumbnail: true,
            thumbnailName: '',
            thumbnailUrl: '',
            thumbnailTitle: '',
            thumbnailDoneLoading: false,
            // alerts
            canceledAlertMessage: '',
            showCanceledAlert: false,
            showFailedToCancelAlert: false,
            // the "v-if hack" (https://michaelnthiessen.com/force-re-render/)
            render: true
        };
    },
    methods: {
        thumbnailFor(path) {
            let i = this.outputFiles.findIndex(f => f.path === path);
            if (
                this.viewMode === 'Grid' &&
                i >= (this.outputFilePage - 1) * this.outputPageSize &&
                i <= this.outputFilePage * this.outputPageSize
            )
                return `/apis/v1/runs/${this.$router.currentRoute.params.id}/thumbnail/?path=${path}`;
            else return null;
        },
        prettifyShort: function(date) {
            return `${moment(date).fromNow()}`;
        },
        fileIsImage(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'png' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpg' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpeg' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'czi'
            );
        },
        fileIsText(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'txt' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'csv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'tsv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yaml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'log' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'out' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'err'
            );
        },
        fileIs3dModel(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'ply'
            );
        },
        renderPreview(f) {
            if (!f.name.endsWith('ply')) return;
            var camera = new THREE.PerspectiveCamera(
                35,
                window.innerWidth / window.innerHeight,
                1,
                15
            );
            // camera.position.set(3, 0.15, 3);
            camera.position.z = 2;
            camera.zoom = 0.5;

            var cameraTarget = new THREE.Vector3(0, -0.1, 0);

            var scene = new THREE.Scene();
            // scene.background = new THREE.Color(0x72645b);
            scene.fog = new THREE.Fog(0x72645b, 2, 15);

            const loader = new PLYLoader();
            var comp = this;
            loader.load(
                `/apis/v1/runs/${this.$router.currentRoute.params.id}/thumbnail/?path=${f.name}`,
                function(geometry) {
                    geometry.computeVertexNormals();

                    // const material = new THREE.MeshStandardMaterial({
                    //     color: 0x0055ff,
                    //     flatShading: true
                    // });
                    const material = new THREE.PointsMaterial({
                        // color: 0x0055ff,
                        size: 0.005,
                        vertexColors: THREE.VertexColors
                    });
                    const mesh = new THREE.Points(geometry, material);
                    //const mesh = new THREE.Mesh(geometry, material);
                    // const mesh = new THREE.Mesh(geometry);

                    mesh.position.y = -0.3;
                    // mesh.position.z = 0.3;
                    mesh.rotation.x = -Math.PI / 2;
                    mesh.scale.multiplyScalar(0.5);

                    mesh.castShadow = true;
                    mesh.receiveShadow = true;

                    comp.currentModel.geometry = geometry;
                    comp.currentModel.material = material;
                    comp.currentModel.mesh = mesh;

                    scene.add(mesh);
                }
            );

            // Lights

            scene.add(new THREE.HemisphereLight(0x443333, 0x111122));

            var addShadowedLight = function(x, y, z, color, intensity) {
                const directionalLight = new THREE.DirectionalLight(
                    color,
                    intensity
                );
                directionalLight.position.set(x, y, z);
                scene.add(directionalLight);

                directionalLight.castShadow = true;

                const d = 1;
                directionalLight.shadow.camera.left = -d;
                directionalLight.shadow.camera.right = d;
                directionalLight.shadow.camera.top = d;
                directionalLight.shadow.camera.bottom = -d;

                directionalLight.shadow.camera.near = 1;
                directionalLight.shadow.camera.far = 4;

                directionalLight.shadow.mapSize.width = 1024;
                directionalLight.shadow.mapSize.height = 1024;

                directionalLight.shadow.bias = -0.001;
            };

            var onWindowResize = function() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();

                renderer.setSize(window.innerWidth, window.innerHeight);
            };

            var animate = function() {
                requestAnimationFrame(animate);
                render();
            };

            var render = function() {
                // const timer = Date.now() * 0.00005;

                // camera.position.x = Math.sin(timer) * 2.5;
                // camera.position.z = Math.cos(timer) * 2.5;

                camera.lookAt(cameraTarget);

                renderer.render(scene, camera);
            };

            addShadowedLight(1, 1, 1, 0xffffff, 1.35);
            // addShadowedLight(0.5, 1, -1, 0xffaa00, 1);

            // renderer

            var renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.outputEncoding = THREE.sRGBEncoding;

            renderer.shadowMap.enabled = true;

            const controls = new OrbitControls(camera, renderer.domElement);
            controls.enableZoom = false;
            controls.target.set(0, 25, 0);
            controls.update();

            // resize

            window.addEventListener('resize', onWindowResize);
            document.getElementById(f.id).innerHTML = '';
            document.getElementById(f.id).prepend(renderer.domElement);
            //.appendChild(renderer.domElement);

            this.currentModel.scene = scene;
            this.currentModel.loader = loader;
            this.currentModel.renderer = renderer;
            this.currentModel.id = f.id;

            animate();
        },
        unrenderPreview() {
            this.currentModel.scene.remove(this.currentModel.mesh);
            this.currentModel.renderer.dispose();
            this.currentModel.renderer.renderLists.dispose();
            // this.currentModel.loader.dispose();
            this.currentModel.geometry.dispose();
            this.currentModel.material.dispose();
        },
        setViewMode(mode) {
            this.viewMode = mode;
        },
        refreshRun() {
            this.$store.dispatch('load', this.$router.currentRoute.params.id);
        },
        onCancel() {
            this.cancelled = true;
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/cancel/`
                )
                .then(response => {
                    this.cancelled = false;
                    if (response.status === 200) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                    } else {
                        this.showFailedToCancelAlert = true;
                    }
                })
                .catch(error => {
                    this.cancelled = false;
                    Sentry.captureException(error);
                    return error;
                });
        },
        onDelete() {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/delete/`
                )
                .then(response => {
                    if (response.status === 200 && response.data.deleted) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                        this.$store.dispatch('loadRuns');
                        router.push({
                            name: 'user',
                            params: {
                                username: this.profile.djangoProfile.username
                            }
                        });
                    } else {
                        this.showFailedToDeleteAlert = true;
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        showDeletePrompt() {
            this.$bvModal.show('delete');
        },
        onRestart() {
            this.resubmitted = true;
            let config = this.workflowsRecentlyRun[this.workflowKey]; // retrieve workflow config

            // resubmit run
            axios({
                method: 'post',
                url: `/apis/v1/runs/`,
                data: {
                    repo: this.getWorkflow.repo,
                    config: config,
                    type: 'Now',
                    delete: false
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    this.resubmitted = false;
                    router.push({
                        name: 'run',
                        params: {
                            username: this.profile.djangoProfile.username,
                            id: response.data.id
                        }
                    });
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.resubmitted = false;
                    throw error;
                });
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        parseSeconds(seconds) {
            return moment.utc(seconds * 1000);
        },
        setOutputFilesPageSize(size) {
            this.outputPageSize = size;
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
            this.thumbnailName = file;
            this.thumbnailUrl = `/apis/v1/runs/${this.$router.currentRoute.params.id}/thumbnail/?path=${file}`;
            this.thumbnailTitle = file;
            this.$bvModal.show('thumbnail');
        },
        downloadFile(file) {
            this.downloading = true;
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
                    this.downloading = false;
                    return error;
                });
        },
        downloadSubmissionLogs() {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/submission_logs/`
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
                    link.setAttribute('download', this.submissionLogFileName);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        downloadContainerLogs() {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/container_logs/`
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
                    link.setAttribute('download', this.containerLogFileName);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        async reloadOutputFiles() {
            this.loadingOutputFiles = true;
            await axios
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
        getTextFile(file) {
            if (!this.fileIsText(file.name)) return;
            this.textContent = [];
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/file_text/?path=${file.path}`
                )
                .then(response => {
                    if (response.status === 200) {
                        this.textContent = response.data.text;
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        }
    },
    async mounted() {
        this.loadingRun = true;
        await this.$store.dispatch(
            'runs/refresh',
            this.$router.currentRoute.params.id
        );
        this.loadingRun = false;
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['workflow', 'workflowsRecentlyRun']),
        ...mapGetters('runs', ['run', 'runs', 'runsLoading']),
        filteredResults() {
            return this.outputFiles
                .slice(
                    (this.outputFilePage - 1) * this.outputPageSize,
                    this.outputFilePage * this.outputPageSize
                )
                .filter(f => f.name.includes(this.resultSearchText));
        },
        workflowKey() {
            return `${this.getWorkflow.repo.owner.login}/${this.getWorkflow.repo.name}`;
        },
        getRun() {
            let run = this.run(this.$router.currentRoute.params.id);
            if (run !== undefined) {
                if (run.is_complete) this.reloadOutputFiles();
                return run;
            }
            return null;
        },
        submissionLogs() {
            let all = this.getRun.submission_logs.slice();
            var firstI = all.findIndex(l => l.includes('PENDING'));
            if (firstI === -1)
                firstI = all.findIndex(l => l.includes('RUNNING'));
            if (firstI === -1) return all;
            all.reverse();
            let lastI =
                all.length - all.findIndex(l => l.includes('RUNNING')) - 1;
            all.reverse();
            if (lastI === -1) return all;
            if (lastI === all.length - 1) return all;
            else if (this.getRun.is_complete)
                all.splice(firstI, lastI - firstI + 1);
            else all.splice(firstI, lastI - firstI + 1, all[lastI]);
            return all;
        },
        runNotFound() {
            return this.getRun === null && !this.loadingRun;
        },
        getWorkflow() {
            return this.workflow(
                this.getRun.workflow_owner,
                this.getRun.workflow_name
            );
        },
        submissionLogFileName() {
            return `${this.$router.currentRoute.params.id}.plantit.log`;
        },
        containerLogFileName() {
            return `${
                this.$router.currentRoute.params.id
            }.${this.getRun.cluster.toLowerCase()}.log`;
        }
    },
    watch: {
        async $route() {
            await this.$store.dispatch('runs/refresh', this.getRun);
            await this.reloadOutputFiles();
        },
        // async run(oldRun, newRun) {
        //     if (newRun.is_complete) await this.reloadOutputFiles();
        // },
        '$route.params.id'() {
            // need to watch for route change to prompt reload
        },
        viewMode() {
            if (
                this.data !== null &&
                this.outputFiles.some(f => f.name.endsWith('ply'))
            ) {
                this.unrenderPreview();
                if (this.viewMode === 'Carousel')
                    if (this.currentCarouselSlide === 0)
                        this.renderPreview(this.outputFiles[0]);
            }

            if (
                this.viewMode === 'Carousel' &&
                this.textContent.length === 0 &&
                this.outputFiles.length > 0
            )
                this.getTextFile(this.outputFiles[0]);
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
