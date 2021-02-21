<template>
    <div
        v-if="render"
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
                                variant="secondary"
                            ></b-spinner>
                        </b-row>
                        <div v-else-if="flow.config">
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
                                        Failed to cancel run {{ run.id }}.
                                    </b-alert>
                                </b-col>
                            </b-row>
                            <b-row class="m-0 p-0">
                                <b-col align-self="end" class="m-0 p-0">
                                    <h4>
                                        <b-badge
                                            :variant="
                                                run.is_failure ||
                                                run.is_timeout ||
                                                run.is_cancelled
                                                    ? 'danger'
                                                    : run.is_success
                                                    ? 'success'
                                                    : 'warning'
                                            "
                                            class="mr-2"
                                            >{{ run.job_status }}</b-badge
                                        >
                                        <b-badge
                                            v-for="tag in run.tags"
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
                                            darkMode
                                                ? 'theme-dark'
                                                : 'theme-light'
                                        "
                                    >
                                        <b-spinner
                                            class="mb-1 mr-1"
                                            small
                                            v-if="!run.is_complete"
                                            variant="secondary"
                                        >
                                        </b-spinner>
                                        <b class="ml-1 mr-0">{{ run.id }}</b>
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
                                        <b class="mr-0">{{ run.target }}</b>
                                    </h5>
                                </b-col>
                                <b-col
                                    md="auto"
                                    align-self="center"
                                    class="mb-2"
                                    ><small>
                                        Last updated {{ prettify(run.updated) }}
                                    </small></b-col
                                >
                                <b-col
                                    v-if="run.is_complete"
                                    md="auto"
                                    class="m-0 mb-2"
                                    align-self="start"
                                >
                                    <b-button
                                        :variant="
                                            darkMode ? 'outline-light' : 'white'
                                        "
                                        size="sm"
                                        v-b-tooltip.hover
                                        :title="'Restart ' + flow.config.name"
                                        @click="onRestart"
                                    >
                                        <i class="fas fa-level-up-alt"></i>
                                        Restart
                                    </b-button>
                                </b-col>
                                <b-col
                                    v-if="!run.is_complete"
                                    md="auto"
                                    class="m-0 mb-2"
                                    align-self="start"
                                >
                                    <b-button
                                        variant="outline-danger"
                                        size="sm"
                                        v-b-tooltip.hover
                                        title="Cancel Run"
                                        @click="onCancel"
                                    >
                                        <i class="fas fa-times"></i>
                                        Cancel
                                    </b-button>
                                </b-col>
                                <b-col
                                    md="auto"
                                    class="m-0 mb-2"
                                    align-self="start"
                                >
                                    <b-button
                                        :variant="
                                            darkMode ? 'outline-light' : 'white'
                                        "
                                        size="sm"
                                        v-b-tooltip.hover
                                        title="Refresh Run"
                                        @click="reloadRun(true)"
                                    >
                                        <i class="fas fa-redo"></i>
                                        Refresh
                                    </b-button>
                                </b-col>
                            </b-row>
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
                                    <b-row class="m-0 p-0 mt-3">
                                        <b-col class="m-0 p-0">
                                            <b-tabs
                                                pills
                                                card
                                                vertical
                                                nav-class="bg-transparent"
                                                active-nav-item-class="bg-secondary text-dark"
                                                fill
                                            >
                                                <b-tab
                                                    title="Logs"
                                                    active
                                                    :title-link-class="
                                                        darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                    :class="
                                                        darkMode
                                                            ? 'theme-container-dark m-0 p-3'
                                                            : 'theme-container-light m-0 p-3'
                                                    "
                                                    ><template #title
                                                        >Logs
                                                    </template>
                                                    <div
                                                        :class="
                                                            darkMode
                                                                ? 'theme-container-dark m-0 p-0'
                                                                : 'theme-container-light m-0 p-0'
                                                        "
                                                    >
                                                        <b-row
                                                            class="m-0"
                                                            style="border-bottom: 1px solid lightgray"
                                                        >
                                                            <b-col
                                                                align-self="end"
                                                                class="mb-2"
                                                            >
                                                                <h5
                                                                    :class="
                                                                        darkMode
                                                                            ? 'text-white'
                                                                            : 'text-dark'
                                                                    "
                                                                    style="font-family: 'Monaco', 'Menlo', 'Courier New', monospace; font-size: 15px"
                                                                >
                                                                    <b
                                                                        >Status
                                                                        Logs</b
                                                                    >
                                                                </h5>
                                                            </b-col>
                                                            <b-col
                                                                md="auto"
                                                                align-self="end"
                                                                class="mb-2"
                                                            >
                                                                <h5
                                                                    :class="
                                                                        darkMode
                                                                            ? 'text-white'
                                                                            : 'text-dark'
                                                                    "
                                                                    style="font-family: 'Monaco', 'Menlo', 'Courier New', monospace; font-size: 15px"
                                                                >
                                                                    <b
                                                                        >Container
                                                                        Logs</b
                                                                    >
                                                                </h5>
                                                            </b-col>
                                                        </b-row>
                                                        <div>
                                                            <b-row
                                                                align-h="center"
                                                                v-if="
                                                                    loadingRun
                                                                "
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
                                                                        run
                                                                            .submission_logs
                                                                            .length >
                                                                            0
                                                                    "
                                                                    class="m-0 p-0 pl-3 pr-3"
                                                                    style="white-space: pre-line;"
                                                                >
                                                                    {{
                                                                        run.submission_logs
                                                                    }}
                                                                    <!--<small
                                                                        v-for="log in statusList"
                                                                        v-bind:key="
                                                                            log.timestamp
                                                                        "
                                                                        >{{
                                                                            log.description
                                                                        }}<br
                                                                    /></small>-->
                                                                </b-col>
                                                                <b-col
                                                                    v-if="
                                                                        run
                                                                            .container_logs
                                                                            .length >
                                                                            0
                                                                    "
                                                                    class="pl-3 pr-3 pb-1 text-right"
                                                                    style="white-space: pre-line;"
                                                                >
                                                                    {{
                                                                        run.container_logs
                                                                    }}
                                                                </b-col>
                                                            </b-row>
                                                        </div>
                                                    </div>
                                                </b-tab>
                                                <b-tab
                                                    title="Outputs"
                                                    class="m-0 p-3"
                                                    :title-link-class="
                                                        darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                    ><template #title>
                                                        Outputs
                                                        <span
                                                            v-if="
                                                                !loadingOutputFiles
                                                            "
                                                            >({{
                                                                outputFiles.length
                                                            }})</span
                                                        >
                                                    </template>
                                                    <div class="mt-0 pt-0">
                                                        <b-row
                                                            v-if="
                                                                flow.config &&
                                                                    flow.config
                                                                        .output
                                                            "
                                                            align-h="center"
                                                            align-v="center"
                                                            class="mt-2 text-center"
                                                        >
                                                            <b-col>
                                                                Output files
                                                                expected:
                                                            </b-col>
                                                        </b-row>
                                                        <b-row
                                                            v-if="
                                                                flow.config &&
                                                                    flow.config
                                                                        .output
                                                            "
                                                            align-h="center"
                                                            align-v="center"
                                                            class="text-center"
                                                        >
                                                            <b-col>
                                                                <b
                                                                    ><code
                                                                        :class="
                                                                            darkMode
                                                                                ? 'theme-dark'
                                                                                : 'theme-light'
                                                                        "
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
                                                                                        )
                                                                                      : []) +
                                                                                  (flow
                                                                                      .config
                                                                                      .output
                                                                                      .include
                                                                                      .names
                                                                                      ? ', ' +
                                                                                        flow.config.output.include.names.join(
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
                                                                                        )
                                                                                      : []) +
                                                                                  (flow
                                                                                      .config
                                                                                      .output
                                                                                      .exclude
                                                                                      .names
                                                                                      ? ', ' +
                                                                                        flow.config.output.exclude.names.join(
                                                                                            ', '
                                                                                        )
                                                                                      : [])
                                                                                : ''
                                                                        }}
                                                                    </code></b
                                                                >
                                                            </b-col>
                                                            <br />
                                                            <br />
                                                        </b-row>
                                                        <b-row>
                                                            <b-col>
                                                                <b-pagination
                                                                    v-model="
                                                                        outputFilePage
                                                                    "
                                                                    pills
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
                                                                        <i
                                                                            v-else
                                                                            >{{
                                                                                page
                                                                            }}</i
                                                                        >
                                                                    </template>
                                                                </b-pagination>
                                                            </b-col>
                                                            <b-col
                                                                md="auto"
                                                                align-self="middle"
                                                            >
                                                                <b-dropdown
                                                                    class="m-2"
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
                                                                        darkMode
                                                                            ? 'outline-light'
                                                                            : 'white'
                                                                    "
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
                                                            </b-col>
                                                        </b-row>
                                                        <b-row
                                                            class="pl-1 pr-1 pb-1"
                                                            align-h="center"
                                                            v-if="
                                                                loadingOutputFiles
                                                            "
                                                        >
                                                            <b-spinner
                                                                type="grow"
                                                                label="Loading..."
                                                                variant="secondary"
                                                            ></b-spinner>
                                                        </b-row>
                                                        <b-row
                                                            v-else
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
                                                                align-self="end"
                                                                class="text-left"
                                                                style="position: relative; top: -5px; left: -40px"
                                                            >
                                                                <b-spinner
                                                                    class="m-0 p-0"
                                                                    v-if="
                                                                        !file.exists &&
                                                                            !run.is_complete
                                                                    "
                                                                    type="grow"
                                                                    small
                                                                    variant="warning"
                                                                ></b-spinner>
                                                                <i
                                                                    v-else-if="
                                                                        !file.exists &&
                                                                            run.is_complete
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
                                                                                file.name
                                                                            ) &&
                                                                                !fileIsText(
                                                                                    file.name
                                                                                ))
                                                                    "
                                                                    :variant="
                                                                        darkMode
                                                                            ? 'outline-light'
                                                                            : 'white'
                                                                    "
                                                                    size="sm"
                                                                    v-b-tooltip.hover
                                                                    :title="
                                                                        'View ' +
                                                                            file.name
                                                                    "
                                                                    @click="
                                                                        viewFile(
                                                                            file.name
                                                                        )
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
                                                                    :disabled="
                                                                        !file.exists
                                                                    "
                                                                    :variant="
                                                                        darkMode
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
                                                                run.is_complete
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
                                                </b-tab>
                                            </b-tabs>
                                        </b-col>
                                    </b-row>

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
import WorkflowBlurb from '@/components/flow-blurb.vue';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';

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
            // flow
            flow: null,
            // run
            loadingRun: true,
            run: null,
            runNotFound: false,
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
            render: true,
            // websocket
            socket: null
        };
    },
    methods: {
        subscribeToSocket(e) {
            let data = JSON.parse(e.data);
            this.run = data.run;
        },
        onCancel() {
            axios
                .get(
                    `/apis/v1/runs/${this.$router.currentRoute.params.id}/cancel/`
                )
                .then(response => {
                    if (response.status === 200) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                    } else {
                        this.showFailedToCancelAlert = true;
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        onRestart() {
            // retrieve config
            let config = this.flowConfigs[this.flowKey];

            // resubmit run
            axios({
                method: 'post',
                url: `/apis/v1/runs/`,
                data: {
                    repo: this.flow.repo,
                    config: config
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    router.push({
                        name: 'run',
                        params: {
                            username: this.profile.djangoProfile.username,
                            id: response.data.id
                        }
                    });
                    location.reload();
                    this.reloadRun();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
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
                    .pop() === 'jpeg'
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
        listOutputFiles() {
            return this.outputFiles.slice(
                (this.outputFilePage - 1) * this.outputPageSize,
                this.outputFilePage * this.outputPageSize
            );
        },
        setOutputFilesPageSize(size) {
            this.outputPageSize = size;
        },
        reloadRun() {
            this.render = false;
            this.$nextTick(() => {
                this.render = true;
            });

            this.loadingRun = true;
            this.showCanceledAlert = false;
            this.showFailedToCancelAlert = false;
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
                    this.reloadOutputFiles();
                    this.loadFlow(
                        response.data.flow_owner,
                        response.data.flow_name
                    );
                    axios
                        .get(
                            `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/${this.profile.djangoProfile.username}/`,
                            {
                                headers: {
                                    Authorization:
                                        'Bearer ' +
                                        this.profile.djangoProfile.profile
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
        }
    },
    async mounted() {
        this.socket = new WebSocket(
            (location.protocol === 'https:' ? 'wss://' : 'ws://') +
                window.location.host +
                '/ws/run/' +
                this.$router.currentRoute.params.id +
                '/'
        );
        this.socket.onmessage = this.subscribeToSocket;
        await this.reloadRun();
    },
    computed: {
        flowKey() {
            return `${this.flow.repo.owner.login}/${this.flow.repo.name}`;
        },
        submissionLogFileName() {
            return `${this.$router.currentRoute.params.id}.plantit.log`;
        },
        containerLogFileName() {
            return `${
                this.$router.currentRoute.params.id
            }.${this.run.target.toLowerCase()}.log`;
        },
        ...mapGetters(['profile', 'loggedIn', 'flowConfigs', 'darkMode']),
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
