<template>
    <div>
        <b-container class="p-2 vl" fluid>
            <b-row v-if="tasksLoading">
                <b-col>
                    <b-spinner
                        small
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
            <!--<b-row v-else-if="getTask.cleaned_up" align-content="center">
                <b-col>
                    <h6 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                        <i class="fas fa-broom fa-1x fa-fw"></i> This task has
                        been cleaned up.
                    </h6>
                </b-col>
            </b-row>-->
            <b-row>
                <b-col>
                    <div v-if="!tasksLoading && getWorkflow.config">
                        <b-row class="m-0 p-0">
                            <b-col md="auto" align-self="end" class="m-0 p-0">
                                <h4
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    <i class="fas fa-tasks fa-fw"></i>
                                    {{ getTask.guid }}
                                </h4></b-col
                            ><b-col class="m-0 ml-2 p-0">
                                <h5>
                                    <b-badge
                                        v-for="tag in getTask.tags"
                                        v-bind:key="tag"
                                        class="mr-2"
                                        variant="secondary"
                                        >{{ tag }}</b-badge
                                    >
                                </h5>
                            </b-col>
                            <b-col md="auto">
                                <b-spinner
                                    v-if="!getTask.is_complete"
                                    class="mr-1"
                                    small
                                    :variant="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                </b-spinner>
                                <b
                                    :class="
                                        getTask.is_failure || getTask.is_timeout
                                            ? 'text-danger'
                                            : getTask.is_cancelled
                                            ? 'text-secondary'
                                            : getTask.is_complete
                                            ? 'text-success'
                                            : profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >{{
                                        !getTask.agent.is_local &&
                                        !getTask.is_complete &&
                                        getTask.job_status !== null
                                            ? getTask.job_status.toUpperCase()
                                            : getTask.status.toUpperCase()
                                    }}</b
                                >
                                <small class="ml-1 mr-1">on</small>
                                <b-link
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    :to="{
                                        name: 'agent',
                                        params: {
                                            name: getTask.agent.name,
                                        },
                                    }"
                                    ><b-img
                                        v-if="getTask.agent.logo"
                                        rounded
                                        class="overflow-hidden"
                                        style="max-height: 1rem"
                                        :src="getTask.agent.logo"
                                    ></b-img
                                    ><i v-else class="fas fa-server fa-fw"></i>
                                    {{
                                        getTask.agent
                                            ? getTask.agent.name
                                            : '[agent removed]'
                                    }}</b-link
                                ></b-col
                            >
                        </b-row>
                        <b-row
                            ><b-col
                                ><span
                                    v-if="
                                        getTask.output_path !== null &&
                                        getTask.output_path !== ''
                                    "
                                >
                                    <small v-if="getTask.input_path !== null"
                                        ><i class="far fa-folder fa-fw mr-1"></i
                                        >{{ getTask.input_path }}</small
                                    ><small v-else
                                        ><i
                                            v-if="profile.darkMode"
                                            class="far fa-circle text-white fa-fw"
                                        ></i
                                        ><i
                                            v-else
                                            class="far fa-circle text-dark fa-fw"
                                        ></i
                                    ></small>
                                    <small
                                        ><i
                                            v-if="profile.darkMode"
                                            class="fas fa-arrow-right text-white fa-fw mr-1 ml-1"
                                        ></i
                                        ><i
                                            v-else
                                            class="fas fa-arrow-right text-dark fa-fw mr-1 ml-1"
                                        ></i
                                    ></small>
                                    <small v-if="getTask.output_path !== null"
                                        ><i class="far fa-folder fa-fw mr-1"></i
                                        >{{ getTask.output_path }}</small
                                    >
                                </span></b-col
                            ></b-row
                        >
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
                                    <!--<b-badge
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
                                    <small> on </small>-->

                                    <b-link
                                        v-if="getTask.project !== null"
                                        :class="
                                            profile.darkMode
                                                ? 'text-light ml-3'
                                                : 'text-dark ml-3'
                                        "
                                        :to="{
                                            name: 'project',
                                            params: {
                                                owner: getTask.project.owner,
                                                title: getTask.project.title,
                                            },
                                        }"
                                        ><b-img
                                            class="mb-1 mr-1"
                                            style="max-width: 18px"
                                            :src="
                                                profile.darkMode
                                                    ? require('../../assets/miappe_icon.png')
                                                    : require('../../assets/miappe_icon_black.png')
                                            "
                                        ></b-img>
                                        <span v-if="getTask.project !== null"
                                            >{{ getTask.project.title }}
                                            <small
                                                v-if="getTask.study !== null"
                                                >{{
                                                    getTask.study.title
                                                }}</small
                                            ></span
                                        ></b-link
                                    >
                                </h5>
                            </b-col>
                            <b-col
                                md="auto"
                                class="m-0 mb-2"
                                align-self="start"
                            >
                                <b-button
                                    :disabled="canceling"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    :title="`${getTask.guid} (click to copy to clipboard)`"
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
                                        style="width: 0.7rem; height: 0.7rem"
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
                                    :disabled="canceling"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    title="Cancel Task"
                                    @click="cancel"
                                >
                                    <i class="fas fa-times fa-fw"></i>
                                    Cancel<b-spinner
                                        small
                                        v-if="canceling"
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
                                    title="Refresh Task"
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
                                    style="min-height: 5rem"
                                    class="overflow-hidden mt-0"
                                    no-body
                                    :style="
                                        getTask.is_failure || getTask.is_timeout
                                            ? 'border-bottom: 5px solid red'
                                            : getTask.is_cancelled
                                            ? 'border-bottom: 5px solid lightgray'
                                            : getTask.is_complete
                                            ? 'border-bottom: 5px solid #d6df5D'
                                            : 'border-bottom: 5px solid #e2e3b0'
                                    "
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
                                            <i
                                                class="fas fa-seedling fa-fw"
                                            ></i>
                                            Created
                                            {{ prettify(getTask.created) }}
                                        </small>
                                    </b-col>
                                    <b-col
                                        class="m-0 p-0 text-center"
                                        v-if="!getTask.is_complete"
                                    >
                                        <small>
                                            <i
                                                class="fas fa-satellite-dish fa-fw"
                                            ></i>

                                            Last updated
                                            {{ prettify(getTask.updated) }}
                                        </small>
                                    </b-col>
                                    <b-col
                                        class="m-0 p-0 text-center"
                                        v-if="getTask.is_complete"
                                        ><small>
                                            <i class="fas fa-clock fa-fw"></i>
                                            Ran for
                                            {{
                                                prettifyDuration(
                                                    duration(getTask)
                                                )
                                            }}</small
                                        ></b-col
                                    >
                                    <b-col class="m-0 p-0 text-center">
                                        <small v-if="getTask.is_complete">
                                            <i class="fas fa-check fa-fw"></i>
                                            Completed
                                            {{
                                                prettify(getTask.completed)
                                            }}</small
                                        >
                                        <small v-else>
                                            <i
                                                class="fas fa-flag-checkered fa-fw"
                                            ></i>

                                            Due
                                            {{ prettify(getTask.due_time) }}
                                        </small>
                                    </b-col>

                                    <b-col
                                        class="m-0 p-0 text-center"
                                        v-if="
                                            getTask.is_complete &&
                                            getTask.cleanup_time !== null
                                        "
                                        ><small>
                                            <i class="fas fa-broom fa-fw"></i>

                                            Cleaning up
                                            {{
                                                prettify(getTask.cleanup_time)
                                            }}</small
                                        ></b-col
                                    >
                                </b-row>
                                <b-row
                                    class="m-0 p-0 mt-2"
                                    v-if="getTask.status !== 'created'"
                                >
                                    <b-col class="m-0 p-1">
                                        <Plotly
                                            style="
                                                position: relative;
                                                top: 20px;
                                            "
                                            :data="timeseriesData"
                                            :layout="timeseriesLayout"
                                        ></Plotly>
                                    </b-col>
                                </b-row>
                                <b-row class="m-0 p-0 mt-2">
                                    <b-col class="m-0 p-1">
                                        <div
                                            :class="
                                                profile.darkMode
                                                    ? 'theme-container-dark m-0 p-1 pt-3 pb-3'
                                                    : 'theme-container-light m-0 p-1 pt-3 pb-3'
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
                                                <!--<b-tabs align="center"
                                                    ><b-tab active
                                                        ><template #title
                                                            >Orchestrator</template-->
                                                <b-row class="m-0">
                                                    <b-col
                                                        v-if="
                                                            getTask
                                                                .orchestrator_logs
                                                                .length > 0
                                                        "
                                                        class="m-0 p-0 pl-3 pr-3"
                                                        style="
                                                            white-space: pre-line;
                                                        "
                                                    >
                                                        <span
                                                            v-for="line in taskLogs"
                                                            v-bind:key="line"
                                                            v-show="
                                                                line !==
                                                                    undefined &&
                                                                line !== null
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
                                                    ></b-col> </b-row
                                                ><!--</b-tab
                                                    ><b-tab
                                                        ><template #title
                                                            >CLI</template
                                                        ><b-row class="m-0">
                                                            <b-col
                                                                v-if="
                                                                    schedulerLogs
                                                                        .length >
                                                                        0
                                                                "
                                                                class="m-0 p-0 pl-3 pr-3 pt-1"
                                                                style="white-space: pre-line;"
                                                            >
                                                                <span
                                                                    v-for="line in schedulerLogs"
                                                                    v-bind:key="
                                                                        line
                                                                    "
                                                                    v-show="
                                                                        line !==
                                                                            undefined &&
                                                                            line !==
                                                                                null
                                                                    "
                                                                    >{{
                                                                        line +
                                                                            '\n'
                                                                    }}</span
                                                                >
                                                            </b-col>
                                                            <b-col v-else
                                                                ><b-skeleton-wrapper
                                                                    :loading="
                                                                        !getTask.is_complete
                                                                    "
                                                                >
                                                                    <template
                                                                        #loading
                                                                    >
                                                                        <b-skeleton
                                                                            width="15%"
                                                                        ></b-skeleton
                                                                        ><b-skeleton
                                                                            width="25%"
                                                                        ></b-skeleton
                                                                        ><b-skeleton
                                                                            width="20%"
                                                                        ></b-skeleton></template></b-skeleton-wrapper
                                                            ></b-col> </b-row></b-tab
                                                ><b-tab
                                                        ><template #title
                                                            >Container</template
                                                        ><b-row class="m-0">
                                                            <b-col
                                                                v-if="
                                                                    agentLogs
                                                                        .length >
                                                                        0
                                                                "
                                                                class="m-0 p-0 pl-3 pr-3 pt-1"
                                                                style="white-space: pre-line;"
                                                            >
                                                                <span
                                                                    v-for="line in agentLogs"
                                                                    v-bind:key="
                                                                        line
                                                                    "
                                                                    v-show="
                                                                        line !==
                                                                            undefined &&
                                                                            line !==
                                                                                null
                                                                    "
                                                                    >{{
                                                                        line +
                                                                            '\n'
                                                                    }}</span
                                                                >
                                                            </b-col>
                                                            <b-col v-else
                                                                ><b-skeleton-wrapper
                                                                    :loading="
                                                                        !getTask.is_complete
                                                                    "
                                                                >
                                                                    <template
                                                                        #loading
                                                                    >
                                                                        <b-skeleton
                                                                            width="15%"
                                                                        ></b-skeleton
                                                                        ><b-skeleton
                                                                            width="25%"
                                                                        ></b-skeleton
                                                                        ><b-skeleton
                                                                            width="20%"
                                                                        ></b-skeleton></template></b-skeleton-wrapper
                                                            ></b-col> </b-row></b-tab
                                                ></b-tabs>-->
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
                                                <b-col
                                                    class="text-left"
                                                    v-if="
                                                        getTask.results_retrieved &&
                                                        getTask.output_files
                                                            .length > 0
                                                    "
                                                >
                                                    <b
                                                        v-if="
                                                            getWorkflow.config
                                                                .output
                                                        "
                                                        >Matching:
                                                        <code
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
                                                    <br />
                                                    <span
                                                        v-if="
                                                            getTask.results_retrieved
                                                        "
                                                        >{{
                                                            getTask.output_files
                                                                .length
                                                        }}
                                                        results found</span
                                                    ><span
                                                        v-else-if="
                                                            getTask.status !==
                                                            'running'
                                                        "
                                                        ><b-spinner
                                                            small
                                                            :variant="
                                                                profile.darkMode
                                                                    ? 'light'
                                                                    : 'dark'
                                                            "
                                                        ></b-spinner>
                                                        Loading</span
                                                    >
                                                    <br />
                                                </b-col>
                                                <b-col
                                                    v-else
                                                    align-self="center"
                                                    class="text-center"
                                                    ><span class="text-center"
                                                        ><i
                                                            class="far fa-folder-open fa-fw"
                                                        ></i>
                                                        No results found</span
                                                    ></b-col
                                                >
                                                <b-col
                                                    v-if="
                                                        getTask.results_retrieved &&
                                                        getTask.output_files !==
                                                            undefined
                                                    "
                                                    md="auto"
                                                    align-self="end"
                                                >
                                                    <b-dropdown
                                                        :disabled="
                                                            getTask.output_files !==
                                                                undefined &&
                                                            getTask.output_files !==
                                                                null &&
                                                            getTask.output_files
                                                                .length === 0
                                                        "
                                                        class="text-right"
                                                        :text="
                                                            outputPageSize.toString()
                                                        "
                                                        dropleft
                                                        :title="
                                                            'Showing ' +
                                                            outputPageSize +
                                                            ' files at once'
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
                                                <!--<b-col
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
                                                >-->
                                                <br />
                                                <br />
                                            </b-row>
                                            <b-row
                                                v-if="
                                                    getTask.results_retrieved &&
                                                    getTask.output_files !==
                                                        undefined
                                                "
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
                                                            #page="{
                                                                page,
                                                                active,
                                                            }"
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
                                                <b-col align-self="center"
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
                                                            style="
                                                                border-top: 1px
                                                                    solid
                                                                    rgba(
                                                                        211,
                                                                        211,
                                                                        211,
                                                                        0.5
                                                                    );
                                                            "
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
                                                                style="
                                                                    position: relative;
                                                                    top: -5px;
                                                                    left: -40px;
                                                                "
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
                                                        </b-row>
                                                    </div>
                                                    <!--<b-card-group
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
                                                            <b-card-body
                                                                class="text-center"
                                                            >
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
                                                            </b-card-body>
                                                        </b-card>
                                                    </b-card-group>-->
                                                    <!--<b-carousel
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
                                                                                preDownloadFile(
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
                                                    </b-carousel>-->
                                                </div>
                                            </b-overlay>
                                        </div>
                                        <div
                                            class="m-3"
                                            v-if="
                                                getTask.results_retrieved &&
                                                getTask.output_files !==
                                                    undefined
                                            "
                                        >
                                            <b-row
                                                ><!--<b-col
                                                    v-if="
                                                        getWorkflow.config
                                                            .input !== undefined
                                                    "
                                                    >{{
                                                        Math.max(
                                                            getTask.inputs_downloaded,
                                                            getTask.inputs_submitted
                                                        )
                                                    }}/{{
                                                        getTask.inputs_detected
                                                    }}
                                                    input(s) loaded<b-progress
                                                        :value="
                                                            Math.max(
                                                                getTask.inputs_downloaded,
                                                                getTask.inputs_submitted
                                                            )
                                                        "
                                                        :max="
                                                            getTask.inputs_detected
                                                        "
                                                        :variant="
                                                            Math.max(
                                                                getTask.inputs_downloaded,
                                                                getTask.inputs_submitted
                                                            ) !==
                                                            getTask.inputs_detected
                                                                ? 'warning'
                                                                : 'success'
                                                        "
                                                        :animated="
                                                            Math.max(
                                                                getTask.inputs_downloaded,
                                                                getTask.inputs_submitted
                                                            ) !==
                                                                getTask.inputs_detected
                                                        "
                                                    ></b-progress></b-col
                                                ><b-col
                                                    v-if="
                                                        getWorkflow.config
                                                            .input !==
                                                            undefined &&
                                                            getWorkflow.config
                                                                .input.kind !==
                                                                'directory'
                                                    "
                                                    >{{
                                                        getTask.inputs_submitted
                                                    }}/{{
                                                        getTask.inputs_detected
                                                    }}
                                                    container(s)
                                                    submitted<b-progress
                                                        :value="
                                                            getTask.inputs_submitted
                                                        "
                                                        :max="
                                                            getTask.inputs_detected
                                                        "
                                                        :variant="
                                                            getTask.inputs_submitted !==
                                                            getTask.inputs_detected
                                                                ? 'warning'
                                                                : 'success'
                                                        "
                                                        :animated="
                                                            getTask.inputs_submitted !==
                                                                getTask.inputs_detected
                                                        "
                                                    ></b-progress></b-col
                                                ><b-col
                                                    v-if="
                                                        getWorkflow.config
                                                            .input !==
                                                            undefined &&
                                                            getWorkflow.config
                                                                .input.kind !==
                                                                'directory'
                                                    "
                                                    >{{
                                                        getTask.inputs_completed
                                                    }}/{{
                                                        getTask.inputs_detected
                                                    }}
                                                    container(s)
                                                    completed<b-progress
                                                        :value="
                                                            getTask.inputs_completed
                                                        "
                                                        :max="
                                                            getTask.inputs_detected
                                                        "
                                                        :variant="
                                                            getTask.inputs_completed !==
                                                            getTask.inputs_detected
                                                                ? 'warning'
                                                                : 'success'
                                                        "
                                                        :animated="
                                                            getTask.inputs_completed !==
                                                                getTask.inputs_detected
                                                        "
                                                    ></b-progress></b-col
                                                >--><b-col
                                                    v-if="
                                                        getTask.is_complete &&
                                                        getTask.result_transfer
                                                    "
                                                    >{{
                                                        getTask.results_transferred
                                                    }}/{{
                                                        getTask.output_files
                                                            .length > 0
                                                            ? getTask
                                                                  .output_files
                                                                  .length
                                                            : '?'
                                                    }}
                                                    results
                                                    transferred<b-progress
                                                        :value="
                                                            getTask.results_transferred
                                                        "
                                                        :max="
                                                            getTask.output_files
                                                                .length
                                                        "
                                                        :variant="
                                                            getTask.results_transferred !==
                                                            getTask.output_files
                                                                .length
                                                                ? 'warning'
                                                                : 'success'
                                                        "
                                                        :animated="
                                                            getTask.results_transferred !==
                                                            getTask.output_files
                                                                .length
                                                        "
                                                    ></b-progress></b-col
                                            ></b-row>
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
                                <b-card
                                    v-if="
                                        getTask.is_complete &&
                                        getTask.transferred
                                    "
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
                                    no-body
                                >
                                    <b-card-header
                                        class="mt-1"
                                        :header-bg-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        ><h5
                                            :class="
                                                profile.darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                        >
                                            <b-img
                                                class="mr-2"
                                                rounded
                                                style="max-height: 1.7rem"
                                                left
                                                :src="
                                                    require('../../assets/logos/cyverse_bright.png')
                                                "
                                            ></b-img>
                                            Data Store
                                        </h5></b-card-header
                                    >
                                    <b-card-body>
                                        <b-row>
                                            <b-col>
                                                <datatree
                                                    :node="userDatasets"
                                                    :upload="true"
                                                    :download="true"
                                                    :create="true"
                                                    :search="
                                                        getTask.transfer_path
                                                    "
                                                    :class="
                                                        profile.darkMode
                                                            ? 'theme-dark'
                                                            : 'theme-light'
                                                    "
                                                ></datatree></b-col
                                        ></b-row>
                                    </b-card-body>
                                </b-card>
                            </b-col>
                        </b-row>
                    </div>
                </b-col>
            </b-row>
        </b-container>
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
import datatree from '@/components/datasets/data-tree';
import WorkflowBlurb from '@/components/workflows/workflow-blurb.vue';
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
import { guid } from '@/utils';
import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Plotly } from 'vue-plotly';

export default {
    name: 'task',
    components: {
        WorkflowBlurb,
        datatree,
        Plotly,
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
            canceling: false,
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
            // the "v-if hack" (https://michaelnthiessen.com/force-re-render/)
            render: true,
            authenticationUsername: '',
            authenticationPassword: '',
            transferringPath: '',
            transferring: false,
            // logs
            schedulerLogs: [],
            agentLogs: [],
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
                noCloseButton: true,
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
        async thumbnailFor(path) {
            let i = this.getTask.output_files.findIndex((f) => f.path === path);
            if (
                this.viewMode === 'Grid' &&
                i >= (this.outputFilePage - 1) * this.outputPageSize &&
                i <= this.outputFilePage * this.outputPageSize
            )
                // return `https://de.cyverse.org/terrain/secured/fileio/download?path=${path}`;
                return `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.guid}/thumbnail/?path=${path}`;
            else return null;
        },
        prettifyShort: function (date) {
            return `${moment(date).fromNow()}`;
        },
        prettifyDuration: function (dur) {
            return moment.duration(dur, 'seconds').humanize();
        },
        duration(task) {
            return moment.duration(
                moment(task.created).diff(moment(task.completed))
            );
        },
        fileIsImage(file) {
            return (
                file.toLowerCase().split('.').pop() === 'png' ||
                file.toLowerCase().split('.').pop() === 'jpg' ||
                file.toLowerCase().split('.').pop() === 'jpeg' ||
                file.toLowerCase().split('.').pop() === 'czi'
            );
        },
        fileIsText(file) {
            return (
                file.toLowerCase().split('.').pop() === 'txt' ||
                file.toLowerCase().split('.').pop() === 'csv' ||
                file.toLowerCase().split('.').pop() === 'tsv' ||
                file.toLowerCase().split('.').pop() === 'yml' ||
                file.toLowerCase().split('.').pop() === 'yaml' ||
                file.toLowerCase().split('.').pop() === 'log' ||
                file.toLowerCase().split('.').pop() === 'out' ||
                file.toLowerCase().split('.').pop() === 'err'
            );
        },
        fileIs3dModel(file) {
            return file.toLowerCase().split('.').pop() === 'ply';
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
                `/apis/v1/tasks/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.guid}/3d_model/?path=${f.name}`,
                function (geometry) {
                    geometry.computeVertexNormals();

                    // const material = new THREE.MeshStandardMaterial({
                    //     color: 0x0055ff,
                    //     flatShading: true
                    // });
                    const material = new THREE.PointsMaterial({
                        // color: 0x0055ff,
                        size: 0.02,
                        vertexColors: THREE.VertexColors,
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

            var addShadowedLight = function (x, y, z, color, intensity) {
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

            var onWindowResize = function () {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();

                renderer.setSize(window.innerWidth, window.innerHeight);
            };

            var animate = function () {
                requestAnimationFrame(animate);
                render();
            };

            var render = function () {
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
                name: this.$router.currentRoute.params.guid,
            });
        },
        async cancel() {
            this.canceling = true;
            await axios({
                method: 'post',
                url: `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/cancel/`,
                data: {},
            })
                .then(async (response) => {
                    this.canceling = false;
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'tasks/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Canceled task ${this.$router.currentRoute.params.guid}`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to cancel task ${this.$router.currentRoute.params.guid}`,
                            guid: guid().toString(),
                        });
                    }
                })
                .catch(async (error) => {
                    this.canceling = false;
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to cancel task ${this.$router.currentRoute.params.guid}`,
                        guid: guid().toString(),
                    });
                    return error;
                });
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
                    delete: false,
                },
                headers: { 'Content-Type': 'application/json' },
            })
                .then((response) => {
                    this.restarted = false;
                    router.push({
                        name: 'task',
                        params: {
                            owner: response.data.owner,
                            name: response.data.guid,
                        },
                    });
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.restarted = false;
                    throw error;
                });
        },
        prettify: function (date) {
            return moment(date).fromNow();
            // (${moment(date).format('MMMM Do YYYY, h:mm a')})
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
            this.thumbnailUrl = `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/thumbnail/?path=${file}`;
            this.thumbnailTitle = file;
            this.$bvModal.show('thumbnail');
        },
        async downloadFile() {
            this.downloading = true;
            let data = {
                path: this.fileToDownload,
            };
            await axios({
                method: 'post',
                data: data,
                url: `/apis/v1/tasks/${this.getTask.guid}/output/`,
                config: { responseType: 'blob' },
            })
                .then((response) => {
                    if (response && response.status === 404) {
                        return;
                    }

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
                .catch((error) => {
                    Sentry.captureException(error);
                    this.downloading = false;
                    return error;
                });
        },
        async getSchedulerLogs() {
            await axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/logs/scheduler/`
                )
                .then((response) => {
                    this.schedulerLogs = response.data.lines;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        async getAgentLogs() {
            await axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/logs/agent/`
                )
                .then((response) => {
                    this.agentLogs = response.data.lines;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        downloadTaskLogs() {
            axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/logs/orchestrator/`
                )
                .then((response) => {
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
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        downloadSchedulerLogs() {
            axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/logs/scheduler/dl/`
                )
                .then((response) => {
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
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        downloadAgentLogs() {
            axios
                .get(
                    `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/logs/agent/dl/`
                )
                .then((response) => {
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
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        // getTextFile(file) {
        //     if (!this.fileIsText(file.name)) return;
        //     this.textContent = [];
        //     axios
        //         .get(
        //             `/apis/v1/tasks/${this.$router.currentRoute.params.guid}/file_text/?path=${file.path}`
        //         )
        //         .then((response) => {
        //             if (response.status === 200) {
        //                 this.textContent = response.data.text;
        //             }
        //         })
        //         .catch((error) => {
        //             Sentry.captureException(error);
        //             return error;
        //         });
        // },
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['workflow']),
        ...mapGetters('tasks', ['task', 'tasks', 'tasksLoading']),
        ...mapGetters('datasets', ['userDatasets', 'userDatasetsLoading']),
        timeseriesData() {
            var x = [
                moment(this.getTask.created).format('YYYY-MM-DD HH:mm:ss'),
            ];
            var y = [0];
            if (this.getTask.is_complete) {
                x.push(
                    moment(this.getTask.completed).format('YYYY-MM-DD HH:mm:ss')
                );
                y.push(0);
            }

            return [
                {
                    x: x,
                    y: y,
                    hovertemplate: '<br>%{text}<br><extra></extra>',
                    text: [
                        `created ${this.prettify(this.getTask.created)}`,
                        `completed ${this.prettify(this.getTask.completed)}`, // TODO show status instead
                    ],
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: {
                        color: '#d6df5D',
                    },
                    marker: {
                        color: [
                            '#e2e3b0',
                            this.getTask.is_success
                                ? '#d6df5D'
                                : 'rgb(255, 114, 114)',
                        ],
                        line: {
                            color: '#e2e3b0',
                            width: 1,
                        },
                        symbol: 'hourglass',
                        size: 20,
                    },
                },
            ];
        },
        timeseriesLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                height: 220,
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    lines: false,
                },
                yaxis: {
                    showticklabels: false,
                    showgrid: false,
                    lines: false,
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
            };
        },
        filteredResults() {
            return this.getTask.output_files
                .slice(
                    (this.outputFilePage - 1) * this.outputPageSize,
                    this.outputFilePage * this.outputPageSize
                )
                .filter((file) => file.name.includes(this.resultSearchText));
        },
        workflowKey() {
            return `${this.getWorkflow.repo.owner.login}/${this.getWorkflow.repo.name}`;
        },
        getTask() {
            let task = this.task(this.$router.currentRoute.params.guid);
            if (task !== undefined && task !== null) return task;
            return null;
        },
        taskLogs() {
            let all = this.getTask.orchestrator_logs.slice();
            // var firstI = all.findIndex(l => l.includes('PENDING'));
            // if (firstI < 1) firstI = all.findIndex(l => l.includes('RUNNING'));

            var firstI = all.findIndex((l) => l.includes('PENDING'));
            if (firstI !== -1) {
                all.reverse();
                var lastI =
                    all.length -
                    all.findIndex((l) => l.includes('PENDING')) -
                    1;
                all.reverse();
                if (this.getTask.is_complete)
                    all.splice(firstI, lastI - firstI);
                else all.splice(firstI, lastI - firstI + 1, all[lastI]);
            }

            firstI = all.findIndex((l) => l.includes('RUNNING'));
            if (firstI !== -1) {
                all.reverse();
                lastI =
                    all.length -
                    all.findIndex((l) => l.includes('RUNNING')) -
                    1;
                all.reverse();
                // if (lastI === all.length - 1) return all;
                if (this.getTask.is_complete)
                    all.splice(firstI, lastI - firstI);
                else all.splice(firstI, lastI - firstI + 1, all[lastI]);
            }

            return all;
        },
        notFound() {
            return this.getTask === null && !this.tasksLoading;
        },
        getWorkflow() {
            return this.workflow(
                this.getTask.workflow_owner,
                this.getTask.workflow_name,
                this.getTask.workflow_branch
            );
        },
        taskLogFileName() {
            return `${this.$router.currentRoute.params.guid}.plantit.log`;
        },
        containerLogFileName() {
            return `${
                this.$router.currentRoute.params.guid
            }.${this.getTask.agent.name.toLowerCase()}.log`;
        },
        mustAuthenticate() {
            let ownsAgent =
                this.getTask.agent.user !== undefined &&
                this.getTask.agent.user === this.profile.djangoProfile.username;
            let isGuest = this.getTask.agent.users_authorized.some(
                (user) => user.username === this.profile.djangoProfile.username
            );
            return (
                this.getTask.agent.authentication === 'password' ||
                (!ownsAgent && !isGuest)
            );
        },
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
        '$route.params.guid'() {
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
        },
    },
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
