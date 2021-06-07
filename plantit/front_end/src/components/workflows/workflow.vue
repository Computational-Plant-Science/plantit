<template>
    <div>
        <b-container class="vl" fluid>
            <b-row no-gutters>
                <b-col v-if="showStatusAlert">
                    <b-alert
                        :show="showStatusAlert"
                        :variant="
                            statusAlertMessage.startsWith('Failed')
                                ? 'danger'
                                : 'success'
                        "
                        dismissible
                        @dismissed="showStatusAlert = false"
                    >
                        {{ statusAlertMessage }}
                    </b-alert>
                </b-col>
            </b-row>
            <b-row
                align-h="center"
                v-if="workflowLoading || getWorkflow === null"
            >
                <b-spinner
                    type="grow"
                    label="Loading..."
                    variant="secondary"
                ></b-spinner>
            </b-row>
            <b-row v-else>
                <b-col>
                    <b-row>
                        <b-col>
                            <b-alert
                                id="flowInvalid"
                                v-if="
                                    this.getWorkflow.validation_errors !==
                                        undefined
                                "
                                :show="
                                    this.getWorkflow.validation_errors !==
                                        undefined
                                "
                                variant="danger"
                                >This workflow's configuration is invalid. It
                                cannot be used in this state.
                                <b-link
                                    :href="
                                        'https://github.com/' +
                                            this.owner +
                                            '/' +
                                            this.name +
                                            '/issues/new'
                                    "
                                    ><i
                                        class="fab fa-github fa-1x mr-1 fa-fw"
                                    ></i
                                    >File an issue?</b-link
                                ><br />
                                Errors:
                                {{
                                    this.getWorkflow.validation_errors.join(
                                        ', '
                                    )
                                }}
                            </b-alert>
                            <div
                                v-if="getWorkflow && getWorkflow.config"
                                :class="
                                    profile.darkMode
                                        ? 'theme-dark'
                                        : 'theme-light'
                                "
                            >
                                <b-row
                                    align-v="center"
                                    align-h="center"
                                    v-if="workflowLoading"
                                >
                                    <b-col align-self="end" class="text-center">
                                        <b-spinner
                                            type="grow"
                                            label="Loading..."
                                            variant="secondary"
                                        ></b-spinner>
                                    </b-col>
                                </b-row>
                                <b-row no-gutters v-else>
                                    <b-img
                                        v-if="getWorkflow.config.logo"
                                        rounded
                                        class="card-img-right"
                                        style="max-width: 7rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                        right
                                        :src="
                                            `https://raw.githubusercontent.com/${getWorkflow.repo.owner.login}/${getWorkflow.repo.name}/master/${getWorkflow.config.logo}`
                                        "
                                    ></b-img>
                                    <!--<b-img
                                        v-else
                                        class="card-img-right"
                                        style="max-width: 7rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                        right
                                        :src="require('../../assets/logo.png')"
                                    ></b-img>-->
                                    <b-col>
                                        <b-row>
                                            <b-col
                                                md="auto"
                                                class="mr-0"
                                                align-self="end"
                                            >
                                                <h2
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-stream fa-fw"
                                                    ></i>
                                                    {{
                                                        getWorkflow.config.name
                                                    }}
                                                </h2> </b-col
                                            ><b-col
                                                md="auto"
                                                align-self="center"
                                                class="m-0"
                                                ><b-button
                                                    v-if="ownsWorkflow"
                                                    size="sm"
                                                    @click="togglePublic"
                                                    :variant="
                                                        getWorkflow.public
                                                            ? 'success'
                                                            : 'warning'
                                                    "
                                                >
                                                    <b-spinner
                                                        small
                                                        v-if="togglingPublic"
                                                        label="Loading..."
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'light'
                                                                : 'dark'
                                                        "
                                                        class="mr-1"
                                                    ></b-spinner>
                                                    <span
                                                        v-if="
                                                            getWorkflow.public
                                                        "
                                                        ><i
                                                            class="fas fa-unlock fa-fw"
                                                        ></i>
                                                        Public</span
                                                    ><span v-else
                                                        ><i
                                                            class="fas fa-lock fa-fw"
                                                        ></i>
                                                        Private</span
                                                    ></b-button
                                                >
                                                <b-badge
                                                    v-else
                                                    class="mr-1"
                                                    :variant="
                                                        getWorkflow.public
                                                            ? 'success'
                                                            : 'warning'
                                                    "
                                                    ><span
                                                        v-if="
                                                            getWorkflow.public
                                                        "
                                                        ><i
                                                            class="fas fa-unlock fa-fw"
                                                        ></i>
                                                        Public</span
                                                    ><span v-else
                                                        ><i
                                                            class="fas fa-lock fa-fw"
                                                        ></i>
                                                        Private</span
                                                    ></b-badge
                                                ></b-col
                                            >
                                            <b-col
                                                class="m-0"
                                                align-self="center"
                                                md="auto"
                                                ><b-button
                                                    size="sm"
                                                    :disabled="workflowLoading"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    v-b-tooltip.hover
                                                    title="Refresh"
                                                    @click="refreshWorkflow"
                                                >
                                                    <i class="fas fa-redo"></i>
                                                    Refresh
                                                    <b-spinner
                                                        small
                                                        v-if="workflowLoading"
                                                        label="Refreshing..."
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'light'
                                                                : 'dark'
                                                        "
                                                        class="ml-2 mb-1"
                                                    ></b-spinner> </b-button></b-col
                                            ><b-col
                                                class="m-0"
                                                align-self="center"
                                                md="auto"
                                                ><b-button
                                                    @click="
                                                        showDisconnectWorkflowModal
                                                    "
                                                    size="sm"
                                                    variant="outline-danger"
                                                    ><i
                                                        class="fas fa-times-circle fa-fw fa-1x"
                                                    ></i>
                                                    Disconnect</b-button
                                                ></b-col
                                            >
                                        </b-row>
                                        <b-row>
                                            <b-col md="auto" class="mr-0 ml-0">
                                                <b-badge
                                                    v-for="topic in getWorkflow
                                                        .repo.topics"
                                                    v-bind:key="topic"
                                                    class="mr-1"
                                                    variant="secondary"
                                                    >{{ topic }}</b-badge
                                                >
                                            </b-col>
                                        </b-row>
                                        <b-row class="mb-1">
                                            <b-col md="auto" class="mr-0 ml-0">
                                                <small>
                                                    <b-link
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-light'
                                                                : 'text-dark'
                                                        "
                                                        :href="
                                                            'https://github.com/' +
                                                                getWorkflow.repo
                                                                    .owner
                                                                    .login +
                                                                '/' +
                                                                getWorkflow.repo
                                                                    .name
                                                        "
                                                    >
                                                        <i
                                                            class="fab fa-github fa-fw"
                                                        ></i>
                                                        {{
                                                            getWorkflow.repo
                                                                .owner.login
                                                        }}/{{
                                                            getWorkflow.repo
                                                                .name
                                                        }}
                                                    </b-link>
                                                </small>
                                            </b-col>
                                            <b-col md="auto" class="mr-0 ml-0"
                                                ><small
                                                    >Stargazers:
                                                    <b>{{
                                                        getWorkflow.repo
                                                            .stargazers_count
                                                    }}</b></small
                                                ></b-col
                                            >
                                            <!--<b-col md="auto" class="mr-0 ml-0"
                                                ><small
                                                    >Runs: <b>0</b></small
                                                ></b-col
                                            >-->
                                        </b-row>
                                        <b-tabs
                                            v-model="activeTab"
                                            nav-class="bg-transparent"
                                            active-nav-item-class="bg-info text-dark"
                                            pills
                                            ><b-tab
                                                title="About"
                                                :title-link-class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark m-0 p-3'
                                                        : 'theme-light m-0 p-3'
                                                "
                                            >
                                                <b-row>
                                                    <b-col>
                                                        <h5
                                                            :class="
                                                                profile.darkMode
                                                                    ? 'text-light'
                                                                    : 'text-dark'
                                                            "
                                                        >
                                                            Description
                                                        </h5>
                                                        <b-row>
                                                            <b-col>
                                                                {{
                                                                    getWorkflow
                                                                        .repo
                                                                        .description
                                                                }}
                                                            </b-col>
                                                        </b-row>
                                                        <hr
                                                            class="mt-2 mb-2"
                                                            style="border-color: gray"
                                                        />
                                                        <div
                                                            v-if="
                                                                getWorkflow
                                                                    .config
                                                                    .author !==
                                                                    undefined &&
                                                                    getWorkflow
                                                                        .config
                                                                        .author !==
                                                                        null
                                                            "
                                                        >
                                                            <h5
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'text-light'
                                                                        : 'text-dark'
                                                                "
                                                            >
                                                                Author(s)
                                                            </h5>
                                                            <b-row>
                                                                <b-col>
                                                                    <b-row
                                                                        v-if="
                                                                            getWorkflow
                                                                                .config
                                                                                .author !==
                                                                                undefined
                                                                        "
                                                                    >
                                                                        <b-col>
                                                                            <span
                                                                                v-if="
                                                                                    typeof getWorkflow
                                                                                        .config
                                                                                        .author ===
                                                                                        'string' ||
                                                                                        (Array.isArray(
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .author
                                                                                        ) &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .author
                                                                                                .length ===
                                                                                                1)
                                                                                "
                                                                                :class="
                                                                                    profile.darkMode
                                                                                        ? 'text-light'
                                                                                        : 'text-dark'
                                                                                "
                                                                                >{{
                                                                                    getWorkflow
                                                                                        .config
                                                                                        .author
                                                                                }}</span
                                                                            >
                                                                            <b-list-group
                                                                                v-else
                                                                            >
                                                                                <b-list-group-item
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'light'
                                                                                    "
                                                                                    v-for="author in getWorkflow
                                                                                        .config
                                                                                        .author"
                                                                                    v-bind:key="
                                                                                        author
                                                                                    "
                                                                                    >{{
                                                                                        author
                                                                                    }}</b-list-group-item
                                                                                >
                                                                            </b-list-group>
                                                                        </b-col>
                                                                    </b-row>
                                                                </b-col>
                                                            </b-row>
                                                        </div>
                                                        <div
                                                            v-if="
                                                                getWorkflow
                                                                    .config
                                                                    .doi !==
                                                                    undefined &&
                                                                    getWorkflow
                                                                        .config
                                                                        .doi !==
                                                                        null
                                                            "
                                                        >
                                                            <br />
                                                            <h5
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'text-light'
                                                                        : 'text-dark'
                                                                "
                                                            >
                                                                Publications/DOIs
                                                            </h5>
                                                            <b-row>
                                                                <b-col>
                                                                    <b-row
                                                                        v-if="
                                                                            getWorkflow
                                                                                .config
                                                                                .doi !==
                                                                                undefined
                                                                        "
                                                                    >
                                                                        <b-col>
                                                                            <b-link
                                                                                v-if="
                                                                                    typeof getWorkflow
                                                                                        .config
                                                                                        .doi ===
                                                                                        'string' ||
                                                                                        (Array.isArray(
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .doi
                                                                                        ) &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .doi
                                                                                                .length ===
                                                                                                1)
                                                                                "
                                                                                :class="
                                                                                    profile.darkMode
                                                                                        ? 'text-light'
                                                                                        : 'text-dark'
                                                                                "
                                                                                :href="
                                                                                    `https://doi.org/${getWorkflow.config.doi}`
                                                                                "
                                                                                >{{
                                                                                    getWorkflow
                                                                                        .config
                                                                                        .doi
                                                                                }}</b-link
                                                                            >
                                                                            <b-list-group
                                                                                v-else
                                                                            >
                                                                                <b-list-group-item
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'light'
                                                                                    "
                                                                                    v-for="doi in getWorkflow
                                                                                        .config
                                                                                        .doi"
                                                                                    v-bind:key="
                                                                                        doi
                                                                                    "
                                                                                    ><b-link
                                                                                        class="
                                                        text-dark
                                                    "
                                                                                        :href="
                                                                                            `https://doi.org/${doi}`
                                                                                        "
                                                                                        >{{
                                                                                            doi
                                                                                        }}</b-link
                                                                                    ></b-list-group-item
                                                                                >
                                                                            </b-list-group>
                                                                        </b-col>
                                                                    </b-row>
                                                                </b-col>
                                                            </b-row>
                                                        </div>
                                                        <hr
                                                            class="mt-2 mb-2"
                                                            style="border-color: gray"
                                                        />
                                                        <div>
                                                            <h5
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'text-light'
                                                                        : 'text-dark'
                                                                "
                                                            >
                                                                Configuration
                                                            </h5>
                                                            <b-row>
                                                                <b-col>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <small
                                                                                >Image</small
                                                                            >
                                                                        </b-col>
                                                                        <b-col
                                                                            cols="10"
                                                                        >
                                                                            <b
                                                                                >{{
                                                                                    getWorkflow
                                                                                        .config
                                                                                        .image
                                                                                }}</b
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <small
                                                                                >GPU</small
                                                                            >
                                                                        </b-col>
                                                                        <b-col
                                                                            cols="10"
                                                                        >
                                                                            {{
                                                                                getWorkflow
                                                                                    .config
                                                                                    .gpu
                                                                                    ? 'Yes'
                                                                                    : 'No'
                                                                            }}
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <small
                                                                                >Mount</small
                                                                            >
                                                                        </b-col>
                                                                        <b-col
                                                                            cols="10"
                                                                        >
                                                                            {{
                                                                                getWorkflow
                                                                                    .config
                                                                                    .mount
                                                                                    ? getWorkflow
                                                                                          .config
                                                                                          .mount
                                                                                    : 'None'
                                                                            }}
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <small
                                                                                >Parameters</small
                                                                            >
                                                                        </b-col>
                                                                        <b-col
                                                                            cols="10"
                                                                        >
                                                                            <b
                                                                                >{{
                                                                                    getWorkflow
                                                                                        .config
                                                                                        .params
                                                                                        ? getWorkflow
                                                                                              .config
                                                                                              .params
                                                                                              .length
                                                                                        : 'None'
                                                                                }}</b
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <small
                                                                                >Command</small
                                                                            >
                                                                        </b-col>
                                                                        <b-col
                                                                            cols="10"
                                                                        >
                                                                            <b
                                                                                ><code
                                                                                    >{{
                                                                                        ' ' +
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .commands
                                                                                    }}</code
                                                                                ></b
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row
                                                                        v-if="
                                                                            getWorkflow
                                                                                .config
                                                                                .input !==
                                                                                undefined
                                                                        "
                                                                    >
                                                                        <b-col>
                                                                            <small
                                                                                >Input</small
                                                                            >
                                                                        </b-col>
                                                                        <b-col
                                                                            cols="10"
                                                                        >
                                                                            <b
                                                                                ><code
                                                                                    >[working
                                                                                    directory]/input/{{
                                                                                        getWorkflow
                                                                                            .config
                                                                                            .input
                                                                                            .filetypes
                                                                                            ? '[' +
                                                                                              (getWorkflow
                                                                                                  .config
                                                                                                  .input
                                                                                                  .filetypes
                                                                                                  ? '*.' +
                                                                                                    getWorkflow.config.input.filetypes.join(
                                                                                                        ', *.'
                                                                                                    )
                                                                                                  : []) +
                                                                                              ']'
                                                                                            : ''
                                                                                    }}</code
                                                                                ></b
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row
                                                                        v-if="
                                                                            getWorkflow
                                                                                .config
                                                                                .output !==
                                                                                undefined
                                                                        "
                                                                    >
                                                                        <b-col>
                                                                            <small
                                                                                >Output</small
                                                                            >
                                                                        </b-col>
                                                                        <b-col
                                                                            cols="10"
                                                                        >
                                                                            <b
                                                                                ><code
                                                                                    >[working
                                                                                    directory]/{{
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
                                                                                        getWorkflow
                                                                                            .config
                                                                                            .output
                                                                                            .include
                                                                                            ? '[' +
                                                                                              (getWorkflow
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
                                                                                            : ''
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
                                                                                            : '' +
                                                                                              ']'
                                                                                    }}
                                                                                </code></b
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                </b-col>
                                                            </b-row>
                                                            <hr
                                                                class="mt-2 mb-2"
                                                                style="border-color: gray"
                                                            />
                                                            <h5
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'text-light'
                                                                        : 'text-dark'
                                                                "
                                                            >
                                                                Resource
                                                                Requests
                                                            </h5>
                                                            <b-row>
                                                                <b-col
                                                                    align-self="end"
                                                                    md="auto"
                                                                    class="text-right"
                                                                    v-if="
                                                                        !getWorkflow
                                                                            .config
                                                                            .resources
                                                                    "
                                                                >
                                                                    <b-alert
                                                                        show
                                                                        variant="warning"
                                                                        >This
                                                                        workflow
                                                                        does not
                                                                        specify
                                                                        resource
                                                                        requests
                                                                        and can
                                                                        only be
                                                                        submitted
                                                                        to
                                                                        agents
                                                                        configured
                                                                        for the
                                                                        <b
                                                                            >Local</b
                                                                        >
                                                                        executor.</b-alert
                                                                    >
                                                                </b-col>
                                                                <b-col
                                                                    align-self="end"
                                                                    class="text-left"
                                                                    v-else
                                                                >
                                                                    <b-row>
                                                                        <b-col>
                                                                            <b
                                                                                ><code
                                                                                    >{{
                                                                                        ' ' +
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .resources
                                                                                                .time
                                                                                    }}</code
                                                                                ></b
                                                                            >
                                                                            <small>
                                                                                time</small
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <b
                                                                                ><code
                                                                                    >{{
                                                                                        ' ' +
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .resources
                                                                                                .mem
                                                                                    }}</code
                                                                                ></b
                                                                            >
                                                                            <small>
                                                                                memory</small
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <b
                                                                                ><code
                                                                                    >{{
                                                                                        ' ' +
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .resources
                                                                                                .processes
                                                                                    }}</code
                                                                                ></b
                                                                            >
                                                                            <small>
                                                                                process(es)</small
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                    <b-row>
                                                                        <b-col>
                                                                            <b
                                                                                ><code
                                                                                    >{{
                                                                                        ' ' +
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .resources
                                                                                                .cores
                                                                                    }}</code
                                                                                ></b
                                                                            >
                                                                            <small>
                                                                                core(s)</small
                                                                            >
                                                                        </b-col>
                                                                    </b-row>
                                                                </b-col>
                                                            </b-row>
                                                        </div>
                                                        <div
                                                            v-if="
                                                                getWorkflow.readme !==
                                                                    undefined &&
                                                                    getWorkflow.readme !==
                                                                        null
                                                            "
                                                        >
                                                            <div
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'theme-container-get_readme m-0 p-3'
                                                                        : 'theme-container-light m-0 p-3'
                                                                "
                                                            >
                                                                <br />
                                                                <b-row>
                                                                    <b-col
                                                                        ><vue-markdown
                                                                            >{{
                                                                                getWorkflow.readme
                                                                            }}</vue-markdown
                                                                        ></b-col
                                                                    >
                                                                </b-row>
                                                            </div>
                                                        </div>
                                                    </b-col>
                                                </b-row>
                                            </b-tab>
                                            <b-tab
                                                title="Submit"
                                                :title-link-class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark m-0 p-3'
                                                        : 'theme-light m-0 p-3'
                                                "
                                                ><b-row>
                                                    <b-col>
                                                        <b-card-group
                                                            deck
                                                            columns
                                                        >
                                                            <b-card
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
                                                                        ? 'dark'
                                                                        : 'white'
                                                                "
                                                                :text-variant="
                                                                    profile.darkMode
                                                                        ? 'white'
                                                                        : 'dark'
                                                                "
                                                                style="min-width: 60rem"
                                                                class="mb-4"
                                                                ><b-row
                                                                    ><b-col
                                                                        ><h4
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-light'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            <i
                                                                                v-if="
                                                                                    nameValid
                                                                                "
                                                                                class="fas fa-pen fa-fw text-success"
                                                                            ></i
                                                                            ><i
                                                                                v-else
                                                                                class="fas fa-pen fa-fw"
                                                                            ></i>
                                                                            Name
                                                                        </h4>
                                                                    </b-col>
                                                                    <b-col
                                                                        md="auto"
                                                                        ><h5
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            {{
                                                                                taskName
                                                                            }}
                                                                            <i
                                                                                v-if="
                                                                                    nameValid
                                                                                "
                                                                                class="fas fa-check text-success fa-fw"
                                                                            ></i>
                                                                            <span
                                                                                class="text-danger"
                                                                                v-if="
                                                                                    taskNameExists
                                                                                "
                                                                                >Duplicate
                                                                                name</span
                                                                            >
                                                                            <i
                                                                                v-if="
                                                                                    !nameValid
                                                                                "
                                                                                class="fas fa-exclamation text-danger fa-fw"
                                                                            ></i></h5
                                                                    ></b-col>
                                                                </b-row>
                                                                <b-row
                                                                    ><b-col
                                                                        ><b
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            Provide
                                                                            a
                                                                            name
                                                                            for
                                                                            this
                                                                            task.
                                                                        </b>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-row
                                                                    class="mt-1"
                                                                >
                                                                    <b-col>
                                                                        <b-form-input
                                                                            v-model="
                                                                                taskName
                                                                            "
                                                                            placeholder="Type a name..."
                                                                        ></b-form-input>
                                                                    </b-col>
                                                                </b-row>
                                                            </b-card>
                                                            <b-card
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
                                                                        ? 'dark'
                                                                        : 'white'
                                                                "
                                                                :text-variant="
                                                                    profile.darkMode
                                                                        ? 'white'
                                                                        : 'dark'
                                                                "
                                                                style="min-width: 60rem"
                                                                class="mb-4"
                                                            >
                                                                <b-row>
                                                                    <b-col>
                                                                        <h4
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            <i
                                                                                v-if="
                                                                                    tags.length >
                                                                                        0
                                                                                "
                                                                                class="fas fa-tags fa-fw text-success"
                                                                            ></i>
                                                                            <i
                                                                                v-else
                                                                                class="fas fa-tags fa-fw"
                                                                            ></i>
                                                                            Tags
                                                                        </h4>
                                                                    </b-col>
                                                                    <b-col
                                                                        md="auto"
                                                                        ><h5
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            {{
                                                                                tags.length
                                                                            }}
                                                                            <i
                                                                                v-if="
                                                                                    tags.length >
                                                                                        0
                                                                                "
                                                                                class="fas fa-check text-success fa-fw"
                                                                            ></i></h5
                                                                    ></b-col>
                                                                </b-row>
                                                                <b-row
                                                                    ><b-col
                                                                        ><b
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            Attach
                                                                            tags
                                                                            to
                                                                            this
                                                                            task.
                                                                        </b>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-row
                                                                    class="mt-1"
                                                                >
                                                                    <b-col>
                                                                        <multiselect
                                                                            style="z-index: 100"
                                                                            v-model="
                                                                                tags
                                                                            "
                                                                            mode="tags"
                                                                            :multiple="
                                                                                true
                                                                            "
                                                                            :close-on-select="
                                                                                false
                                                                            "
                                                                            :clear-on-select="
                                                                                false
                                                                            "
                                                                            :preserve-search="
                                                                                true
                                                                            "
                                                                            :options="
                                                                                tagOptions
                                                                            "
                                                                            :taggable="
                                                                                true
                                                                            "
                                                                            placeholder="Add tags..."
                                                                            :createTag="
                                                                                true
                                                                            "
                                                                            :appendNewTag="
                                                                                true
                                                                            "
                                                                            :searchable="
                                                                                true
                                                                            "
                                                                            @tag="
                                                                                addTag
                                                                            "
                                                                        >
                                                                        </multiselect>
                                                                    </b-col>
                                                                </b-row>
                                                            </b-card>
                                                            <b-card
                                                                v-if="
                                                                    workflow !==
                                                                        null &&
                                                                    getWorkflow
                                                                        .config
                                                                        .params !==
                                                                        undefined
                                                                        ? getWorkflow
                                                                              .config
                                                                              .params
                                                                              .length !==
                                                                          0
                                                                        : false
                                                                "
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
                                                                        ? 'dark'
                                                                        : 'white'
                                                                "
                                                                :text-variant="
                                                                    profile.darkMode
                                                                        ? 'white'
                                                                        : 'dark'
                                                                "
                                                                style="min-width: 40rem"
                                                                class="mb-4"
                                                            >
                                                                <b-row>
                                                                    <b-col>
                                                                        <h4
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            <i
                                                                                v-if="
                                                                                    params &&
                                                                                        params.every(
                                                                                            p =>
                                                                                                p.name !==
                                                                                                ''
                                                                                        )
                                                                                "
                                                                                class="fas fa-keyboard fa-fw text-success"
                                                                            ></i>
                                                                            <i
                                                                                v-else
                                                                                class="fas fa-keyboard fa-fw"
                                                                            ></i>
                                                                            Parameters
                                                                        </h4> </b-col
                                                                    ><b-col
                                                                        md="auto"
                                                                        ><h5
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            <span
                                                                                v-if="
                                                                                    paramsValid
                                                                                "
                                                                                >{{
                                                                                    params.length
                                                                                }}</span
                                                                            >
                                                                            <i
                                                                                v-if="
                                                                                    paramsValid
                                                                                "
                                                                                class="fas fa-check text-success fa-fw"
                                                                            ></i>
                                                                            <i
                                                                                v-else
                                                                                class="fas fa-exclamation text-danger fa-fw"
                                                                            ></i></h5
                                                                    ></b-col>
                                                                </b-row>
                                                                <b-row
                                                                    ><b-col
                                                                        ><b
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            Configure
                                                                            parameters
                                                                            for
                                                                            this
                                                                            task.
                                                                        </b>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-row
                                                                    ><b-col>
                                                                        <b-row
                                                                            class="mt-1"
                                                                            v-for="param in params"
                                                                            v-bind:key="
                                                                                param.name
                                                                            "
                                                                        >
                                                                            <b-col
                                                                                >{{
                                                                                    param.name.toLowerCase()
                                                                                }}</b-col
                                                                            ><b-col>
                                                                                <b-form-input
                                                                                    v-if="
                                                                                        param.type ===
                                                                                            'string'
                                                                                    "
                                                                                    size="sm"
                                                                                    v-model="
                                                                                        param.value
                                                                                    "
                                                                                    :placeholder="
                                                                                        param.value ===
                                                                                        ''
                                                                                            ? 'Enter a value for \'' +
                                                                                              param.name.toLowerCase() +
                                                                                              '\''
                                                                                            : param.value
                                                                                    "
                                                                                ></b-form-input>
                                                                                <b-form-select
                                                                                    v-if="
                                                                                        param.type ===
                                                                                            'select'
                                                                                    "
                                                                                    size="sm"
                                                                                    v-model="
                                                                                        param.value
                                                                                    "
                                                                                    :options="
                                                                                        param.options
                                                                                    "
                                                                                ></b-form-select>
                                                                                <b-form-checkbox-group
                                                                                    v-if="
                                                                                        param.type ===
                                                                                            'multiselect'
                                                                                    "
                                                                                    size="sm"
                                                                                    v-model="
                                                                                        param.value
                                                                                    "
                                                                                    :options="
                                                                                        param.options
                                                                                    "
                                                                                ></b-form-checkbox-group>
                                                                                <b-form-spinbutton
                                                                                    v-if="
                                                                                        param.type ===
                                                                                            'number'
                                                                                    "
                                                                                    size="sm"
                                                                                    v-model="
                                                                                        param.value
                                                                                    "
                                                                                    :min="
                                                                                        param.min
                                                                                    "
                                                                                    :max="
                                                                                        param.max
                                                                                    "
                                                                                    :step="
                                                                                        param.step
                                                                                    "
                                                                                ></b-form-spinbutton>
                                                                                <b-form-checkbox
                                                                                    v-if="
                                                                                        param.type ===
                                                                                            'boolean'
                                                                                    "
                                                                                    size="sm"
                                                                                    v-model="
                                                                                        param.value
                                                                                    "
                                                                                    switch
                                                                                >
                                                                                    <b>
                                                                                        {{
                                                                                            param.value
                                                                                        }}</b
                                                                                    >
                                                                                </b-form-checkbox>
                                                                            </b-col></b-row
                                                                        >
                                                                    </b-col></b-row
                                                                >
                                                            </b-card>
                                                            <b-card
                                                                v-if="
                                                                    workflow !==
                                                                        null &&
                                                                        getWorkflow
                                                                            .config
                                                                            .input !==
                                                                            undefined &&
                                                                        getWorkflow
                                                                            .config
                                                                            .input
                                                                            .path !==
                                                                            undefined &&
                                                                        input.kind !==
                                                                            undefined &&
                                                                        input.kind !==
                                                                            null &&
                                                                        input
                                                                            .kind
                                                                            .length >
                                                                            0
                                                                "
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
                                                                        ? 'dark'
                                                                        : 'white'
                                                                "
                                                                :text-variant="
                                                                    profile.darkMode
                                                                        ? 'white'
                                                                        : 'dark'
                                                                "
                                                                style="min-width: 50rem"
                                                                class="mb-4"
                                                            >
                                                                <b-row>
                                                                    <b-col>
                                                                        <h4
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            <i
                                                                                v-if="
                                                                                    inputValid
                                                                                "
                                                                                class="fas fa-download fa-fw text-success"
                                                                            ></i>
                                                                            <i
                                                                                v-else
                                                                                class="fas fa-download fa-fw"
                                                                            ></i>
                                                                            Input
                                                                            {{
                                                                                this.input.kind[0].toUpperCase() +
                                                                                    this.input.kind.substr(
                                                                                        1
                                                                                    )
                                                                            }}
                                                                        </h4>
                                                                    </b-col>
                                                                    <b-col
                                                                        md="auto"
                                                                        ><h5
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            <span
                                                                                v-if="
                                                                                    inputValid
                                                                                "
                                                                                >{{
                                                                                    selectedDataset.path
                                                                                }}<i
                                                                                    class="fas fa-check text-success fa-fw"
                                                                                ></i
                                                                            ></span>
                                                                            <i
                                                                                v-else
                                                                                class="fas fa-exclamation text-danger fa-fw"
                                                                            ></i></h5
                                                                    ></b-col>
                                                                </b-row>

                                                                <div>
                                                                    <b
                                                                        :class="
                                                                            profile.darkMode
                                                                                ? 'text-white'
                                                                                : 'text-dark'
                                                                        "
                                                                    >
                                                                        Select a
                                                                        public
                                                                        {{
                                                                            this
                                                                                .input
                                                                                .kind ===
                                                                            'files'
                                                                                ? 'directory'
                                                                                : this
                                                                                      .input
                                                                                      .kind
                                                                        }}
                                                                        from the
                                                                        Data
                                                                        Commons
                                                                        or your
                                                                        own
                                                                        {{
                                                                            this
                                                                                .input
                                                                                .kind ===
                                                                            'files'
                                                                                ? 'directory'
                                                                                : this
                                                                                      .input
                                                                                      .kind
                                                                        }}
                                                                        from the
                                                                        Data
                                                                        Store.
                                                                    </b>
                                                                    <b-tabs
                                                                        class="mt-2"
                                                                        pills
                                                                        nav-class="bg-transparent"
                                                                        active-nav-item-class="bg-info text-dark"
                                                                    >
                                                                        <b-tab
                                                                            active
                                                                            title="Personal"
                                                                            :title-link-class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'theme-dark m-0 p-3'
                                                                                    : 'theme-light m-0 p-3'
                                                                            "
                                                                        >
                                                                            <b-row
                                                                                v-if="
                                                                                    personalDatasetsLoading
                                                                                "
                                                                                align-v="center"
                                                                                align-h="center"
                                                                            >
                                                                                <b-col
                                                                                    align-self="end"
                                                                                >
                                                                                    <b-spinner
                                                                                        type="grow"
                                                                                        variant="secondary"
                                                                                    ></b-spinner> </b-col
                                                                            ></b-row>
                                                                            <b-row
                                                                                v-else
                                                                            >
                                                                                <b-col>
                                                                                    <datatree
                                                                                        :select="
                                                                                            input.kind
                                                                                        "
                                                                                        :upload="
                                                                                            true
                                                                                        "
                                                                                        :download="
                                                                                            true
                                                                                        "
                                                                                        @selectNode="
                                                                                            inputSelected
                                                                                        "
                                                                                        :node="
                                                                                            personalDatasets
                                                                                        "
                                                                                    ></datatree></b-col
                                                                            ></b-row>
                                                                        </b-tab>
                                                                        <b-tab
                                                                            title="Shared"
                                                                            :title-link-class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'theme-dark m-0 p-3'
                                                                                    : 'theme-light m-0 p-3'
                                                                            "
                                                                        >
                                                                            <b-row
                                                                                v-if="
                                                                                    sharedDatasetsLoading
                                                                                "
                                                                                align-v="center"
                                                                                align-h="center"
                                                                            >
                                                                                <b-col
                                                                                    align-self="end"
                                                                                    ><b-spinner
                                                                                        type="grow"
                                                                                        variant="secondary"
                                                                                    ></b-spinner></b-col
                                                                            ></b-row>
                                                                            <b-row
                                                                                v-else
                                                                            >
                                                                                <b-col>
                                                                                    <datatree
                                                                                        :select="
                                                                                            input.kind
                                                                                        "
                                                                                        :upload="
                                                                                            true
                                                                                        "
                                                                                        :download="
                                                                                            true
                                                                                        "
                                                                                        @selectNode="
                                                                                            inputSelected
                                                                                        "
                                                                                        :node="
                                                                                            sharedDatasets
                                                                                        "
                                                                                    ></datatree>
                                                                                    <!--<datatree
                            v-for="node in sharedDatasets"
                            v-bind:key="node.path"
                            v-bind:node="node"
                            :select="kind"
                            @selectNode="inputSelected"
                            :upload="true"
                            :download="true"
                            :class="
                                profile.darkMode ? 'theme-dark' : 'theme-light'
                            "
                        ></datatree>--></b-col
                                                                                ></b-row
                                                                            ></b-tab
                                                                        >
                                                                        <b-tab
                                                                            title="Public"
                                                                            :title-link-class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'theme-dark m-0 p-3'
                                                                                    : 'theme-light m-0 p-3'
                                                                            "
                                                                        >
                                                                            <b-row
                                                                                v-if="
                                                                                    publicDatasetsLoading
                                                                                "
                                                                                align-v="center"
                                                                                align-h="center"
                                                                            >
                                                                                <b-col
                                                                                    align-self="end"
                                                                                >
                                                                                    <b-spinner
                                                                                        type="grow"
                                                                                        variant="secondary"
                                                                                    ></b-spinner> </b-col
                                                                            ></b-row>
                                                                            <b-row
                                                                                v-else
                                                                                ><b-col>
                                                                                    <datatree
                                                                                        :select="
                                                                                            input.kind
                                                                                        "
                                                                                        :upload="
                                                                                            true
                                                                                        "
                                                                                        :download="
                                                                                            true
                                                                                        "
                                                                                        @selectNode="
                                                                                            inputSelected
                                                                                        "
                                                                                        :node="
                                                                                            publicDatasets
                                                                                        "
                                                                                    ></datatree></b-col
                                                                            ></b-row>
                                                                        </b-tab>
                                                                    </b-tabs>
                                                                </div>
                                                                <b-row
                                                                    v-if="
                                                                        input
                                                                            .filetypes
                                                                            .length >
                                                                            0
                                                                    "
                                                                >
                                                                    <b-col>
                                                                        <b
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            Select
                                                                            one
                                                                            or
                                                                            more
                                                                            input
                                                                            filetypes.
                                                                        </b>
                                                                        <multiselect
                                                                            :multiple="
                                                                                true
                                                                            "
                                                                            :close-on-select="
                                                                                false
                                                                            "
                                                                            :clear-on-select="
                                                                                false
                                                                            "
                                                                            :preserve-search="
                                                                                true
                                                                            "
                                                                            :preselect-first="
                                                                                true
                                                                            "
                                                                            v-model="
                                                                                inputSelectedPatterns
                                                                            "
                                                                            :options="
                                                                                input.filetypes
                                                                            "
                                                                        ></multiselect>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-alert
                                                                    class="mt-1"
                                                                    :variant="
                                                                        inputFiletypeSelected
                                                                            ? 'success'
                                                                            : 'danger'
                                                                    "
                                                                    :show="true"
                                                                    >Selected:
                                                                    {{
                                                                        inputFiletypeSelected
                                                                            ? '*.' +
                                                                              inputSelectedPatterns.join(
                                                                                  ', *.'
                                                                              )
                                                                            : 'None'
                                                                    }}
                                                                    <i
                                                                        v-if="
                                                                            inputFiletypeSelected
                                                                        "
                                                                        class="fas fa-check text-success"
                                                                    ></i>
                                                                    <i
                                                                        v-else
                                                                        class="fas fa-exclamation text-danger"
                                                                    ></i>
                                                                </b-alert>
                                                            </b-card>
                                                            <!--<b-card
                                    v-if="
                                        getWorkflow !== null &&
                                            getWorkflow.config !== undefined &&
                                            getWorkflow.config.input !==
                                                undefined &&
                                            getWorkflow.config.output !== undefined
                                    "
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    style="min-width: 50rem"
                                    class="mb-4"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="outputDataset"
                                                    class="fas fa-upload fa-fw text-success"
                                                ></i>
                                                <i
                                                    v-else-if="
                                                        !outputDataset &&
                                                            profile.darkMode
                                                    "
                                                    class="fas fa-upload fa-fw text-white"
                                                ></i>
                                                <i
                                                    v-else-if="
                                                        !outputDataset &&
                                                            !profile.darkMode
                                                    "
                                                    class="fas fa-upload fa-fw text-dark"
                                                ></i>
                                                Output Sync
                                                {{
                                                    outputDataset
                                                        ? ''
                                                        : ' (off)'
                                                }}
                                            </h4>
                                        </b-col>
                                        <b-col md="auto">
                                            <b-form-checkbox
                                                v-model="outputSync"
                                                switch
                                                size="md"
                                            >
                                            </b-form-checkbox>
                                        </b-col>
                                    </b-row>
                                    <runoutput
                                        v-if="outputDataset"
                                        :user="user"
                                        v-on:outputSelected="outputSelected"
                                    ></runoutput>
                                </b-card>-->
                                                            <b-card
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
                                                                        ? 'dark'
                                                                        : 'white'
                                                                "
                                                                :text-variant="
                                                                    profile.darkMode
                                                                        ? 'white'
                                                                        : 'dark'
                                                                "
                                                                style="min-width: 40rem"
                                                                class="mb-4"
                                                            >
                                                                <b-row>
                                                                    <b-col>
                                                                        <h4
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            <i
                                                                                v-if="
                                                                                    selectedAgent.name !==
                                                                                        ''
                                                                                "
                                                                                class="fas fa-robot fa-fw text-success"
                                                                            ></i>
                                                                            <i
                                                                                v-else
                                                                                class="fas fa-robot fa-fw"
                                                                            ></i>
                                                                            Agent
                                                                        </h4>
                                                                    </b-col>
                                                                    <b-col
                                                                        md="auto"
                                                                        ><h5
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            {{
                                                                                selectedAgent.name !==
                                                                                ''
                                                                                    ? selectedAgent.name
                                                                                    : ''
                                                                            }}<i
                                                                                v-if="
                                                                                    selectedAgent.name !==
                                                                                        ''
                                                                                "
                                                                                class="fas fa-check text-success fa-fw"
                                                                            ></i>
                                                                            <i
                                                                                v-else
                                                                                class="fas fa-exclamation text-danger fa-fw"
                                                                            ></i></h5
                                                                    ></b-col>
                                                                </b-row>
                                                                <div>
                                                                    <b
                                                                        :class="
                                                                            profile.darkMode
                                                                                ? 'text-white'
                                                                                : 'text-dark'
                                                                        "
                                                                    >
                                                                        Select
                                                                        an agent
                                                                        to
                                                                        submit
                                                                        this
                                                                        task to.
                                                                    </b>
                                                                    <b-tabs
                                                                        class="mt-2"
                                                                        pills
                                                                        nav-class="bg-transparent"
                                                                        active-nav-item-class="bg-info text-dark"
                                                                    >
                                                                        <b-tab
                                                                            title="Personal"
                                                                            :title-link-class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'theme-dark m-0 p-3'
                                                                                    : 'theme-light m-0 p-3'
                                                                            "
                                                                        >
                                                                            <b-row
                                                                                align-h="center"
                                                                                v-if="
                                                                                    personalAgentsLoading
                                                                                "
                                                                            >
                                                                                <b-spinner
                                                                                    type="grow"
                                                                                    label="Loading..."
                                                                                    variant="secondary"
                                                                                ></b-spinner>
                                                                            </b-row>
                                                                            <b-row
                                                                                align-h="center"
                                                                                class="text-center"
                                                                                v-else-if="
                                                                                    personalAgents.length ===
                                                                                        0
                                                                                "
                                                                            >
                                                                                <b-col>
                                                                                    None
                                                                                    to
                                                                                    show.
                                                                                </b-col>
                                                                            </b-row>
                                                                            <div
                                                                                v-else
                                                                            >
                                                                                <b-row
                                                                                    class="text-right"
                                                                                    v-for="agent in personalAgents"
                                                                                    v-bind:key="
                                                                                        agent.name
                                                                                    "
                                                                                >
                                                                                    <b-col
                                                                                        md="auto"
                                                                                        ><b-button
                                                                                            size="md"
                                                                                            class="text-left pt-2"
                                                                                            @click="
                                                                                                agentSelected(
                                                                                                    agent
                                                                                                )
                                                                                            "
                                                                                            :variant="
                                                                                                profile.darkMode
                                                                                                    ? 'dark'
                                                                                                    : 'white'
                                                                                            "
                                                                                            :disabled="
                                                                                                agentUnsupported(
                                                                                                    agent
                                                                                                ) ||
                                                                                                    agent.disabled
                                                                                            "
                                                                                            >{{
                                                                                                agent.name
                                                                                            }}</b-button
                                                                                        ></b-col
                                                                                    >
                                                                                    <b-col
                                                                                        align-self="end"
                                                                                    >
                                                                                        <small
                                                                                            >{{
                                                                                                agent.max_cores
                                                                                            }}
                                                                                            cores,
                                                                                            {{
                                                                                                agent.max_processes
                                                                                            }}
                                                                                            processes,
                                                                                            <span
                                                                                                v-if="
                                                                                                    parseInt(
                                                                                                        agent.max_mem
                                                                                                    ) >=
                                                                                                        parseInt(
                                                                                                            getWorkflow
                                                                                                                .config
                                                                                                                .resources
                                                                                                                .mem
                                                                                                        ) &&
                                                                                                        parseInt(
                                                                                                            agent.max_mem
                                                                                                        ) >
                                                                                                            0
                                                                                                "
                                                                                                >{{
                                                                                                    agent.max_mem
                                                                                                }}
                                                                                                GB
                                                                                                memory</span
                                                                                            >
                                                                                            <span
                                                                                                v-else-if="
                                                                                                    parseInt(
                                                                                                        agent.max_mem
                                                                                                    ) >
                                                                                                        0
                                                                                                "
                                                                                                class="text-danger"
                                                                                                >{{
                                                                                                    agent.max_mem
                                                                                                }}
                                                                                                GB
                                                                                                memory</span
                                                                                            >
                                                                                            <span
                                                                                                v-else-if="
                                                                                                    parseInt(
                                                                                                        agent.max_mem
                                                                                                    ) ===
                                                                                                        -1
                                                                                                "
                                                                                                >virtual
                                                                                                memory</span
                                                                                            ><span
                                                                                                v-if="
                                                                                                    agent.gpu
                                                                                                "
                                                                                            >
                                                                                                ,
                                                                                                GPU
                                                                                            </span>
                                                                                            <span
                                                                                                v-else
                                                                                                >,
                                                                                                No
                                                                                                GPU
                                                                                            </span></small
                                                                                        ></b-col
                                                                                    >
                                                                                </b-row>
                                                                            </div>
                                                                        </b-tab>
                                                                        <b-tab
                                                                            title="Public"
                                                                            :title-link-class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'theme-dark m-0 p-3'
                                                                                    : 'theme-light m-0 p-3'
                                                                            "
                                                                        >
                                                                            <b-row
                                                                                align-h="center"
                                                                                v-if="
                                                                                    publicAgentsLoading
                                                                                "
                                                                            >
                                                                                <b-spinner
                                                                                    type="grow"
                                                                                    label="Loading..."
                                                                                    variant="secondary"
                                                                                ></b-spinner>
                                                                            </b-row>
                                                                            <b-row
                                                                                align-h="center"
                                                                                class="text-center"
                                                                                v-else-if="
                                                                                    publicAgents.length ===
                                                                                        0
                                                                                "
                                                                            >
                                                                                <b-col>
                                                                                    None
                                                                                    to
                                                                                    show.
                                                                                </b-col>
                                                                            </b-row>
                                                                            <div
                                                                                v-else
                                                                            >
                                                                                <b-row
                                                                                    class="text-right"
                                                                                    v-for="agent in publicAgents"
                                                                                    v-bind:key="
                                                                                        agent.name
                                                                                    "
                                                                                >
                                                                                    <b-col
                                                                                        md="auto"
                                                                                        ><b-button
                                                                                            size="md"
                                                                                            class="text-left pt-2"
                                                                                            @click="
                                                                                                agentSelected(
                                                                                                    agent
                                                                                                )
                                                                                            "
                                                                                            :variant="
                                                                                                profile.darkMode
                                                                                                    ? 'dark'
                                                                                                    : 'white'
                                                                                            "
                                                                                            :disabled="
                                                                                                agentUnsupported(
                                                                                                    agent
                                                                                                ) ||
                                                                                                    agent.disabled
                                                                                            "
                                                                                            >{{
                                                                                                agent.name
                                                                                            }}</b-button
                                                                                        ></b-col
                                                                                    >
                                                                                    <b-col
                                                                                        align-self="end"
                                                                                    >
                                                                                        <small
                                                                                            >{{
                                                                                                agent.max_cores
                                                                                            }}
                                                                                            cores,
                                                                                            {{
                                                                                                agent.max_processes
                                                                                            }}
                                                                                            processes, </small
                                                                                        ><span
                                                                                            v-if="
                                                                                                parseInt(
                                                                                                    agent.max_mem
                                                                                                ) >=
                                                                                                    parseInt(
                                                                                                        getWorkflow
                                                                                                            .config
                                                                                                            .resources
                                                                                                            .mem
                                                                                                    ) &&
                                                                                                    parseInt(
                                                                                                        agent.max_mem
                                                                                                    ) >
                                                                                                        0
                                                                                            "
                                                                                            >{{
                                                                                                agent.max_mem
                                                                                            }}
                                                                                            GB
                                                                                            memory</span
                                                                                        >
                                                                                        <span
                                                                                            v-else-if="
                                                                                                parseInt(
                                                                                                    agent.max_mem
                                                                                                ) >
                                                                                                    0
                                                                                            "
                                                                                            class="text-danger"
                                                                                            >{{
                                                                                                agent.max_mem
                                                                                            }}
                                                                                            GB
                                                                                            memory</span
                                                                                        >
                                                                                        <span
                                                                                            v-else-if="
                                                                                                parseInt(
                                                                                                    agent.max_mem
                                                                                                ) ===
                                                                                                    -1
                                                                                            "
                                                                                            >virtual
                                                                                            memory</span
                                                                                        ><span
                                                                                            v-if="
                                                                                                agent.gpu
                                                                                            "
                                                                                        >
                                                                                            ,
                                                                                            GPU
                                                                                        </span>
                                                                                        <span
                                                                                            v-else
                                                                                            >,
                                                                                            No
                                                                                            GPU
                                                                                        </span></b-col
                                                                                    >
                                                                                </b-row>
                                                                            </div>
                                                                        </b-tab>
                                                                    </b-tabs>
                                                                </div>
                                                            </b-card>
                                                        </b-card-group>
                                                    </b-col>
                                                </b-row>
                                                <b-row
                                                    ><b-col
                                                        md="auto"
                                                        class="mr-0"
                                                        align-self="end"
                                                    >
                                                        <b-input-group>
                                                            <template #prepend>
                                                                <b-input-group-text
                                                                    >Start
                                                                    {{
                                                                        getWorkflow
                                                                            .config
                                                                            .name
                                                                    }}</b-input-group-text
                                                                >
                                                            </template>
                                                            <template #append>
                                                                <b-dropdown
                                                                    variant="secondary"
                                                                    :text="
                                                                        submitType
                                                                    "
                                                                    v-model="
                                                                        submitType
                                                                    "
                                                                    block
                                                                >
                                                                    <template
                                                                        #button-content
                                                                    >
                                                                        {{
                                                                            submitType
                                                                        }}
                                                                        <i
                                                                            class="fas fa-caret-down fa-fw"
                                                                        ></i>
                                                                    </template>
                                                                    <b-dropdown-item
                                                                        @click="
                                                                            submitType =
                                                                                'Now'
                                                                        "
                                                                        >Now</b-dropdown-item
                                                                    >
                                                                    <!--<b-dropdown-item
                                            @click="submitType = 'After'"
                                            >After</b-dropdown-item
                                        >-->
                                                                    <!--<b-dropdown-item
                                                                        @click="
                                                                            submitType =
                                                                                'Every'
                                                                        "
                                                                        >Every</b-dropdown-item
                                                                    >-->
                                                                </b-dropdown>
                                                            </template>
                                                        </b-input-group>
                                                    </b-col>
                                                    <b-col
                                                        md="auto"
                                                        v-if="
                                                            submitType ===
                                                                'After' ||
                                                                submitType ===
                                                                    'Every'
                                                        "
                                                        ><b-input-group>
                                                            <b-form-spinbutton
                                                                v-model="
                                                                    delayValue
                                                                "
                                                                min="1"
                                                                max="100"
                                                            ></b-form-spinbutton
                                                            ><template #append>
                                                                <b-dropdown
                                                                    variant="secondary"
                                                                    :text="
                                                                        submitType
                                                                    "
                                                                    v-model="
                                                                        submitType
                                                                    "
                                                                    block
                                                                >
                                                                    <template
                                                                        #button-content
                                                                    >
                                                                        {{
                                                                            delayUnits
                                                                        }}
                                                                        <i
                                                                            class="fas fa-caret-down fa-fw"
                                                                        ></i>
                                                                    </template>
                                                                    <b-dropdown-item
                                                                        @click="
                                                                            delayUnits =
                                                                                'Seconds'
                                                                        "
                                                                        >Seconds</b-dropdown-item
                                                                    >
                                                                    <b-dropdown-item
                                                                        @click="
                                                                            delayUnits =
                                                                                'Minutes'
                                                                        "
                                                                        >Minutes</b-dropdown-item
                                                                    >
                                                                    <b-dropdown-item
                                                                        @click="
                                                                            delayUnits =
                                                                                'Hours'
                                                                        "
                                                                        >Hours</b-dropdown-item
                                                                    >
                                                                    <b-dropdown-item
                                                                        @click="
                                                                            delayUnits =
                                                                                'Days'
                                                                        "
                                                                        >Days</b-dropdown-item
                                                                    >
                                                                </b-dropdown>
                                                            </template></b-input-group
                                                        ></b-col
                                                    >
                                                    <b-col
                                                        ><b-button
                                                            :disabled="
                                                                !canSubmit ||
                                                                    submitted
                                                            "
                                                            @click="onTryStart"
                                                            variant="success"
                                                            block
                                                        >
                                                            Submit<b-spinner
                                                                small
                                                                v-if="submitted"
                                                                label="Loading..."
                                                                variant="dark"
                                                                class="ml-2 mb-1"
                                                            ></b-spinner> </b-button></b-col
                                                ></b-row>
                                            </b-tab>
                                            <!--<b-tab
                                                title="Runs"
                                                :title-link-class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark m-0 p-3'
                                                        : 'theme-light m-0 p-3'
                                                "
                                            >
                                                <b-row>
                                                    <b-row
                        ><b-col align-self="end"
                            ><h5 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                                Delayed Runs
                            </h5></b-col
                        ></b-row
                    >
                    <b-list-group class="text-left m-0 p-0">
                        <b-row v-if="delayedRuns.length === 0"
                            ><b-col
                                ><small
                                    >You haven't scheduled any delayed
                                    {{ flow.config.name }} tasks.</small
                                ></b-col
                            ></b-row
                        >
                        <b-list-group-item
                            variant="default"
                            style="box-shadow: -2px 2px 2px #adb5bd"
                            v-for="task in delayedRuns"
                            v-bind:key="task.id"
                            :class="
                                profile.darkMode
                                    ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                    : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                            "
                        >
                            <b-row class="pt-1">
                                <b-col align-self="end"
                                    >{{
                                        `After ${task.interval.every} ${task.interval.period} on ${task.agent.name}`
                                    }}<br /><b-row
                                        ><b-col
                                            md="auto"
                                            align-self="end"
                                            class="mb-1"
                                            ></b-col
                                        >
                                    </b-row></b-col
                                >
                                <b-col
                                    md="auto"
                                    align-self="start"
                                    class="mb-1"
                                    ><b-button
                                        size="sm"
                                        variant="outline-danger"
                                        @click="deleteDelayed(task)"
                                        ><i class="fas fa-trash fa-fw"></i>
                                        Cancel</b-button
                                    ></b-col
                                >
                            </b-row>
                        </b-list-group-item>
                    </b-list-group>
                    <hr
                                                    class="mt-2 mb-2"
                                                    style="border-color: gray"
                                                />

                                                    <b-row
                                                            ><b-col
                                                                align-self="end"
                                                                ><h5
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-white'
                                                                            : 'text-dark'
                                                                    "
                                                                >
                                                                    Periodic
                                                                    Runs
                                                                </h5></b-col
                                                            ></b-row
                                                        >
                                                        <b-list-group
                                                            class="text-left m-0 p-0"
                                                        >
                                                            <b-row
                                                                v-if="
                                                                    repeatingRuns.length ===
                                                                        0
                                                                "
                                                                ><b-col
                                                                    ><small
                                                                        >You
                                                                        haven't
                                                                        scheduled
                                                                        any
                                                                        repeating
                                                                        {{
                                                                            getWorkflow
                                                                                .config
                                                                                .name
                                                                        }}
                                                                        tasks.</small
                                                                    ></b-col
                                                                ></b-row
                                                            >
                                                            <b-list-group-item
                                                                variant="default"
                                                                style="box-shadow: -2px 2px 2px #adb5bd"
                                                                v-for="task in repeatingRuns"
                                                                v-bind:key="
                                                                    task.id
                                                                "
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                                                        : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                                                "
                                                            >
                                                                <b-row
                                                                    class="pt-1"
                                                                >
                                                                    <b-col
                                                                        >{{
                                                                            `Every ${task.interval.every} ${task.interval.period} on ${task.agent.name}`
                                                                        }}<br /><b-row
                                                                            ><b-col
                                                                                md="auto"
                                                                                align-self="end"
                                                                                class="mb-1"
                                                                                ><small v-if="task.enabled"
                                    >Next running {{ cronTime(task)
                                    }}<br /></small
                                ><small v-if="task.last_run !== null"
                                                                                    >Last
                                                                                    ran
                                                                                    {{
                                                                                        prettify(
                                                                                            task.last_run
                                                                                        )
                                                                                    }}</small
                                                                                ><small
                                                                                    v-else
                                                                                    >Task
                                                                                    has
                                                                                    not
                                                                                    run
                                                                                    yet</small
                                                                                ></b-col
                                                                            >
                                                                        </b-row></b-col
                                                                    >
                                                                    <b-col
                                                                        md="auto"
                                                                        align-self="start"
                                                                        ><b-form-checkbox
                                        class="text-right"
                                        v-model="task.enabled"
                                        @change="toggleRepeating(task)"
                                        switch
                                        size="md"
                                    >
                                    </b-form-checkbox
                                    ><b-button
                                                                            size="sm"
                                                                            variant="outline-danger"
                                                                            @click="
                                                                                deleteRepeating(
                                                                                    task
                                                                                )
                                                                            "
                                                                            ><i
                                                                                class="fas fa-trash fa-fw"
                                                                            ></i>
                                                                            Remove</b-button
                                                                        ></b-col
                                                                    >
                                                                </b-row>
                                                            </b-list-group-item>
                                                        </b-list-group>
                                                    </b-col>
                                                    <b-col>
                                                        <b-row
                                                            ><b-col
                                                                align-self="end"
                                                                ><h5
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-white'
                                                                            : 'text-dark'
                                                                    "
                                                                >
                                                                    Recent Runs
                                                                </h5></b-col
                                                            ><b-col class="mb-1" align-self="start" md="auto"
                            ><b-button
                                :variant="profile.darkMode ? 'outline-light' : 'white'"
                                size="sm"
                                v-b-tooltip.hover
                                title="Create Periodic Task"
                                :disabled="agent.role !== 'admin'"
                                v-b-modal.createTask
                            >
                                <i class="fas fa-plus fa-fw"></i>
                                Create
                            </b-button></b-col
                        ></b-row
                                                        >
                                                        <b-list-group
                                                            class="text-left m-0 p-0"
                                                        >
                                                            <b-row
                                                                v-if="
                                                                    taskHistory.length ===
                                                                        0
                                                                "
                                                                ><b-col
                                                                    ><small
                                                                        >You
                                                                        haven't
                                                                        run
                                                                        {{
                                                                            getWorkflow
                                                                                .config
                                                                                .name
                                                                        }}
                                                                        yet.</small
                                                                    ></b-col
                                                                ></b-row
                                                            >
                                                            <b-list-group-item
                                                                variant="default"
                                                                style="box-shadow: -2px 2px 2px #adb5bd"
                                                                v-for="task in taskHistory"
                                                                v-bind:key="
                                                                    task.guid
                                                                "
                                                                :class="
                                                                    profile.darkMode
                                                                        ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                                                        : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                                                "
                                                           >
                                                                <b-link
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-light'
                                                                            : 'text-dark'
                                                                    "
                                                                    :to="{
                                                                        name:
                                                                            'task',
                                                                        params: {
                                                                            owner:
                                                                                task.owner,
                                                                            name:
                                                                                task.name
                                                                        }
                                                                    }"
                                                                    >{{
                                                                        task.name
                                                                    }}</b-link
                                                                >
                                                                <br />
                                                                <b-badge
                                                                    v-for="tag in task.tags"
                                                                    v-bind:key="
                                                                        tag
                                                                    "
                                                                    class="mr-1"
                                                                    variant="secondary"
                                                                    >{{ tag }}
                                                                </b-badge>
                                                                <br
                                                                    v-if="
                                                                        task.tags
                                                                            .length >
                                                                            0
                                                                    "
                                                                />
                                                                <small
                                                                    v-if="
                                                                        !task.is_complete
                                                                    "
                                                                    >Running</small
                                                                >
                                                                <b-badge
                                                                    :variant="
                                                                        task.is_failure ||
                                                                        task.is_timeout
                                                                            ? 'danger'
                                                                            : task.is_cancelled
                                                                            ? 'secondary'
                                                                            : 'success'
                                                                    "
                                                                    v-else
                                                                    >{{
                                                                        task.job_status
                                                                    }}</b-badge
                                                                >
                                                                <small>
                                                                    on
                                                                </small>
                                                                <b-badge
                                                                    class="ml-0 mr-0"
                                                                    variant="secondary"
                                                                    >{{
                                                                        task.agent
                                                                    }}</b-badge
                                                                ><small
                                                                    v-if="
                                                                        task.job_status ===
                                                                            'Scheduled'
                                                                    "
                                                                ></small
                                                                ><small v-else>
                                                                    {{
                                                                        prettify(
                                                                            task.updated
                                                                        )
                                                                    }}</small
                                                                >
                                                            </b-list-group-item>
                                                        </b-list-group></b-col
                                                    ></b-row
                                                ></b-tab
                                            >--></b-tabs
                                        >
                                    </b-col>
                                </b-row>
                            </div>
                        </b-col>
                    </b-row>
                    <br />
                </b-col>
            </b-row>
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
                :title="'Authenticate with ' + this.selectedAgent.name"
                @ok="onStart"
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
                id="disconnect"
                :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
                centered
                close
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-border-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
                :title="`Disconnect ${this.getWorkflow.config.name}?`"
                @ok="disconnectWorkflow"
                ok-variant="danger"
            >
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    You {{ getWorkflow.public ? 'and others' : '' }} will no
                    longer be able to run this workflow. You can always
                    reconnect it later.
                </p>
            </b-modal>
        </b-container>
    </div>
</template>

<script>
import datatree from '@/components/datasets/data-tree';
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '../../router';
import Multiselect from 'vue-multiselect';
import moment from 'moment';
import cronstrue from 'cronstrue';
import VueMarkdown from 'vue-markdown';
import { guid } from '@/utils';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'workflow',
    components: {
        Multiselect,
        VueMarkdown,
        datatree
    },
    props: {
        owner: {
            required: true
        },
        name: {
            required: true
        }
    },
    data: function() {
        return {
            togglingPublic: false,
            selectedDataset: null,
            selectedDatasetLoading: false,
            activeTab: 0,
            submitted: false,
            authenticationUsername: '',
            authenticationPassword: '',
            currentResourceTab: 0,
            showStatusAlert: false,
            statusAlertMessage: '',
            submitType: 'Now',
            crontime: '* */5 * * *',
            delayValue: 10,
            delayUnits: 'Minutes',
            // delayedRuns: [],
            // repeatingRuns: [],
            taskName: '',
            tags: [],
            tagOptions: [],
            params: [],
            input: {
                kind: '',
                from: '',
                filetypes: []
            },
            inputSelectedPatterns: [],
            outputDataset: false,
            outputSync: false,
            outputSpecified: false,
            output: {
                from: '',
                to: '',
                include: {
                    patterns: [],
                    names: []
                },
                exclude: {
                    patterns: [],
                    names: []
                }
            },
            selectedAgent: {
                name: ''
            },
        };
    },
    async mounted() {
        this.populateComponents();
        if ('input' in this.getWorkflow.config)
            await Promise.all([
                this.$store.dispatch('datasets/loadPersonal'),
                this.$store.dispatch('datasets/loadPublic'),
                this.$store.dispatch('datasets/loadShared')
            ]);

        // if (this.workflowKey in this.recentlyRunWorkflows) {
        //     let config = this.recentlyRunWorkflows[this.workflowKey];
        //     if (config.input !== undefined && config.input.from !== undefined)
        //         this.path = config.input.from;
        //     this.presetPath(this.path);
        // }
        // if (this.defaultPath !== undefined && this.defaultPath !== null) {
        //     this.path = this.defaultPath;
        // }
    },
    methods: {
        async togglePublic() {
            if (!this.ownsWorkflow) return;
            this.togglingPublic = true;
            await axios({
                method: 'post',
                url: `/apis/v1/workflows/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/public/`,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await Promise.all([
                            this.$store.dispatch(
                                'workflows/setPersonal',
                                response.data.workflows
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Made ${
                                    this.$router.currentRoute.params.owner
                                }/${this.$router.currentRoute.params.name} ${
                                    response.data.workflows.find(
                                        wf =>
                                            wf.config.name ===
                                            this.getWorkflow.config.name
                                    ).public
                                        ? 'public'
                                        : 'private'
                                }`,
                                guid: guid().toString(),
                                time: moment().format()
                            })
                        ]);
                        this.togglingPublic = false;
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to make ${
                                this.$router.currentRoute.params.owner
                            }/${this.$router.currentRoute.params.name} ${
                                this.getWorkflow.public ? 'private' : 'public'
                            }`,
                            guid: guid().toString(),
                            time: moment().format()
                        });
                        this.togglingPublic = false;
                    }
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to make ${
                            this.$router.currentRoute.params.owner
                        }/${this.$router.currentRoute.params.name} ${
                            this.getWorkflow.public ? 'private' : 'public'
                        }`,
                        guid: guid().toString(),
                        time: moment().format()
                    });
                    this.togglingPublic = false;
                    throw error;
                });
        },
        showDisconnectWorkflowModal() {
            this.$bvModal.show('disconnect');
        },
        async loadSelectedDataset(path) {
            this.selectedDatasetLoading = true;
            return await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        }
                    }
                )
                .then(async response => {
                    this.selectedDataset = response.data;
                    this.selectedDatasetLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.selectedDatasetLoading = false;
                    throw error;
                });
        },
        async refreshWorkflow() {
            await this.$store.dispatch('workflows/refresh', {
                owner: this.$router.currentRoute.params.owner,
                name: this.$router.currentRoute.params.name
            });
        },
        async disconnectWorkflow() {
            await axios({
                method: 'delete',
                url: `/apis/v1/workflows/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/disconnect/`,
                data: this.workflowSearchResult,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    if (response.status === 200) {
                        this.$store.dispatch(
                            'workflows/setPersonal',
                            response.data.workflows
                        );
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Disconnected ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`,
                            guid: guid().toString()
                        });
                        router.push({
                            name: 'workflows'
                        });
                    } else {
                        this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to disconnect ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`,
                            guid: guid().toString()
                        });
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        // async getWorkflowReadme() {
        //     return axios
        //         .get(
        //             `/apis/v1/workflows/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}/readme/`
        //         )
        //         .then(response => {
        //             return response.data.readme;
        //         })
        //         .catch(error => {
        //             Sentry.captureException(error);
        //             throw error;
        //         });
        // },
        parseCronTime(time) {
            let cron = cronstrue.toString(time);
            return cron.charAt(0).toLowerCase() + cron.slice(1);
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        addTag(tag) {
            this.tags.push(tag);
            this.tagOptions.push(tag);
        },
        mapParam(param) {
            if (param.type === 'string')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : ''
                };
            else if (param.type === 'select')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : null,
                    options: param.options
                };
            else if (param.type === 'number')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : 0,
                    min: param.min,
                    max: param.max,
                    step: param.step
                };
            else if (param.type === 'boolean')
                return {
                    name: param.name,
                    type: param.type,
                    value:
                        param.default !== undefined
                            ? param.default.toString().toLowerCase() === 'false'
                            : false
                };
        },
        populateComponents() {
            if (this.getWorkflow !== null) {
                // if a local input path is specified, set it
                if ('input' in this.getWorkflow.config) {
                    this.input.from =
                        this.getWorkflow.config.input.path !== null
                            ? this.getWorkflow.config.input.path
                            : '';
                    this.input.kind = this.getWorkflow.config.input.kind;
                    this.input.filetypes =
                        this.getWorkflow.config.input.filetypes !== undefined &&
                        this.getWorkflow.config.input.filetypes !== null
                            ? this.getWorkflow.config.input.filetypes
                            : [];
                    if (this.input.filetypes.length > 0)
                        this.inputSelectedPatterns = this.input.filetypes;
                }

                // if a local output path is specified, add it to included files
                if (
                    this.getWorkflow.config.output !== undefined &&
                    this.getWorkflow.config.output.path !== undefined
                ) {
                    this.output.from =
                        this.getWorkflow.config.output.path !== null
                            ? this.getWorkflow.config.output.path
                            : '';
                    if (
                        this.getWorkflow.config.output.include !== undefined &&
                        this.getWorkflow.config.output.include.names !==
                            undefined
                    )
                        this.output.include.names = this.getWorkflow.config.output.include.names;
                    if (
                        this.getWorkflow.config.output.include !== undefined &&
                        this.getWorkflow.config.output.include.patterns !==
                            undefined
                    )
                        this.output.include.patterns = this.getWorkflow.config.output.include.patterns;
                    if (
                        this.getWorkflow.config.output.exclude !== undefined &&
                        this.getWorkflow.config.output.exclude.names !==
                            undefined
                    )
                        this.output.exclude.names = this.getWorkflow.config.output.exclude.names;
                    if (
                        this.getWorkflow.config.output.exclude !== undefined &&
                        this.getWorkflow.config.output.exclude.patterns !==
                            undefined
                    )
                        this.output.exclude.patterns = this.getWorkflow.config.output.exclude.patterns;
                }

                // if params are specified, set them
                if ('params' in this.getWorkflow['config'])
                    this.params = this.getWorkflow['config'][
                        'params'
                    ].map(param => this.mapParam(param));
            }

            // if we have pre-configured values for this flow, populate them
            if (
                `${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}` in
                this.recentlyRunWorkflows
            ) {
                let flowConfig = this.recentlyRunWorkflows[
                    `${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`
                ];
                this.params =
                    flowConfig.params !== undefined
                        ? flowConfig.params
                        : this.params;
                this.input = flowConfig.input;
                this.output = flowConfig.output;
                this.selectedAgent = flowConfig.agent;
            }

            if (this.input.from !== null && this.input.from !== '')
                this.loadSelectedDataset(this.input.from);
        },
        inputSelected(node) {
            this.input.from = node.path;
            this.loadSelectedDataset(node.path);
        },
        outputSelected(node) {
            this.output.to = node.path;
        },
        agentSelected(agent) {
            this.selectedAgent = agent;
        },
        agentUnsupported(agent) {
            return (
                (parseInt(agent.max_mem) !== -1 &&
                    parseInt(agent.max_mem) <
                        parseInt(this.getWorkflow.config.resources.mem)) ||
                parseInt(agent.max_cores) <
                    parseInt(this.getWorkflow.config.resources.cores) ||
                parseInt(agent.max_processes) <
                    parseInt(this.getWorkflow.config.resources.processes)
            );
            // TODO walltime
        },
        onTryStart() {
            if (this.mustAuthenticate) this.showAuthenticateModal();
            else this.onStart();
        },
        showAuthenticateModal() {
            this.$bvModal.show('authenticate');
        },
        async onStart() {
            if (
                !this.getWorkflow.config.resources &&
                this.selectedAgent.name !== 'Sandbox'
            ) {
                alert('This workflow can only be submitted to the Sandbox.');
                return;
            }

            // prepare configuration
            this.params['config'] = {};
            this.params['config']['api_url'] = '/apis/v1/tasks/status/';
            let agent = this.selectedAgent;
            if (this.getWorkflow.config.resources)
                agent['resources'] = this.getWorkflow.config.resources;
            let config = {
                name: this.getWorkflow.config.name,
                task_name: this.taskName,
                image: this.getWorkflow.config.image,
                parameters: this.params,
                agent: agent,
                commands: this.getWorkflow.config.commands,
                tags: this.tags
            };
            if ('gpu' in this.getWorkflow.config)
                config['gpu'] = this.getWorkflow.config.gpu;
            if ('branch' in this.getWorkflow.config)
                config['branch'] = this.getWorkflow.config.branch;
            if (this.getWorkflow.config.mount !== null)
                config['mount'] = this.getWorkflow.config.mount;
            if (this.input !== undefined && this.input.from) {
                config.input = this.input;
                config.input.patterns =
                    this.inputSelectedPatterns.length > 0
                        ? this.inputSelectedPatterns
                        : this.input.filetypes;
            }
            if (this.output !== undefined) {
                config.output = this.output;
                // if (!this.outputDataset) delete config.output['to'];
            }

            // save config
            this.$store.dispatch('workflows/setRecentlyRun', {
                name: this.workflowKey,
                config: config
            });

            let data = {
                repo: this.getWorkflow.repo,
                config: config,
                type: this.submitType
            };
            if (this.mustAuthenticate)
                data['auth'] = {
                    username: this.authenticationUsername,
                    password: this.authenticationPassword
                };

            this.submitted = true;
            if (this.submitType === 'Now')
                // submit immediately
                await axios({
                    method: 'post',
                    url: `/apis/v1/tasks/`,
                    data: data,
                    headers: { 'Content-Type': 'application/json' }
                })
                    .then(async response => {
                        await this.$store.dispatch('tasks/setAll', response.data.tasks);
                        router.push({
                            name: 'task',
                            params: {
                                owner: this.profile.djangoProfile.username,
                                name: this.taskName
                            }
                        });
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        throw error;
                    });
            else if (this.submitType === 'After')
                // schedule after delay
                await axios({
                    method: 'post',
                    url: `/apis/v1/tasks/`,
                    data: {
                        repo: this.getWorkflow.repo,
                        config: config,
                        type: this.submitType,
                        delayUnits: this.delayUnits,
                        delayValue: this.delayValue
                    },
                    headers: { 'Content-Type': 'application/json' }
                })
                    .then(response => {
                        this.statusAlertMessage =
                            response.status === 200 && response.data.created
                                ? `Scheduled task ${this.$router.currentRoute.params.name} on ${config.agent.name}`
                                : `Failed to schedule task ${this.$router.currentRoute.params.name} on ${config.agent.name}`;
                        this.showStatusAlert = true;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        this.statusAlertMessage = `Failed to schedule task ${this.createTaskForm.name} on ${this.selectedAgent.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    });
            else if (this.submitType === 'Every')
                // schedule periodically
                await axios({
                    method: 'post',
                    url: `/apis/v1/tasks/`,
                    data: {
                        repo: this.getWorkflow.repo,
                        config: config,
                        type: this.submitType,
                        delayUnits: this.delayUnits,
                        delayValue: this.delayValue
                    },
                    headers: { 'Content-Type': 'application/json' }
                })
                    .then(response => {
                        this.loadRepeatingRuns();
                        this.statusAlertMessage =
                            response.status === 200 && response.data.created
                                ? `Scheduled repeating task ${this.$router.currentRoute.params.name} on ${config.agent.name}`
                                : `Failed to schedule repeating task ${this.$router.currentRoute.params.name} on ${config.agent.name}`;
                        this.showStatusAlert = true;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        this.statusAlertMessage = `Failed to schedule task ${this.createTaskForm.name} on ${this.selectedAgent.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    });
        }
    },
    watch: {
        personalWorkflows: function() {
            // noop
        }
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', [
            'workflow',
            'publicWorkflowsLoading',
            'personalWorkflowsLoading',
            'recentlyRunWorkflows'
        ]),
        ...mapGetters('tasks', [
            'tasks',
            'tasksByOwner',
            'task',
            'tasksLoading'
        ]),
        ...mapGetters('agents', [
            'publicAgentsLoading',
            'publicAgents',
            'personalAgentsLoading',
            'personalAgents'
        ]),
        ...mapGetters('datasets', [
            'personalDatasets',
            'publicDatasets',
            'sharedDatasets',
            'sharingDatasets',
            'personalDatasetsLoading',
            'publicDatasetsLoading',
            'sharedDatasetsLoading',
            'sharingDatasetsLoading'
        ]),
        taskHistory() {
            return this.$store.getters['tasks/tasksByOwner'](
                this.profile.djangoProfile.username
            );
        },
        mustAuthenticate() {
            return !this.selectedAgent.policies.some(
                p =>
                    p.user === this.profile.djangoProfile.username &&
                    (p.role.toLowerCase() === 'guest' ||
                        p.role.toLowerCase() === 'admin')
            );
        },
        getWorkflow() {
            return this.workflow(this.owner, this.name);
        },
        ownsWorkflow() {
            return (
                this.getWorkflow.repo.owner.login ===
                this.profile.githubProfile.login
            );
        },
        workflowLoading() {
            return this.publicWorkflowsLoading || this.personalWorkflowsLoading;
        },
        scheduledTime: function() {
            return `${this.submitType === 'After' ? 'in' : 'every'} ${
                this.delayValue
            } ${this.delayUnits.toLowerCase()}`;
            // else return `${this.parseCronTime(this.crontime)}`;  TODO allow direct cron editing
        },
        workflowKey: function() {
            return `${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`;
        },
        inputFiletypeSelected: function() {
            return this.inputSelectedPatterns.some(pattern => pattern !== '');
        },
        taskNameExists() {
            return this.tasks.some(r => r.name === this.taskName);
        },
        nameValid() {
            return (
                this.taskName !== '' && !this.taskNameExists // && !this.taskNameExists
            );
        },
        paramsValid: function() {
            if (
                this.getWorkflow !== null &&
                this.getWorkflow.config.params !== undefined &&
                this.getWorkflow.config.params.length !== 0
            )
                return this.params.every(
                    param =>
                        param !== undefined &&
                        param.value !== undefined &&
                        param.value !== ''
                );
            else return true;
        },
        inputValid: function() {
            if (
                this.getWorkflow !== null &&
                this.getWorkflow.config.input !== undefined
            )
                return (
                    this.getWorkflow.config.input.path !== undefined &&
                    this.input.from !== '' &&
                    this.input.kind !== '' &&
                    this.inputFiletypeSelected &&
                    this.selectedDataset !== null
                );
            return true;
        },
        outputValid: function() {
            if (
                this.outputDataset &&
                this.getWorkflow &&
                this.getWorkflow.config &&
                this.getWorkflow.config.input !== undefined &&
                this.getWorkflow.config.output.path !== undefined
            )
                return this.output.to !== '';
            return true;
        },
        canSubmit: function() {
            return (
                this.nameValid &&
                this.paramsValid &&
                this.inputValid &&
                this.outputValid &&
                this.selectedAgent.name !== ''
            );
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: white
    padding: 24px

    img
        margin-top: 20px
        max-width: 140px
        max-height: 190px
</style>
