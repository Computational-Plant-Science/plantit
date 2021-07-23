<template>
    <div>
        <b-container class="p-2 vl" fluid>
            <b-row v-if="tasksLoading">
                <b-col>
                    <b-spinner
                        small
                        v-if="tasksLoading"
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading task...</span
                    >
                </b-col>
            </b-row>
            <b-row align-content="center" v-else-if="notFound">
                <b-col class="text-center">
                    <p class="text-danger">
                        <i class="fas fa-exclamation-circle fa-3x fa-fw"></i>
                        <br />
                        <br />
                        This task does not exist.
                    </p>
                </b-col>
            </b-row>
            <b-row v-else-if="getTask.cleaned_up" align-content="center">
                <b-col>
                    <h6 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                        <i class="fas fa-broom fa-1x fa-fw"></i> This task has
                        been cleaned up.
                    </h6>
                </b-col>
            </b-row>
            <b-row v-else>
                <b-col>
                    <b-row align-h="center" v-if="tasksLoading">
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
                                    @dismissed="showFailedToCancelAlert = false"
                                >
                                    Failed to cancel task {{ getTask.name }}.
                                </b-alert>
                            </b-col>
                        </b-row>
                        <b-row class="m-0 p-0">
                            <b-col md="auto" align-self="end" class="m-0 p-0">
                                <h3
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    <i class="fas fa-tasks fa-fw"></i>
                                    {{ getTask.name }}
                                </h3></b-col
                            ><b-col class="m-0 ml-2 p-0">
                                <h5>
                                    <b-badge
                                        v-for="tag in getTask.tags"
                                        v-bind:key="tag"
                                        class="mr-2"
                                        variant="secondary"
                                        >{{ tag }}</b-badge
                                    ><span v-if="getTask.project !== null"
                                        ><b-badge class="mr-2" variant="info">{{
                                            getTask.project.title
                                        }}</b-badge
                                        ><small v-if="getTask.study !== null"
                                            ><b-badge
                                                class="mr-2"
                                                variant="info"
                                                >{{
                                                    getTask.study.title
                                                }}</b-badge
                                            ></small
                                        ></span
                                    >
                                </h5>
                            </b-col>
                        </b-row>
                        <!--<b-row v-if="getTask.project !== null"
                            ><b-col md="auto"
                                ><h5>
                                    <b-badge class="mr-2" variant="info">{{
                                        getTask.project.title
                                    }}</b-badge
                                    ><small v-if="getTask.study !== null"
                                        ><b-badge class="mr-2" variant="info">{{
                                            getTask.study.title
                                        }}</b-badge></small
                                    >
                                </h5></b-col
                            ></b-row
                        >-->
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
                                        v-if="!getTask.is_complete"
                                        variant="warning"
                                    >
                                    </b-spinner>
                                    <b-badge
                                        :variant="
                                            getTask.is_failure ||
                                            getTask.is_timeout
                                                ? 'danger'
                                                : getTask.is_success
                                                ? 'success'
                                                : getTask.is_cancelled
                                                ? 'secondary'
                                                : 'warning'
                                        "
                                        >{{
                                            getTask.status.toUpperCase()
                                        }}</b-badge
                                    >
                                    <small> on </small>
                                    <b-link
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        :to="{
                                            name: 'agent',
                                            params: {
                                                name: getTask.agent.name
                                            }
                                        }"
                                        >{{
                                            getTask.agent
                                                ? getTask.agent.name
                                                : '[agent removed]'
                                        }}</b-link
                                    >
                                </h5>
                            </b-col>
                            <b-col
                                md="auto"
                                class="m-0 mb-2"
                                align-self="start"
                            >
                                <b-button
                                    :disabled="canceled"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    :title="
                                        `${getTask.guid} (click to copy to clipboard)`
                                    "
                                    @click="copyGUID"
                                    ><i class="fas fa-copy fa-fw"></i
                                    >GUID</b-button
                                >
                            </b-col>
                            <b-col
                                v-if="
                                    getTask.is_complete && getTask.can_restart
                                "
                                md="auto"
                                class="m-0 mb-2"
                                align-self="start"
                            >
                                <b-button
                                    :disabled="restarted"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    :title="'Restart this task'"
                                    @click="restart"
                                >
                                    <i class="fas fa-level-up-alt fa-fw"></i
                                    >Restart
                                    <b-spinner
                                        small
                                        v-if="restarted"
                                        label="Loading..."
                                        :variant="
                                            profile.darkMode ? 'light' : 'dark'
                                        "
                                        style="width: 0.7rem; height: 0.7rem;"
                                    ></b-spinner>
                                </b-button>
                            </b-col>
                            <b-col
                                v-if="!getTask.is_complete"
                                md="auto"
                                class="m-0 mb-2"
                                align-self="start"
                            >
                                <b-button
                                    :disabled="canceled"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    title="Cancel Run"
                                    @click="cancel"
                                >
                                    <i class="fas fa-times fa-fw"></i>
                                    Cancel<b-spinner
                                        small
                                        v-if="canceled"
                                        label="Loading..."
                                        :variant="
                                            profile.darkMode ? 'light' : 'dark'
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
                                    v-if="getTask.is_complete"
                                    :disabled="tasksLoading"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    title="Refresh Run"
                                    @click="refresh"
                                >
                                    <i class="fas fa-redo"></i>
                                    Refresh
                                    <b-spinner
                                        small
                                        v-if="tasksLoading"
                                        label="Loading..."
                                        :variant="
                                            profile.darkMode ? 'light' : 'dark'
                                        "
                                        class="ml-2 mb-1"
                                    ></b-spinner>
                                </b-button>
                            </b-col>
                            <!--<b-col
                                v-if="getTask.is_complete"
                                md="auto"
                                class="m-0 mb-2"
                                align-self="start"
                            >
                                <b-button
                                    variant="outline-danger"
                                    size="sm"
                                    v-b-tooltip.hover
                                    title="Delete Task"
                                    @click="showDeletePrompt"
                                >
                                    <i class="fas fa-trash"></i>
                                    Delete
                                </b-button>
                            </b-col>-->
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
                                            :linkable="true"
                                            :workflow="getWorkflow"
                                        ></WorkflowBlurb>
                                    </b-card-body>
                                </b-card>
                                <b-row class="m-0 p-0 mt-1">
                                    <b-col class="m-0 p-0 text-center">
                                        <small>
                                            Created
                                            {{ prettify(getTask.created) }}
                                        </small>
                                    </b-col>
                                    <b-col
                                        class="m-0 p-0 text-center"
                                        v-if="!getTask.is_complete"
                                    >
                                        <small>
                                            Last updated
                                            {{ prettify(getTask.updated) }}
                                        </small>
                                    </b-col>
                                    <b-col class="m-0 p-0 text-center">
                                        <small v-if="getTask.is_complete"
                                            >Completed
                                            {{
                                                prettify(getTask.completed)
                                            }}</small
                                        >
                                        <small v-else>
                                            Due
                                            {{ prettify(getTask.due_time) }}
                                        </small>
                                    </b-col>
                                    <b-col
                                        v-if="
                                            getTask.is_complete &&
                                                getTask.cleanup_time !== null
                                        "
                                        ><small
                                            >Cleaning up
                                            {{
                                                prettify(getTask.cleanup_time)
                                            }}</small
                                        ></b-col
                                    >
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
                                                    v-if="tasksLoading"
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
                                                            getTask.task_logs
                                                                .length > 0
                                                        "
                                                        class="m-0 p-0 pl-3 pr-3 pt-1"
                                                        style="white-space: pre-line;"
                                                    >
                                                        <span
                                                            v-for="line in taskLogs"
                                                            v-bind:key="line"
                                                            v-show="
                                                                line !==
                                                                    undefined &&
                                                                    line !==
                                                                        null
                                                            "
                                                            >{{
                                                                line + '\n'
                                                            }}</span
                                                        >
                                                    </b-col>
                                                    <b-col v-else
                                                        ><b-skeleton-wrapper
                                                            :loading="
                                                                !getTask.is_complete
                                                            "
                                                        >
                                                            <template #loading>
                                                                <b-skeleton
                                                                    width="15%"
                                                                ></b-skeleton
                                                                ><b-skeleton
                                                                    width="25%"
                                                                ></b-skeleton
                                                                ><b-skeleton
                                                                    width="20%"
                                                                ></b-skeleton></template></b-skeleton-wrapper
                                                    ></b-col>
                                                </b-row>
                                            </div>
                                        </div>
                                        <div
                                            class="m-3"
                                            v-if="
                                                getTask.is_complete &&
                                                    getTask.output_files !==
                                                        undefined
                                            "
                                        >
                                            <b-row
                                                align-h="center"
                                                align-v="center"
                                                class="mt-2"
                                            >
                                                <b-col class="text-left">
                                                    <span
                                                        v-if="
                                                            task.results_retrieved
                                                        "
                                                        >{{
                                                            getTask.output_files
                                                                .length
                                                        }}</span
                                                    ><span v-else><b-spinner small :variant="profile.darkMode ? 'light' : 'dark'"></b-spinner> Loading</span>
                                                  result(s)
                                                    <br />
                                                    <b
                                                        v-if="
                                                            getWorkflow.config
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
                                                                    .output.path
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
                                                                    `, ${getTask.name}.zip`
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
                                                    v-if="
                                                        getWorkflow.config
                                                            .output
                                                    "
                                                >
                                                    <b-button
                                                        title="Transfer results to CyVerse Data Store"
                                                        :disabled="
                                                            transferring ||
                                                                getTask.transferred
                                                        "
                                                        v-b-tooltip.hover
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'outline-light'
                                                                : 'white'
                                                        "
                                                        @click="
                                                            showTransferToCyVerseModal
                                                        "
                                                        ><i
                                                            v-if="
                                                                !transferring &&
                                                                    !getTask.transferred
                                                            "
                                                            class="fas fa-upload fa-fw mr-1"
                                                        ></i
                                                        ><i
                                                            v-else-if="
                                                                transferring &&
                                                                    !getTask.transferred
                                                            "
                                                            class="fas fa-spinner fa-fw mr-1"
                                                        ></i>
                                                        <i
                                                            v-else
                                                            class="fas fa-check fa-fw mr-1"
                                                        ></i>
                                                        {{
                                                            getTask.transferred
                                                                ? 'Transferred'
                                                                : transferring
                                                                ? 'Transferring'
                                                                : 'Transfer'
                                                        }}
                                                        to
                                                        <b-img
                                                            class="ml-2 mt-1"
                                                            rounded
                                                            style="max-height: 1.1rem;"
                                                            right
                                                            :src="
                                                                require('../../assets/logos/cyverse_bright.png')
                                                            "
                                                        ></b-img
                                                    ></b-button>
                                                </b-col>
                                                <b-col
                                                    md="auto"
                                                    align-self="end"
                                                >
                                                    <b-dropdown
                                                        :disabled="
                                                            getTask.output_files !==
                                                                undefined &&
                                                                getTask.output_files !==
                                                                    null &&
                                                                getTask
                                                                    .output_files
                                                                    .length ===
                                                                    0
                                                        "
                                                        class="text-right"
                                                        :text="outputPageSize"
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
                                                            getTask.output_files !==
                                                                undefined &&
                                                                getTask.output_files !==
                                                                    null &&
                                                                getTask
                                                                    .output_files
                                                                    .length ===
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
                                                v-show="viewMode !== 'Carousel'"
                                            >
                                                <b-col
                                                    md="auto"
                                                    align-self="end"
                                                >
                                                    <b-pagination
                                                        v-model="outputFilePage"
                                                        pills
                                                        class="mt-3"
                                                        size="md"
                                                        :total-rows="
                                                            getTask.output_files
                                                                .length
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
                                                            <b v-if="active">{{
                                                                page
                                                            }}</b>
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
                                                            viewMode === 'List'
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
                                                                            !getTask.is_complete
                                                                    "
                                                                    type="grow"
                                                                    small
                                                                    variant="warning"
                                                                ></b-spinner>
                                                                <i
                                                                    v-else-if="
                                                                        !file.exists &&
                                                                            getTask.is_complete
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
                                                                        preDownloadFile(
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
                                                            viewMode === 'Grid'
                                                        "
                                                        columns
                                                    >
                                                        <b-card
                                                            v-for="file in filteredResults"
                                                            v-bind:key="
                                                                file.name
                                                            "
                                                            style="min-width: 20rem;"
                                                            no-body
                                                            class="overflow-hidden mb-4 mr-4 p-0 text-left border-0"
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
                                                            <b-card-img
                                                                v-if="
                                                                    viewMode ===
                                                                        'Grid'
                                                                "
                                                                :style="
                                                                    getTask.result_previews_loaded ||
                                                                    noPreview(
                                                                        file
                                                                    )
                                                                        ? 'min-width: 20rem'
                                                                        : 'max-width: 4rem'
                                                                "
                                                                :src="
                                                                    thumbnailPath(
                                                                        file
                                                                    )
                                                                "
                                                                top
                                                            ></b-card-img>
                                                            <!--<template #header
                                                                ><b-img-lazy
                                                                    center
                                                                    v-if="
                                                                        viewMode ===
                                                                            'Grid'
                                                                    "
                                                                    fluid-grow
                                                                    :style="
                                                                        getTask.result_previews_loaded ||
                                                                        noPreview(
                                                                            file
                                                                        )
                                                                            ? 'min-width: 20rem'
                                                                            : 'max-width: 4rem'
                                                                    "
                                                                    :src="
                                                                        thumbnailPath(
                                                                            file
                                                                        )
                                                                    "
                                                                ></b-img-lazy
                                                            ></template>-->
                                                            <b-card-body class="text-center">
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
                                                                <b-button
                                                                    block
                                                                    :title="
                                                                        `Download ${file.name}`
                                                                    "
                                                                    v-b-tooltip.hover
                                                                    :variant="
                                                                        profile.darkMode
                                                                            ? 'outline-light'
                                                                            : 'white'
                                                                    "
                                                                    class="text-center m-0"
                                                                    @click="
                                                                        downloadFile(
                                                                            file.name
                                                                        )
                                                                    "
                                                                >
                                                                    <i
                                                                        class="fas fa-download fa-fw"
                                                                    ></i> Download
                                                                </b-button>
                                                            </b-card-body>
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
                                                                    getTask
                                                                        .output_files[
                                                                        slide
                                                                    ]
                                                                )
                                                        "
                                                        @sliding-end="
                                                            slide =>
                                                                renderPreview(
                                                                    getTask
                                                                        .output_files[
                                                                        slide
                                                                    ]
                                                                )
                                                        "
                                                    >
                                                        <b-carousel-slide
                                                            v-for="file in getTask.output_files"
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
                                                                        file.name
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
                                                                            require('../../assets/no_preview_thumbnail.png')
                                                                        "
                                                                    ></b-img></div
                                                            ></template>
                                                            <template #default
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
        </b-container>
        <b-modal
            id="remove"
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
            title="Delete this task?"
            @ok="remove"
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
        <b-modal
            id="authenticate"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="'Authenticate with ' + this.getTask.agent.name"
            @ok="transferToCyVerse"
            ok-variant="success"
        >
            <b-form-input
                v-model="authenticationUsername"
                type="text"
                placeholder="Your username"
                required
            ></b-form-input>
            <b-form-input
                v-model="authenticationPassword"
                type="password"
                placeholder="Your password"
                required
            ></b-form-input>
        </b-modal>
        <b-modal
            id="authenticate-download"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="'Authenticate with ' + this.getTask.agent.name"
            @ok="downloadFile"
            ok-variant="success"
        >
            <b-form-input
                v-model="authenticationUsername"
                type="text"
                placeholder="Your username"
                required
            ></b-form-input>
            <b-form-input
                v-model="authenticationPassword"
                type="password"
                placeholder="Your password"
                required
            ></b-form-input>
        </b-modal>
        <b-modal
            size="lg"
            id="transfer"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="`Transfer results to CyVerse`"
            hide-footer
        >
            <div v-if="!transferring">
                <p>
                    Select a directory to transfer result files to.
                </p>
                <datatree
                    select="directory"
                    :create="true"
                    :upload="false"
                    :download="false"
                    @selectNode="preTransferToCyVerse"
                    :node="personalDatasets"
                ></datatree>
            </div>
            <div v-else>
                <b-spinner
                    small
                    :variant="profile.darkMode ? 'light' : 'dark'"
                ></b-spinner>
                Transferring results to {{ transferringPath }}...
            </div>
        </b-modal>
    </div>
</template>

<script>
import datatree from '@/components/datasets/data-tree';
import WorkflowBlurb from '@/components/workflows/workflow-blurb.vue';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { guid } from '@/utils';

export default {
    name: 'task',
    components: {
        WorkflowBlurb,
        datatree
    },
    data() {
        return {
            textContent: [],
            currentModel: {},
            currentCarouselSlide: 0,
            viewMode: 'List',
            resultSearchText: '',
            // action flags
            downloading: false,
            restarted: false,
            canceled: false,
            // user data
            userData: null,
            // walltime
            walltimeTotal: null,
            runtimeUpdateInterval: null,
            // result files
            loadingOutputFiles: false,
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
            authenticationUsername: '',
            authenticationPassword: '',
            transferringPath: '',
            transferring: false
        };
    },
    methods: {
        showTransferToCyVerseModal() {
            this.$bvModal.show('transfer');
        },
        hideTransferToCyVerseModal() {
            this.$bvModal.hide('transfer');
        },
        showAuthenticateModal() {
            this.$bvModal.show('authenticate');
        },
        async preTransferToCyVerse(node) {
            this.transferringPath = node.path;
            if (this.mustAuthenticate) this.showAuthenticateModal();
            else await this.transferToCyVerse(node);
        },
        async transferToCyVerse() {
            this.transferring = true;
            let data = {
                path: this.transferringPath
            };
            if (this.mustAuthenticate)
                data['auth'] = {
                    username: this.authenticationUsername,
                    password: this.authenticationPassword
                };
            else
                data['auth'] = {
                    username: this.getTask.agent.user
                };
            await axios({
                method: 'post',
                data: data,
                url: `/apis/v1/tasks/${this.getTask.owner}/${this.getTask.name}/transfer/`
            })
                .then(async response => {
                    this.hideTransferToCyVerseModal();
                    this.transferred = true;
                    this.transferring = false;
                    await Promise.all([
                        this.$store.dispatch('tasks/update', response.data),
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Transferred results to ${this.transferringPath}`,
                            guid: guid().toString(),
                            time: moment().format()
                        })
                    ]);
                })
                .catch(async error => {
                    this.hideTransferToCyVerseModal();
                    this.transferring = false;
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to transfer results to ${this.transferringPath}`,
                        guid: guid().toString(),
                        time: moment().format()
                    });
                    throw error;
                });
        },
        copyGUID() {
            const el = document.createElement('textarea');
            el.value = this.getTask.guid;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            this.$bvToast.toast(`Copied task GUID to clipboard`, {
                autoHideDelay: 3000,
                appendToast: false,
                noCloseButton: true
            });
        },
        noPreview(file) {
            return (
                this.fileIs3dModel(file.name) ||
                (!this.fileIsText(file.name) && !this.fileIsImage(file.name))
            );
        },
        thumbnailPath(file) {
            if (this.noPreview(file))
                return require('../../assets/no_preview_thumbnail.png');
            else if (!this.getTask.result_previews_loaded)
                return require('../../assets/PlantITLoading.gif');
            else return this.thumbnailFor(file.path);
        },
        thumbnailFor(path) {
            let i = this.getTask.output_files.findIndex(f => f.path === path);
            if (
                this.viewMode === 'Grid' &&
                i >= (this.outputFilePage - 1) * this.outputPageSize &&
                i <= this.outputFilePage * this.outputPageSize
            )
                return `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/thumbnail/?path=${path}`;
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
            camera.position.set(3, 0.15, 3);
            camera.position.z = 2;
            camera.zoom = 0.5;

            var cameraTarget = new THREE.Vector3(0, -0.1, 0);

            var scene = new THREE.Scene();
            scene.background = new THREE.Color(0x343a40);
            scene.fog = new THREE.Fog(0x72645b, 2, 15);

            const loader = new PLYLoader();
            var comp = {};
            loader.load(
                `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/3d_model/?path=${f.name}`,
                function(geometry) {
                    geometry.computeVertexNormals();

                    // const material = new THREE.MeshStandardMaterial({
                    //     color: 0x0055ff,
                    //     flatShading: true
                    // });
                    const material = new THREE.PointsMaterial({
                        // color: 0x0055ff,
                        size: 0.02,
                        vertexColors: THREE.VertexColors
                    });
                    const mesh = new THREE.Points(geometry, material);
                    //const mesh = new THREE.Mesh(geometry, material);
                    // const mesh = new THREE.Mesh(geometry);

                    mesh.position.y = -0.3;
                    mesh.position.z = 0.3;
                    mesh.rotation.x = -Math.PI / 2;
                    mesh.scale.multiplyScalar(0.5);

                    mesh.castShadow = true;
                    mesh.receiveShadow = true;

                    comp.geometry = geometry;
                    comp.material = material;
                    comp.mesh = mesh;

                    scene.add(mesh);
                }
            );

            this.currentModel.geometry = comp.geometry;
            this.currentModel.material = comp.material;
            this.currentModel.mesh = comp.mesh;

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
                const timer = Date.now() * 0.00005;

                camera.position.x = Math.sin(timer) * 2.5;
                camera.position.z = Math.cos(timer) * 2.5;

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
            document.getElementById(f.name).innerHTML = '';
            document.getElementById(f.name).prepend(renderer.domElement);
            //.appendChild(renderer.domElement);

            this.currentModel.scene = scene;
            this.currentModel.loader = loader;
            this.currentModel.renderer = renderer;
            this.currentModel.id = f.name;

            animate();
        },
        unrenderPreview() {
            if (
                this.currentModel.scene === undefined ||
                this.currentModel.scene === null
            )
                return;
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
        refresh() {
            this.$store.dispatch('tasks/refresh', {
                owner: this.$router.currentRoute.params.owner,
                name: this.$router.currentRoute.params.name
            });
        },
        cancel() {
            this.canceled = true;
            axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/cancel/`
                )
                .then(response => {
                    this.canceled = false;
                    if (response.status === 200) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                    } else {
                        this.showFailedToCancelAlert = true;
                    }
                })
                .catch(error => {
                    this.canceled = false;
                    Sentry.captureException(error);
                    return error;
                });
        },
        remove() {
            axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/delete/`
                )
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'tasks/setAll',
                            response.data.tasks
                        );
                        await router.push({
                            name: 'tasks'
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
            this.$bvModal.show('remove');
        },
        restart() {
            this.restarted = true;
            let config = this.recentlyRunWorkflows[this.workflowKey]; // retrieve workflow config

            // resubmit
            axios({
                method: 'post',
                url: `/apis/v1/tasks/`,
                data: {
                    repo: this.getWorkflow.repo,
                    config: config,
                    type: 'Now',
                    delete: false
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    this.restarted = false;
                    router.push({
                        name: 'task',
                        params: {
                            owner: response.data.owner,
                            name: response.data.name
                        }
                    });
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.restarted = false;
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
            this.thumbnailUrl = `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/thumbnail/?path=${file}`;
            this.thumbnailTitle = file;
            this.$bvModal.show('thumbnail');
        },
        preDownloadFile(file) {
            this.fileToDownload = file;
            if (this.mustAuthenticate)
                this.$bvModal.show('authenticate-download');
            else this.downloadFile();
        },
        async downloadFile() {
            this.downloading = true;
            let data = {
                path: this.fileToDownload
            };
            if (this.mustAuthenticate)
                data['auth'] = {
                    username: this.authenticationUsername,
                    password: this.authenticationPassword
                };
            else
                data['auth'] = {
                    username: this.getTask.agent.user
                };
            await axios({
                method: 'post',
                data: data,
                url: `/apis/v1/tasks/${this.getTask.owner}/${this.getTask.name}/output/`,
                config: { responseType: 'blob' }
            })
                .then(response => {
                    if (response && response.status === 404) {
                        return;
                    }

                    this.$bvModal.hide('authenticate-download');

                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', this.fileToDownload);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.downloading = false;
                    this.$bvModal.hide('authenticate-download');
                    return error;
                });
        },
        downloadTaskLogs() {
            axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/task_logs/`
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
                    link.setAttribute('download', this.taskLogFileName);
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
                    `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/container_logs/`
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
        getTextFile(file) {
            if (!this.fileIsText(file.name)) return;
            this.textContent = [];
            axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/file_text/?path=${file.path}`
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
        // await this.$store.dispatch('tasks/refresh', {
        //     owner: this.$router.currentRoute.params.owner,
        //     name: this.$router.currentRoute.params.name
        // });
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['workflow', 'recentlyRunWorkflows']),
        ...mapGetters('tasks', ['task', 'tasks', 'tasksLoading']),
        ...mapGetters('datasets', [
            'personalDatasets',
            'personalDatasetsLoading'
        ]),
        filteredResults() {
            return this.getTask.output_files
                .slice(
                    (this.outputFilePage - 1) * this.outputPageSize,
                    this.outputFilePage * this.outputPageSize
                )
                .filter(file => file.name.includes(this.resultSearchText));
        },
        workflowKey() {
            return `${this.getWorkflow.repo.owner.login}/${this.getWorkflow.repo.name}`;
        },
        getTask() {
            let task = this.task(
                this.$router.currentRoute.params.owner,
                this.$router.currentRoute.params.name
            );
            if (task !== undefined && task !== null) return task;
            return null;
        },
        taskLogs() {
            let all = this.getTask.task_logs.slice();
            var firstI = all.findIndex(l => l.includes('PENDING'));
            if (firstI === -1)
                firstI = all.findIndex(l => l.includes('RUNNING'));
            if (firstI === -1) return all;
            all.reverse();
            let lastI =
                all.length - all.findIndex(l => l.includes('RUNNING')) - 1;
            all.reverse();
            if (lastI === -1) return all;
            // if (lastI === all.length - 1) return all;
            else if (this.getTask.is_complete)
                all.splice(firstI, lastI - firstI + 1);
            else all.splice(firstI, lastI - firstI + 1, all[lastI]);
            return all;
        },
        notFound() {
            return this.getTask === null && !this.tasksLoading;
        },
        getWorkflow() {
            return this.workflow(
                this.getTask.workflow_owner,
                this.getTask.workflow_name
            );
        },
        taskLogFileName() {
            return `${this.$router.currentRoute.params.name}.plantit.log`;
        },
        containerLogFileName() {
            return `${
                this.$router.currentRoute.params.name
            }.${this.getTask.agent.name.toLowerCase()}.log`;
        },
        mustAuthenticate() {
            let ownsAgent =
                this.getTask.agent.user !== undefined &&
                this.getTask.agent.user === this.profile.djangoProfile.username;
            let isGuest = this.getTask.agent.users_authorized.some(
                user => user.username === this.profile.djangoProfile.username
            );
            return (
                this.getTask.agent.authentication === 'password' ||
                (!ownsAgent && !isGuest)
            );
        }
    },
    watch: {
        async $route() {
            // await this.$store.dispatch('tasks/refresh', this.getRun);
            window.location.reload(false);
            // this.$forceUpdate();
        },
        '$route.params.owner'() {
            // need to watch for route change to prompt reload
        },
        '$route.params.name'() {
            // need to watch for route change to prompt reload
        },
        viewMode() {
            // if (
            //     this.data !== null &&
            //     this.getTask.output_files.some(f => f.name.endsWith('ply'))
            // ) {
            //     this.unrenderPreview();
            //     if (this.viewMode === 'Carousel')
            //         if (this.currentCarouselSlide === 0)
            //             this.renderPreview(this.getTask.output_files[0]);
            // }
            // if (
            //     this.viewMode === 'Carousel' &&
            //     this.textContent.length === 0 &&
            //     this.getTask.output_files.length > 0
            // )
            //     this.getTextFile(this.getTask.output_files[0]);
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"


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
