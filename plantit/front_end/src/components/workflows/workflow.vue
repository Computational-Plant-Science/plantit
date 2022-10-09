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
            <b-row v-if="workflowLoading">
                <b-col>
                    <b-spinner
                        small
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading workflow...</span
                    >
                </b-col>
            </b-row>
            <b-row v-else-if="getWorkflow === null"
                ><b-col
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        ><i class="fas fa-exclamation-triangle fa-fw"></i>
                        Workflow not found.</span
                    ></b-col
                ></b-row
            >
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
                                    @click="
                                        openInNewTab(
                                            'https://github.com/' +
                                                this.owner +
                                                '/' +
                                                this.name
                                        )
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
                                        style="
                                            max-width: 7rem;
                                            position: absolute;
                                            right: 20px;
                                            top: 80px;
                                            z-index: 1;
                                        "
                                        right
                                        :src="`https://raw.githubusercontent.com/${getWorkflow.repo.owner.login}/${getWorkflow.repo.name}/master/${getWorkflow.config.logo}`"
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
                                                <h4
                                                    v-if="
                                                        getWorkflow.config
                                                            .name !== undefined
                                                    "
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
                                                </h4>
                                                <h4 v-else class="text-danger">
                                                    <i
                                                        class="fas fa-exclamation-circle text-danger mr-2"
                                                    ></i>
                                                    <small
                                                        >(name not
                                                        provided)</small
                                                    >
                                                </h4></b-col
                                            ><b-col
                                                md="auto"
                                                align-self="center"
                                                class="m-0"
                                            >
                                                <b-badge
                                                    class="mr-1"
                                                    :variant="
                                                        getWorkflow.config
                                                            .public
                                                            ? 'success'
                                                            : 'success'
                                                    "
                                                    ><span
                                                        v-if="
                                                            getWorkflow.config
                                                                .public
                                                        "
                                                        ><i
                                                            class="fas fa-lock-open fa-fw"
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
                                            <!--<b-col v-if="!getWorkflow.example && !getWorkflow.featured">
                                                <b-button
                                                    id="featured-request"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'dark'
                                                            : 'outline-light'
                                                    "
                                                    size="sm"
                                                    @click="
                                                        sendFeaturedRequest
                                                    "
                                                    class="
                                                        justify-self-flex-end
                                                        ml-0
                                                    "
                                                    ><i
                                                        class="
                                                            fas
                                                            fa-certificate fa-fw
                                                        "
                                                    ></i>
                                                    Feature Request
                                                </b-button>
                                                <b-popover
                                                        v-if="profile.hints"
                                                        triggers="hover"
                                                        placement="bottomleft"
                                                        target="featured-request"
                                                        title="Feature Request"
                                                        >Click here to submit a request to make this a featured workflow. An administrator will review the request and contact you shortly.</b-popover
                                                    >
                                            </b-col>-->
                                        </b-row>
                                        <b-row>
                                            <b-col md="auto" class="mr-0 ml-0">
                                                <h5>
                                                    <b-badge
                                                        variant="secondary"
                                                        >{{
                                                            getWorkflow.branch
                                                                .name
                                                        }}</b-badge
                                                    >
                                                </h5>
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
                                        <b-row class="mt-1 mb-1">
                                            <b-col md="auto" class="mr-0 ml-0">
                                                <small>
                                                    <b-link
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-light'
                                                                : 'text-dark'
                                                        "
                                                        @click="
                                                            openInNewTab(
                                                                'https://github.com/' +
                                                                    getWorkflow
                                                                        .repo
                                                                        .owner
                                                                        .login +
                                                                    '/' +
                                                                    getWorkflow
                                                                        .repo
                                                                        .name
                                                            )
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
                                                    ><i
                                                        class="fas fa-star fa-fw"
                                                    ></i>
                                                    {{
                                                        getWorkflow.repo
                                                            .stargazers_count
                                                    }}</small
                                                ></b-col
                                            >
                                            <!--<b-col md="auto" class="mr-0 ml-0"
                                                ><small
                                                    ><i
                                                        class="fas fa-terminal fa-fw"
                                                    ></i
                                                    >{{
                                                        getWorkflow.stats.tasks
                                                    }}</small
                                                ></b-col
                                            >-->
                                        </b-row>
                                        <b-tabs
                                            v-model="activeTab"
                                            nav-class="bg-transparent"
                                            active-nav-item-class="bg-transparent text-dark"
                                            pills
                                            ><b-tab
                                                title="Info"
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
                                                <template #title>
                                                    <b-button
                                                        id="about-workflow"
                                                        :variant="
                                                            activeTab === 0
                                                                ? profile.darkMode
                                                                    ? 'outline-warning'
                                                                    : 'warning'
                                                                : profile.darkMode
                                                                ? 'outline-light'
                                                                : 'white'
                                                        "
                                                        :title="`About ${getWorkflow.config.name}`"
                                                        ><i
                                                            class="fas fa-info fa-fw"
                                                        ></i>
                                                        Info </b-button
                                                    ><b-popover
                                                        v-if="profile.hints"
                                                        triggers="hover"
                                                        placement="bottomleft"
                                                        target="about-workflow"
                                                        title="Workflow Info"
                                                        >Click here to view this
                                                        workflow's metadata and
                                                        description,
                                                        configuration, resource
                                                        requirements, and
                                                        associated
                                                        publications.</b-popover
                                                    ></template
                                                >
                                                <b-row class="mb-3">
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
                                                        {{
                                                            getWorkflow.repo
                                                                .description
                                                        }}
                                                    </b-col>
                                                </b-row>
                                                <b-row
                                                    class="mb-3"
                                                    v-if="
                                                        getWorkflow.config
                                                            .author !==
                                                            undefined &&
                                                        getWorkflow.config
                                                            .author !== null
                                                    "
                                                >
                                                    <b-col>
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
                                                    </b-col>
                                                </b-row>
                                                <b-row
                                                    class="mb-3"
                                                    v-if="
                                                        getWorkflow.config
                                                            .email !==
                                                            undefined &&
                                                        getWorkflow.config
                                                            .email !== null
                                                    "
                                                    ><b-col>
                                                        <h5
                                                            :class="
                                                                profile.darkMode
                                                                    ? 'text-light'
                                                                    : 'text-dark'
                                                            "
                                                        >
                                                            Contact
                                                        </h5>
                                                        <b-row>
                                                            <b-col>
                                                                <b-link
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-light'
                                                                            : 'text-dark'
                                                                    "
                                                                    :href="`mailto:${getWorkflow.config.email}`"
                                                                    ><i
                                                                        class="fas fa-envelope fa-fw"
                                                                    ></i>
                                                                    {{
                                                                        getWorkflow
                                                                            .config
                                                                            .email
                                                                    }}</b-link
                                                                >
                                                            </b-col>
                                                        </b-row>
                                                    </b-col>
                                                </b-row>
                                                <b-row
                                                    class="mb-3"
                                                    v-if="
                                                        getWorkflow.config
                                                            .doi !==
                                                            undefined &&
                                                        getWorkflow.config
                                                            .doi !== null
                                                    "
                                                    ><b-col>
                                                        <h5
                                                            :class="
                                                                profile.darkMode
                                                                    ? 'text-light'
                                                                    : 'text-dark'
                                                            "
                                                        >
                                                            DOI(s)
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
                                                                    <b-col
                                                                        md="auto"
                                                                    >
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
                                                                            :href="`https://doi.org/${getWorkflow.config.doi}`"
                                                                            >{{
                                                                                getWorkflow
                                                                                    .config
                                                                                    .doi
                                                                            }}</b-link
                                                                        >
                                                                        <div
                                                                            v-else
                                                                        >
                                                                            <b-row
                                                                                v-for="doi in getWorkflow
                                                                                    .config
                                                                                    .doi"
                                                                                v-bind:key="
                                                                                    doi
                                                                                "
                                                                                ><b-col
                                                                                    ><b-link
                                                                                        :class="
                                                                                            profile.darkMode
                                                                                                ? 'text-light'
                                                                                                : 'text-dark'
                                                                                        "
                                                                                        :href="`https://doi.org/${doi}`"
                                                                                        >{{
                                                                                            doi
                                                                                        }}</b-link
                                                                                    ></b-col
                                                                                ></b-row
                                                                            >
                                                                        </div>
                                                                    </b-col>
                                                                </b-row>
                                                            </b-col>
                                                        </b-row>
                                                    </b-col>
                                                </b-row>
                                                <b-row class="mb-3">
                                                    <b-col>
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
                                                                        <b>{{
                                                                            getWorkflow
                                                                                .config
                                                                                .image
                                                                        }}</b>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-row>
                                                                    <b-col>
                                                                        <small
                                                                            >Shell</small
                                                                        >
                                                                    </b-col>
                                                                    <b-col
                                                                        cols="10"
                                                                    >
                                                                        <b>{{
                                                                            getWorkflow
                                                                                .config
                                                                                .shell
                                                                                ? getWorkflow
                                                                                      .config
                                                                                      .shell
                                                                                : 'None'
                                                                        }}</b>
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
                                                                            >Environment
                                                                            Variables</small
                                                                        >
                                                                    </b-col>
                                                                    <b-col
                                                                        cols="10"
                                                                    >
                                                                        {{
                                                                            getWorkflow
                                                                                .config
                                                                                .env
                                                                                ? getWorkflow
                                                                                      .config
                                                                                      .env
                                                                                : 'None'
                                                                        }}
                                                                    </b-col>
                                                                </b-row>
                                                                <b-row>
                                                                    <b-col>
                                                                        <small
                                                                            >Bind
                                                                            Mounts</small
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
                                                                        <b>{{
                                                                            getWorkflow
                                                                                .config
                                                                                .params
                                                                                ? getWorkflow
                                                                                      .config
                                                                                      .params
                                                                                      .length
                                                                                : 'None'
                                                                        }}</b>
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
                                                    </b-col>
                                                </b-row>
                                                <b-row class="mb-3">
                                                    <b-col>
                                                        <h5
                                                            :class="
                                                                profile.darkMode
                                                                    ? 'text-light'
                                                                    : 'text-dark'
                                                            "
                                                        >
                                                            Resource Requests
                                                        </h5>
                                                        <b-row>
                                                            <b-col
                                                                align-self="end"
                                                                md="auto"
                                                                class="text-right"
                                                                v-if="
                                                                    getWorkflow
                                                                        .config
                                                                        .jobqueue ===
                                                                    undefined
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
                                                                    requests. If
                                                                    submitted to
                                                                    an agent
                                                                    with a
                                                                    <b
                                                                        >Jobqueue</b
                                                                    >
                                                                    executor,
                                                                    defaults of
                                                                    1 hour, 10
                                                                    GB, 1 core &
                                                                    1 process
                                                                    will be
                                                                    requested.</b-alert
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
                                                                                    walltime
                                                                                }}</code
                                                                            ></b
                                                                        >
                                                                        <small>
                                                                            walltime</small
                                                                        >
                                                                    </b-col>
                                                                </b-row>
                                                                <b-row>
                                                                    <b-col>
                                                                        <b
                                                                            ><code
                                                                                >{{
                                                                                    ' ' +
                                                                                    memory
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
                                                                                        .jobqueue
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
                                                                                        .jobqueue
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
                                                ><template #title>
                                                    <b-button
                                                        id="submit-workflow"
                                                        :disabled="
                                                            workflowLoading
                                                        "
                                                        :variant="
                                                            activeTab === 1
                                                                ? profile.darkMode
                                                                    ? 'outline-warning'
                                                                    : 'warning'
                                                                : profile.darkMode
                                                                ? 'outline-light'
                                                                : 'white'
                                                        "
                                                        :title="`Submit ${getWorkflow.config.name}`"
                                                        ><i
                                                            class="fas fa-terminal fa-fw"
                                                        ></i>
                                                        Submit
                                                    </b-button>
                                                    <b-popover
                                                        v-if="profile.hints"
                                                        triggers="hover"
                                                        placement="bottomleft"
                                                        target="submit-workflow"
                                                        title="Submit Workflow"
                                                        >Click here to configure
                                                        and submit
                                                        {{
                                                            getWorkflow.config
                                                                .name
                                                        }}
                                                        to an agent.</b-popover
                                                    ></template
                                                >
                                                <b-row
                                                    ><b-col>
                                                        <!--<b-row
                                                            ><b-col
                                                                ><h5
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-light'
                                                                            : 'text-dark'
                                                                    "
                                                                >
                                                                    Saved
                                                                    Configurations
                                                                </h5></b-col
                                                            ></b-row
                                                        >-->
                                                        <b-row
                                                            ><b-col
                                                                ><p
                                                                    v-if="
                                                                        getWorkflow.last_config !==
                                                                            undefined &&
                                                                        getWorkflow.last_config !==
                                                                            null
                                                                    "
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-light'
                                                                            : 'text-dark'
                                                                    "
                                                                >
                                                                    Last run
                                                                    {{
                                                                        prettify(
                                                                            getWorkflow
                                                                                .last_config
                                                                                .timestamp
                                                                        )
                                                                    }}
                                                                </p>
                                                                <p
                                                                    :class="
                                                                        profile.darkMode
                                                                            ? 'text-light'
                                                                            : 'text-dark'
                                                                    "
                                                                >
                                                                    Sections
                                                                    marked with
                                                                    <i
                                                                        class="fas fa-exclamation text-danger fa-fw"
                                                                    ></i>
                                                                    are
                                                                    required.
                                                                </p></b-col
                                                            ></b-row
                                                        >
                                                        <b-row>
                                                            <b-col>
                                                                <b-card-group
                                                                    columns
                                                                    deck
                                                                >
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
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
                                                                        :border-variant="
                                                                            submitType ===
                                                                            'Every'
                                                                                ? 'secondary'
                                                                                : timeLimit !==
                                                                                  0
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                        ><b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                                style="
                                                                                    border-right: 2px
                                                                                        lightgray;
                                                                                "
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    class="m-0"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.taskid
                                                                                    ><i
                                                                                        v-if="
                                                                                            idVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row>
                                                                                    <b-col
                                                                                        ><h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-light'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <i
                                                                                                class="fas fa-hashtag fa-fw"
                                                                                            ></i>
                                                                                            ID
                                                                                        </h5>
                                                                                    </b-col>
                                                                                    <b-col
                                                                                        md="auto"
                                                                                        ><h5
                                                                                            :class="
                                                                                                submitType ===
                                                                                                'Every'
                                                                                                    ? 'text-secondary'
                                                                                                    : profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            {{
                                                                                                submitType !==
                                                                                                'Now'
                                                                                                    ? '(auto-generated)'
                                                                                                    : taskName !==
                                                                                                      ''
                                                                                                    ? taskName
                                                                                                    : taskGuid
                                                                                            }}
                                                                                            <i
                                                                                                v-if="
                                                                                                    submitType ===
                                                                                                    'Every'
                                                                                                "
                                                                                                class="far fa-circle text-secondary fa-fw"
                                                                                            ></i>
                                                                                            <i
                                                                                                v-else-if="
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
                                                                                <b-collapse
                                                                                    id="taskid"
                                                                                    v-model="
                                                                                        idVisible
                                                                                    "
                                                                                >
                                                                                    <b-row
                                                                                        ><b-col
                                                                                            ><b
                                                                                                :class="
                                                                                                    profile.darkMode
                                                                                                        ? 'text-white'
                                                                                                        : 'text-dark'
                                                                                                "
                                                                                            >
                                                                                                Enter
                                                                                                a
                                                                                                task
                                                                                                name
                                                                                                to
                                                                                                replace
                                                                                                the
                                                                                                auto-generated
                                                                                                GUID.
                                                                                                (This
                                                                                                value
                                                                                                must
                                                                                                be
                                                                                                unique.)
                                                                                            </b>
                                                                                        </b-col>
                                                                                    </b-row>
                                                                                    <b-row
                                                                                        class="mt-1"
                                                                                    >
                                                                                        <b-col>
                                                                                            <b-form-input
                                                                                                :disabled="
                                                                                                    submitType ===
                                                                                                    'Every'
                                                                                                "
                                                                                                :class="
                                                                                                    profile.darkMode
                                                                                                        ? 'input-dark'
                                                                                                        : 'input-light'
                                                                                                "
                                                                                                v-model="
                                                                                                    taskName
                                                                                                "
                                                                                                :placeholder="
                                                                                                    taskGuid
                                                                                                "
                                                                                            ></b-form-input>
                                                                                        </b-col>
                                                                                    </b-row>
                                                                                </b-collapse>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
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
                                                                        :border-variant="
                                                                            timeLimit !==
                                                                            0
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                    >
                                                                        <b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    class="m-0"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.time-limit
                                                                                    ><i
                                                                                        v-if="
                                                                                            timeLimitVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row>
                                                                                    <b-col>
                                                                                        <h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <i
                                                                                                class="fas fa-stopwatch fa-fw"
                                                                                            ></i>
                                                                                            Time
                                                                                        </h5>
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
                                                                                                    timeLimit !==
                                                                                                    0
                                                                                                "
                                                                                                >{{
                                                                                                    timeLimit
                                                                                                }}
                                                                                                {{
                                                                                                    timeLimitUnits
                                                                                                }}</span
                                                                                            >
                                                                                            <span
                                                                                                v-if="
                                                                                                    timeLimit ===
                                                                                                    0
                                                                                                "
                                                                                                >None</span
                                                                                            ><span
                                                                                                v-else
                                                                                                ><i
                                                                                                    class="fas fa-check fa-fw ml-1 text-success"
                                                                                                ></i
                                                                                            ></span></h5
                                                                                    ></b-col>
                                                                                </b-row>

                                                                                <b-collapse
                                                                                    id="time-limit"
                                                                                    v-model="
                                                                                        timeLimitVisible
                                                                                    "
                                                                                >
                                                                                    <b-row
                                                                                        ><b-col
                                                                                            ><b
                                                                                                :class="
                                                                                                    profile.darkMode
                                                                                                        ? 'text-white'
                                                                                                        : 'text-dark'
                                                                                                "
                                                                                            >
                                                                                                Set
                                                                                                a
                                                                                                time
                                                                                                limit
                                                                                                for
                                                                                                this
                                                                                                task.
                                                                                            </b>
                                                                                        </b-col>
                                                                                    </b-row>
                                                                                    <b-row
                                                                                        class="mt-2"
                                                                                        ><b-col
                                                                                            md="auto"
                                                                                            ><b-form-spinbutton
                                                                                                v-model="
                                                                                                    timeLimit
                                                                                                "
                                                                                                min="1"
                                                                                                :max="
                                                                                                    timeLimitUnits ===
                                                                                                    'Minutes'
                                                                                                        ? 60
                                                                                                        : timeLimitUnits ===
                                                                                                          'Hours'
                                                                                                        ? 48
                                                                                                        : 10
                                                                                                "
                                                                                            ></b-form-spinbutton></b-col
                                                                                        ><b-col
                                                                                            md="auto"
                                                                                            ><b-dropdown
                                                                                                dropright
                                                                                                ><template
                                                                                                    #button-content
                                                                                                    >{{
                                                                                                        timeLimitUnits
                                                                                                    }}</template
                                                                                                ><b-dropdown-item
                                                                                                    class="darklinks"
                                                                                                    @click="
                                                                                                        setTimeLimitUnits(
                                                                                                            'Minutes'
                                                                                                        )
                                                                                                    "
                                                                                                    >Minutes</b-dropdown-item
                                                                                                ><b-dropdown-item
                                                                                                    class="darklinks"
                                                                                                    @click="
                                                                                                        setTimeLimitUnits(
                                                                                                            'Hours'
                                                                                                        )
                                                                                                    "
                                                                                                    >Hours</b-dropdown-item
                                                                                                ><b-dropdown-item
                                                                                                    class="darklinks"
                                                                                                    @click="
                                                                                                        setTimeLimitUnits(
                                                                                                            'Days'
                                                                                                        )
                                                                                                    "
                                                                                                    >Days</b-dropdown-item
                                                                                                ></b-dropdown
                                                                                            ></b-col
                                                                                        ></b-row
                                                                                    >
                                                                                </b-collapse>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
                                                                        "
                                                                        v-if="
                                                                            getWorkflow !==
                                                                                null &&
                                                                            getWorkflow
                                                                                .config
                                                                                .input !==
                                                                                undefined &&
                                                                            getWorkflow
                                                                                .config
                                                                                .input
                                                                                .kind !==
                                                                                undefined &&
                                                                            getWorkflow
                                                                                .config
                                                                                .input
                                                                                .kind !==
                                                                                null
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
                                                                        :border-variant="
                                                                            inputValid
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                    >
                                                                        <b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.input
                                                                                    ><i
                                                                                        v-if="
                                                                                            inputVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row>
                                                                                    <b-col>
                                                                                        <h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <i
                                                                                                class="fas fa-download fa-fw"
                                                                                            ></i>
                                                                                            Input
                                                                                            <!--{{
                                                                                this.input.kind[0].toUpperCase() +
                                                                                    this.input.kind.substr(
                                                                                        1
                                                                                    )
                                                                            }}-->
                                                                                        </h5>
                                                                                    </b-col>
                                                                                    <b-col
                                                                                        md="auto"
                                                                                    >
                                                                                        <b-row
                                                                                            align-v="center"
                                                                                            ><b-col>
                                                                                                <h5
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
                                                                                                        ><i
                                                                                                            v-if="
                                                                                                                selectedInput.type ===
                                                                                                                'file'
                                                                                                            "
                                                                                                            class="fas fa-file fa-fw mr-1"
                                                                                                        ></i>
                                                                                                        <i
                                                                                                            v-else
                                                                                                            class="fas fa-folder fa-fw mr-1"
                                                                                                        ></i
                                                                                                        >{{
                                                                                                            selectedInput.path
                                                                                                        }}
                                                                                                        <i
                                                                                                            class="fas fa-check text-success fa-fw"
                                                                                                        ></i>
                                                                                                    </span>
                                                                                                    <i
                                                                                                        v-else
                                                                                                        class="fas fa-exclamation text-danger fa-fw"
                                                                                                    ></i></h5
                                                                                            ></b-col>
                                                                                        </b-row>
                                                                                    </b-col>
                                                                                </b-row>
                                                                                <b-row>
                                                                                    <b-col>
                                                                                        <b-collapse
                                                                                            id="input"
                                                                                            v-model="
                                                                                                inputVisible
                                                                                            "
                                                                                        >
                                                                                            <div>
                                                                                                <b
                                                                                                    :class="
                                                                                                        profile.darkMode
                                                                                                            ? 'text-white'
                                                                                                            : 'text-dark'
                                                                                                    "
                                                                                                >
                                                                                                    Select
                                                                                                    a
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
                                                                                                    from
                                                                                                    the
                                                                                                    Data
                                                                                                    Commons
                                                                                                    or
                                                                                                    your
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
                                                                                                    from
                                                                                                    the
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
                                                                                                                userDatasetsLoading
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
                                                                                                                        userDatasets
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
                                                                                                                ></datatree> </b-col></b-row
                                                                                                    ></b-tab>
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
                                                                                                        :class="
                                                                                                            profile.darkMode
                                                                                                                ? 'input-dark'
                                                                                                                : 'input-light'
                                                                                                        "
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
                                                                                                v-if="
                                                                                                    input.kind !==
                                                                                                    'directory'
                                                                                                "
                                                                                                class="mt-1"
                                                                                                :variant="
                                                                                                    inputFiletypeSelected
                                                                                                        ? 'success'
                                                                                                        : 'danger'
                                                                                                "
                                                                                                :show="
                                                                                                    true
                                                                                                "
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
                                                                                            <b-alert
                                                                                                v-else-if="
                                                                                                    input.path !==
                                                                                                        undefined &&
                                                                                                    input.path !==
                                                                                                        null &&
                                                                                                    input.path.includes(
                                                                                                        ' '
                                                                                                    )
                                                                                                "
                                                                                                class="mt-1"
                                                                                                variant="danger"
                                                                                                :show="
                                                                                                    true
                                                                                                "
                                                                                            >
                                                                                                <i
                                                                                                    class="fas fa-exclamation text-danger"
                                                                                                ></i>
                                                                                                Input
                                                                                                path
                                                                                                may
                                                                                                not
                                                                                                contain
                                                                                                spaces
                                                                                            </b-alert>
                                                                                            <b-alert
                                                                                                v-else
                                                                                                class="mt-1"
                                                                                                :variant="
                                                                                                    inputValid
                                                                                                        ? 'success'
                                                                                                        : 'danger'
                                                                                                "
                                                                                                :show="
                                                                                                    true
                                                                                                "
                                                                                                >Selected:
                                                                                                {{
                                                                                                    inputValid
                                                                                                        ? selectedInput.path
                                                                                                        : 'None'
                                                                                                }}
                                                                                                <i
                                                                                                    v-if="
                                                                                                        inputValid
                                                                                                    "
                                                                                                    class="fas fa-check text-success"
                                                                                                ></i>
                                                                                                <i
                                                                                                    v-else
                                                                                                    class="fas fa-exclamation text-danger"
                                                                                                ></i>
                                                                                            </b-alert>
                                                                                        </b-collapse>
                                                                                    </b-col>
                                                                                </b-row>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
                                                                        "
                                                                        v-if="
                                                                            getWorkflow !==
                                                                                null &&
                                                                            getWorkflow.config !==
                                                                                undefined
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
                                                                        :border-variant="
                                                                            outputValid
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                    >
                                                                        <b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.output
                                                                                    ><i
                                                                                        v-if="
                                                                                            outputVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row
                                                                                    ><b-col>
                                                                                        <h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <i
                                                                                                v-if="
                                                                                                    profile.darkMode
                                                                                                "
                                                                                                class="fas fa-upload fa-fw text-white"
                                                                                            ></i>
                                                                                            <i
                                                                                                v-else
                                                                                                class="fas fa-upload fa-fw text-dark"
                                                                                            ></i>
                                                                                            Output
                                                                                        </h5>
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
                                                                                                    selectedOutput !==
                                                                                                        null &&
                                                                                                    outputValid
                                                                                                "
                                                                                            >
                                                                                                <i
                                                                                                    class="fas fa-folder fa-fw mr-1"
                                                                                                ></i
                                                                                                >{{
                                                                                                    selectedOutput.path
                                                                                                }}
                                                                                                <i
                                                                                                    class="fas fa-check text-success fa-fw"
                                                                                                ></i>
                                                                                            </span>
                                                                                            <span
                                                                                                v-else
                                                                                            >
                                                                                                <i
                                                                                                    class="fas fa-exclamation text-danger fa-fw ml-1"
                                                                                                ></i
                                                                                            ></span></h5
                                                                                    ></b-col>
                                                                                </b-row>
                                                                                <b-collapse
                                                                                    id="output"
                                                                                    v-model="
                                                                                        outputVisible
                                                                                    "
                                                                                >
                                                                                    <b-row
                                                                                        ><b-col
                                                                                            ><b>
                                                                                                Select
                                                                                                a
                                                                                                directory
                                                                                                in
                                                                                                the
                                                                                                CyVerse
                                                                                                Data
                                                                                                Store
                                                                                                to
                                                                                                transfer
                                                                                                results
                                                                                                to.
                                                                                            </b>
                                                                                            <datatree
                                                                                                select="directory"
                                                                                                :create="
                                                                                                    true
                                                                                                "
                                                                                                :upload="
                                                                                                    false
                                                                                                "
                                                                                                :download="
                                                                                                    false
                                                                                                "
                                                                                                @selectNode="
                                                                                                    outputSelected
                                                                                                "
                                                                                                :node="
                                                                                                    userDatasets
                                                                                                "
                                                                                            ></datatree></b-col
                                                                                    ></b-row>
                                                                                    <b-row
                                                                                        v-if="
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output !==
                                                                                                undefined &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output !==
                                                                                                null &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output
                                                                                                .include !==
                                                                                                undefined &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output
                                                                                                .include
                                                                                                .patterns !==
                                                                                                undefined &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output
                                                                                                .include
                                                                                                .patterns
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
                                                                                                output
                                                                                                patterns.
                                                                                            </b>
                                                                                            <multiselect
                                                                                                :class="
                                                                                                    profile.darkMode
                                                                                                        ? 'input-dark'
                                                                                                        : 'input-light'
                                                                                                "
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
                                                                                                    outputSelectedPatterns
                                                                                                "
                                                                                                :options="
                                                                                                    getWorkflow
                                                                                                        .config
                                                                                                        .output
                                                                                                        .include
                                                                                                        .patterns
                                                                                                "
                                                                                            ></multiselect>
                                                                                        </b-col>
                                                                                    </b-row>
                                                                                    <b-row
                                                                                        v-if="
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output !==
                                                                                                undefined &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output !==
                                                                                                null &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output
                                                                                                .include !==
                                                                                                undefined &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output
                                                                                                .include
                                                                                                .names !==
                                                                                                undefined &&
                                                                                            getWorkflow
                                                                                                .config
                                                                                                .output
                                                                                                .include
                                                                                                .names
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
                                                                                                output
                                                                                                files
                                                                                                by
                                                                                                name.
                                                                                            </b>
                                                                                            <multiselect
                                                                                                :class="
                                                                                                    profile.darkMode
                                                                                                        ? 'input-dark'
                                                                                                        : 'input-light'
                                                                                                "
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
                                                                                                    outputSelectedNames
                                                                                                "
                                                                                                :options="
                                                                                                    getWorkflow
                                                                                                        .config
                                                                                                        .output
                                                                                                        .include
                                                                                                        .names
                                                                                                "
                                                                                            ></multiselect>
                                                                                        </b-col>
                                                                                    </b-row>
                                                                                    <b-alert
                                                                                        v-if="
                                                                                            output.to !==
                                                                                                undefined &&
                                                                                            output.to !==
                                                                                                null &&
                                                                                            output.to.includes(
                                                                                                ' '
                                                                                            )
                                                                                        "
                                                                                        class="mt-1"
                                                                                        variant="danger"
                                                                                        :show="
                                                                                            true
                                                                                        "
                                                                                    >
                                                                                        <i
                                                                                            class="fas fa-exclamation text-danger"
                                                                                        ></i>
                                                                                        Output
                                                                                        path
                                                                                        may
                                                                                        not
                                                                                        contain
                                                                                        spaces
                                                                                    </b-alert>
                                                                                </b-collapse>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
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
                                                                        :border-variant="
                                                                            agentValid
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                    >
                                                                        <b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.agent
                                                                                    ><i
                                                                                        v-if="
                                                                                            agentVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row
                                                                                    ><b-col>
                                                                                        <h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <i
                                                                                                class="fas fa-server fa-fw"
                                                                                            ></i>
                                                                                            Agent
                                                                                        </h5>
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
                                                                                                agentValid
                                                                                                    ? selectedAgent
                                                                                                    : ''
                                                                                            }}<i
                                                                                                v-if="
                                                                                                    agentValid
                                                                                                "
                                                                                                class="fas fa-check text-success fa-fw ml-1"
                                                                                            ></i>
                                                                                            <span
                                                                                                v-else
                                                                                                ><i
                                                                                                    class="fas fa-exclamation text-danger fa-fw ml-1"
                                                                                                ></i>
                                                                                            </span></h5
                                                                                    ></b-col>
                                                                                </b-row>
                                                                                <b-collapse
                                                                                    id="agent"
                                                                                    v-model="
                                                                                        agentVisible
                                                                                    "
                                                                                >
                                                                                    <div>
                                                                                        <b
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            Select
                                                                                            an
                                                                                            agent
                                                                                            to
                                                                                            submit
                                                                                            this
                                                                                            task
                                                                                            to.
                                                                                        </b>
                                                                                        <b-row
                                                                                            align-h="center"
                                                                                            v-if="
                                                                                                agentsLoading
                                                                                            "
                                                                                        >
                                                                                            <b-spinner
                                                                                                type="grow"
                                                                                                label="Loading..."
                                                                                                variant="secondary"
                                                                                            ></b-spinner>
                                                                                        </b-row>
                                                                                        <b-row
                                                                                            v-else-if="
                                                                                                getAgents.length ===
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
                                                                                                v-for="agent in getAgents"
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
                                                                                                            getWorkflow
                                                                                                                .config
                                                                                                                .jobqueue !==
                                                                                                                undefined &&
                                                                                                            parseInt(
                                                                                                                agent.max_mem
                                                                                                            ) >=
                                                                                                                parseInt(
                                                                                                                    memory
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
                                                                                                            agent.gpus
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
                                                                                    </div>
                                                                                </b-collapse>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
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
                                                                        :border-variant="
                                                                            tags.length >
                                                                            0
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                    >
                                                                        <b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.tags
                                                                                    ><i
                                                                                        v-if="
                                                                                            tagsVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row>
                                                                                    <b-col>
                                                                                        <h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <i
                                                                                                class="fas fa-tags fa-fw"
                                                                                            ></i>
                                                                                            Tags
                                                                                        </h5>
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
                                                                                <b-collapse
                                                                                    id="tags"
                                                                                    v-model="
                                                                                        tagsVisible
                                                                                    "
                                                                                >
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
                                                                                        class="mt-2"
                                                                                    >
                                                                                        <b-col>
                                                                                            <multiselect
                                                                                                :class="
                                                                                                    profile.darkMode
                                                                                                        ? 'input-dark'
                                                                                                        : 'input-light'
                                                                                                "
                                                                                                style="
                                                                                                    z-index: 100;
                                                                                                "
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
                                                                                </b-collapse>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
                                                                        "
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
                                                                        :border-variant="
                                                                            paramsValid
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                    >
                                                                        <b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.parameters
                                                                                    ><i
                                                                                        v-if="
                                                                                            parametersVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row
                                                                                    ><b-col>
                                                                                        <h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <i
                                                                                                class="fas fa-keyboard fa-fw"
                                                                                            ></i>
                                                                                            Parameters
                                                                                        </h5> </b-col
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
                                                                                                class="fas fa-check text-success fa-fw ml-1"
                                                                                            ></i>
                                                                                            <i
                                                                                                v-else
                                                                                                class="fas fa-exclamation text-danger fa-fw ml-1"
                                                                                            ></i></h5
                                                                                    ></b-col>
                                                                                </b-row>
                                                                                <b-collapse
                                                                                    id="parameters"
                                                                                    v-model="
                                                                                        parametersVisible
                                                                                    "
                                                                                >
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
                                                                                        class="mt-2"
                                                                                        ><b-col>
                                                                                            <b-row
                                                                                                class="mt-1"
                                                                                                v-for="param in params"
                                                                                                v-bind:key="
                                                                                                    param.name
                                                                                                "
                                                                                            >
                                                                                                <b-col>
                                                                                                    <i
                                                                                                        v-if="
                                                                                                            param.type ===
                                                                                                            'number'
                                                                                                        "
                                                                                                        class="fas fa-calculator fa-fw mr-1"
                                                                                                    ></i>
                                                                                                    <i
                                                                                                        v-else-if="
                                                                                                            param.type ===
                                                                                                            'boolean'
                                                                                                        "
                                                                                                        class="far fa-flag fa-fw mr-1"
                                                                                                    ></i>
                                                                                                    <i
                                                                                                        v-else-if="
                                                                                                            param.type ===
                                                                                                            'string'
                                                                                                        "
                                                                                                        class="fas fa-edit fa-fw mr-1"
                                                                                                    ></i>
                                                                                                    <i
                                                                                                        v-else-if="
                                                                                                            param.type ===
                                                                                                            'select'
                                                                                                        "
                                                                                                        class="fas fa-list fa-fw mr-1"
                                                                                                    ></i>
                                                                                                    <i
                                                                                                        v-else-if="
                                                                                                            param.type ===
                                                                                                            'multiselect'
                                                                                                        "
                                                                                                        class="fas fa-th-list fa-fw mr-1"
                                                                                                    ></i>
                                                                                                    {{
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
                                                                                </b-collapse>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                    <b-card
                                                                        style="
                                                                            min-width: 60rem;
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
                                                                        :border-variant="
                                                                            selectedProject !==
                                                                            null
                                                                                ? 'success'
                                                                                : 'secondary'
                                                                        "
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
                                                                        class="mb-4"
                                                                        ><b-row>
                                                                            <b-col
                                                                                md="auto"
                                                                            >
                                                                                <b-button
                                                                                    size="sm"
                                                                                    :variant="
                                                                                        profile.darkMode
                                                                                            ? 'dark'
                                                                                            : 'outline-dark'
                                                                                    "
                                                                                    v-b-toggle.project
                                                                                    ><i
                                                                                        v-if="
                                                                                            projectVisible
                                                                                        "
                                                                                        class="fas fa-minus"
                                                                                    ></i
                                                                                    ><i
                                                                                        v-else
                                                                                        class="fas fa-plus"
                                                                                    ></i
                                                                                ></b-button>
                                                                            </b-col>
                                                                            <b-col>
                                                                                <b-row
                                                                                    ><b-col>
                                                                                        <h5
                                                                                            :class="
                                                                                                profile.darkMode
                                                                                                    ? 'text-white'
                                                                                                    : 'text-dark'
                                                                                            "
                                                                                        >
                                                                                            <b-img
                                                                                                class="mb-1"
                                                                                                style="
                                                                                                    max-width: 25px;
                                                                                                "
                                                                                                :src="
                                                                                                    profile.darkMode
                                                                                                        ? require('../../assets/miappe_icon.png')
                                                                                                        : require('../../assets/miappe_icon_black.png')
                                                                                                "
                                                                                            ></b-img>
                                                                                            Project
                                                                                        </h5> </b-col
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
                                                                                                    selectedProject !==
                                                                                                    null
                                                                                                "
                                                                                                ><small
                                                                                                    >Project</small
                                                                                                >
                                                                                                {{
                                                                                                    selectedProject.title
                                                                                                }}</span
                                                                                            >
                                                                                            <span
                                                                                                v-if="
                                                                                                    selectedStudy !==
                                                                                                    null
                                                                                                "
                                                                                                >,
                                                                                                <small
                                                                                                    >Study</small
                                                                                                >
                                                                                                {{
                                                                                                    selectedStudy.title
                                                                                                }}</span
                                                                                            >
                                                                                            <span
                                                                                                v-if="
                                                                                                    selectedProject ===
                                                                                                    null
                                                                                                "
                                                                                            ></span
                                                                                            ><span
                                                                                                v-else
                                                                                                ><i
                                                                                                    class="fas fa-check fa-fw ml-1 text-success"
                                                                                                ></i
                                                                                            ></span></h5
                                                                                    ></b-col>
                                                                                </b-row>
                                                                                <b-collapse
                                                                                    id="project"
                                                                                    v-model="
                                                                                        projectVisible
                                                                                    "
                                                                                >
                                                                                    <b-row
                                                                                        ><b-col
                                                                                            ><b
                                                                                                :class="
                                                                                                    profile.darkMode
                                                                                                        ? 'text-white'
                                                                                                        : 'text-dark'
                                                                                                "
                                                                                            >
                                                                                                Associate
                                                                                                this
                                                                                                task
                                                                                                with
                                                                                                a
                                                                                                MIAPPE
                                                                                                project
                                                                                                or
                                                                                                study.
                                                                                            </b>
                                                                                        </b-col>
                                                                                    </b-row>
                                                                                    <b-row
                                                                                        v-if="
                                                                                            userProjects.length >
                                                                                            0
                                                                                        "
                                                                                        class="mt-2"
                                                                                        ><b-col
                                                                                            cols="3"
                                                                                            ><i
                                                                                                >Project</i
                                                                                            ></b-col
                                                                                        ><b-col
                                                                                            cols="9"
                                                                                            v-if="
                                                                                                selectedProject !==
                                                                                                null
                                                                                            "
                                                                                            ><i
                                                                                                >Study</i
                                                                                            ></b-col
                                                                                        ></b-row
                                                                                    >
                                                                                    <b-row
                                                                                        v-else
                                                                                        class="mt-2"
                                                                                        ><b-col
                                                                                            cols="3"
                                                                                            ><i
                                                                                                >You
                                                                                                haven't
                                                                                                started
                                                                                                any
                                                                                                projects.</i
                                                                                            ></b-col
                                                                                        ></b-row
                                                                                    >
                                                                                    <b-row
                                                                                        class="mt-1"
                                                                                        v-for="project in userProjects"
                                                                                        v-bind:key="
                                                                                            project.title
                                                                                        "
                                                                                        ><b-col
                                                                                            style="
                                                                                                border-top: 2px
                                                                                                    solid
                                                                                                    lightgray;
                                                                                                left: -5px;
                                                                                            "
                                                                                            cols="3"
                                                                                        >
                                                                                            <b-button
                                                                                                :variant="
                                                                                                    profile.darkMode
                                                                                                        ? 'outline-light'
                                                                                                        : 'white'
                                                                                                "
                                                                                                @click="
                                                                                                    selectedProject =
                                                                                                        project
                                                                                                "
                                                                                                >{{
                                                                                                    project.title
                                                                                                }}<i
                                                                                                    v-if="
                                                                                                        selectedProject !==
                                                                                                            null &&
                                                                                                        selectedProject.title ===
                                                                                                            project.title
                                                                                                    "
                                                                                                    class="fas fa-check fa-fw text-success ml-1"
                                                                                                ></i
                                                                                            ></b-button> </b-col
                                                                                        ><b-col
                                                                                            style="
                                                                                                border-top: 2px
                                                                                                    solid
                                                                                                    lightgray;
                                                                                                left: -5px;
                                                                                            "
                                                                                            cols="9"
                                                                                            v-if="
                                                                                                selectedProject !==
                                                                                                null
                                                                                            "
                                                                                            ><b-row
                                                                                                v-for="study in project.studies"
                                                                                                v-bind:key="
                                                                                                    study.title
                                                                                                "
                                                                                                ><b-col
                                                                                                    ><b-button
                                                                                                        :disabled="
                                                                                                            project.title !==
                                                                                                            selectedProject.title
                                                                                                        "
                                                                                                        :variant="
                                                                                                            profile.darkMode
                                                                                                                ? 'outline-light'
                                                                                                                : 'white'
                                                                                                        "
                                                                                                        @click="
                                                                                                            selectedStudy =
                                                                                                                study
                                                                                                        "
                                                                                                        >{{
                                                                                                            study.title
                                                                                                        }}<i
                                                                                                            v-if="
                                                                                                                selectedStudy !==
                                                                                                                    null &&
                                                                                                                selectedStudy.title ===
                                                                                                                    study.title &&
                                                                                                                selectedProject ===
                                                                                                                    project
                                                                                                            "
                                                                                                            class="fas fa-check fa-fw ml-1 text-success"
                                                                                                        ></i></b-button></b-col></b-row></b-col
                                                                                    ></b-row>
                                                                                </b-collapse>
                                                                            </b-col>
                                                                        </b-row>
                                                                    </b-card>
                                                                </b-card-group>
                                                            </b-col>
                                                        </b-row>
                                                        <b-row>
                                                            <b-col
                                                                ><b-button
                                                                    :disabled="
                                                                        !canSubmit ||
                                                                        submitting
                                                                    "
                                                                    @click="
                                                                        onStart
                                                                    "
                                                                    :variant="
                                                                        profile.darkMode
                                                                            ? 'outline-success'
                                                                            : 'success'
                                                                    "
                                                                    block
                                                                >
                                                                    <b-spinner
                                                                        small
                                                                        v-if="
                                                                            submitting
                                                                        "
                                                                        label="Loading..."
                                                                        variant="dark"
                                                                        class="mr-2"
                                                                    ></b-spinner
                                                                    ><i
                                                                        v-else
                                                                        class="fas fa-chevron-right fa-fw mr-1"
                                                                    ></i>
                                                                    Start</b-button
                                                                ></b-col
                                                            >
                                                            <b-col
                                                                md="auto"
                                                                class="mr-0"
                                                                align-self="end"
                                                            >
                                                                <b-input-group>
                                                                    <b-form-input
                                                                        v-if="
                                                                            submitType ===
                                                                            'Now'
                                                                        "
                                                                        v-show="
                                                                            submitType ===
                                                                                'Now' &&
                                                                            getWorkflow
                                                                                .config
                                                                                .input ===
                                                                                undefined
                                                                        "
                                                                        min="1"
                                                                        max="10"
                                                                        v-model="
                                                                            iterations
                                                                        "
                                                                        type="number"
                                                                    ></b-form-input>
                                                                    <!--<b-input-group-append is-text>{{ iterations }} Run{{ iterations === 1 ? '' : 's' }}</b-input-group-append>-->
                                                                    <template
                                                                        #append
                                                                    >
                                                                        <b-dropdown
                                                                            :variant="
                                                                                profile.darkMode
                                                                                    ? 'outline-secondary'
                                                                                    : 'secondary'
                                                                            "
                                                                            :text="
                                                                                submitType
                                                                            "
                                                                            v-model="
                                                                                submitType
                                                                            "
                                                                            block
                                                                            dropup
                                                                        >
                                                                            <template
                                                                                #button-content
                                                                            >
                                                                                {{
                                                                                    submitType
                                                                                }}
                                                                            </template>
                                                                            <b-dropdown-item
                                                                                class="darklinks"
                                                                                @click="
                                                                                    submitType =
                                                                                        'Now'
                                                                                "
                                                                                >Now</b-dropdown-item
                                                                            >
                                                                            <b-dropdown-item
                                                                                class="darklinks"
                                                                                @click="
                                                                                    submitType =
                                                                                        'After'
                                                                                "
                                                                                >After</b-dropdown-item
                                                                            >
                                                                            <b-dropdown-item
                                                                                class="darklinks"
                                                                                @click="
                                                                                    submitType =
                                                                                        'Every'
                                                                                "
                                                                                >Every</b-dropdown-item
                                                                            >
                                                                            <b-dropdown-item
                                                                                v-if="
                                                                                    getWorkflow
                                                                                        .config
                                                                                        .input !==
                                                                                    undefined
                                                                                "
                                                                                class="darklinks"
                                                                                @click="
                                                                                    submitType =
                                                                                        'Watch'
                                                                                "
                                                                                >Watch</b-dropdown-item
                                                                            >
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
                                                                    ><template
                                                                        #append
                                                                    >
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
                                                        </b-row>
                                                        <!--<b-row class="mt-4" v-if="submitType === 'Watch'">
                                                    <b-col>
                                                      Watching {{ input.path }}
                                                    </b-col>
                                                  </b-row>-->
                                                        <b-row class="mt-4">
                                                            <b-col
                                                                ><b-row
                                                                    ><b-col
                                                                        ><h5
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-white'
                                                                                    : 'text-dark'
                                                                            "
                                                                        >
                                                                            Scheduled
                                                                            Tasks
                                                                        </h5></b-col
                                                                    ></b-row
                                                                >
                                                                <hr
                                                                    style="
                                                                        border-top: 1px
                                                                            solid
                                                                            darkgray;
                                                                    "
                                                                />
                                                                <b-row>
                                                                    <b-col
                                                                        ><b
                                                                            >Delayed</b
                                                                        ></b-col
                                                                    >
                                                                </b-row>
                                                                <b-row
                                                                    v-if="
                                                                        tasksLoading
                                                                    "
                                                                    ><b-col
                                                                        ><b-spinner
                                                                            small
                                                                            label="Loading..."
                                                                            :variant="
                                                                                profile.darkMode
                                                                                    ? 'light'
                                                                                    : 'dark'
                                                                            "
                                                                            class="mr-1"
                                                                        ></b-spinner></b-col
                                                                ></b-row>
                                                                <b-row
                                                                    v-else-if="
                                                                        !tasksLoading &&
                                                                        delayedTasks.length ===
                                                                            0
                                                                    "
                                                                >
                                                                    <b-col>
                                                                        <p
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-light pl-3 pr-3'
                                                                                    : 'text-dark pl-3 pr-3'
                                                                            "
                                                                        >
                                                                            No
                                                                            delayed
                                                                            tasks
                                                                            are
                                                                            scheduled.
                                                                        </p>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-list-group
                                                                    v-else
                                                                    class="text-left m-0 p-0 mt-2 mb-2"
                                                                >
                                                                    <delayedtaskblurb
                                                                        v-for="task in delayedTasks"
                                                                        v-bind:key="
                                                                            task.name
                                                                        "
                                                                        :task="
                                                                            task
                                                                        "
                                                                    ></delayedtaskblurb>
                                                                </b-list-group>
                                                                <b-row
                                                                    class="mt-3"
                                                                >
                                                                    <b-col
                                                                        ><b
                                                                            >Repeating</b
                                                                        ></b-col
                                                                    >
                                                                </b-row>
                                                                <b-row
                                                                    v-if="
                                                                        tasksLoading
                                                                    "
                                                                    ><b-col
                                                                        ><b-spinner
                                                                            small
                                                                            label="Loading..."
                                                                            :variant="
                                                                                profile.darkMode
                                                                                    ? 'light'
                                                                                    : 'dark'
                                                                            "
                                                                            class="mr-1"
                                                                        ></b-spinner></b-col
                                                                ></b-row>
                                                                <b-row
                                                                    v-else-if="
                                                                        !tasksLoading &&
                                                                        repeatingTasks.length ===
                                                                            0
                                                                    "
                                                                >
                                                                    <b-col>
                                                                        <p
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-light pl-3 pr-3'
                                                                                    : 'text-dark pl-3 pr-3'
                                                                            "
                                                                        >
                                                                            No
                                                                            repeating
                                                                            tasks
                                                                            are
                                                                            scheduled.
                                                                        </p>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-list-group
                                                                    v-else
                                                                    class="text-left m-0 p-0 mt-2 mb-2"
                                                                >
                                                                    <repeatingtaskblurb
                                                                        v-for="task in repeatingTasks"
                                                                        v-bind:key="
                                                                            task.name
                                                                        "
                                                                        :task="
                                                                            task
                                                                        "
                                                                    ></repeatingtaskblurb>
                                                                </b-list-group>

                                                                <b-row
                                                                    class="mt-3"
                                                                >
                                                                    <b-col
                                                                        ><b
                                                                            >Triggered</b
                                                                        ></b-col
                                                                    >
                                                                </b-row>
                                                                <b-row
                                                                    v-if="
                                                                        tasksLoading
                                                                    "
                                                                    ><b-col
                                                                        ><b-spinner
                                                                            small
                                                                            label="Loading..."
                                                                            :variant="
                                                                                profile.darkMode
                                                                                    ? 'light'
                                                                                    : 'dark'
                                                                            "
                                                                            class="mr-1"
                                                                        ></b-spinner></b-col
                                                                ></b-row>
                                                                <b-row
                                                                    v-else-if="
                                                                        !tasksLoading &&
                                                                        triggeredTasks.length ===
                                                                            0
                                                                    "
                                                                >
                                                                    <b-col>
                                                                        <p
                                                                            :class="
                                                                                profile.darkMode
                                                                                    ? 'text-light pl-3 pr-3'
                                                                                    : 'text-dark pl-3 pr-3'
                                                                            "
                                                                        >
                                                                            No
                                                                            triggered
                                                                            tasks
                                                                            are
                                                                            scheduled.
                                                                        </p>
                                                                    </b-col>
                                                                </b-row>
                                                                <b-list-group
                                                                    v-else
                                                                    class="text-left m-0 p-0 mt-2 mb-2"
                                                                >
                                                                    <triggeredtaskblurb
                                                                        v-for="task in triggeredTasks"
                                                                        v-bind:key="
                                                                            task.name
                                                                        "
                                                                        :task="
                                                                            task
                                                                        "
                                                                    ></triggeredtaskblurb>
                                                                </b-list-group>
                                                            </b-col>
                                                        </b-row> </b-col
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
import { guid } from '@/utils';
import delayedtaskblurb from '@/components/tasks/delayed-task-blurb';
import repeatingtaskblurb from '@/components/tasks/repeating-task-blurb';
import triggeredtaskblurb from '@/components/tasks/triggered-task-blurb';

String.prototype.capitalize = function () {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'workflow',
    components: {
        Multiselect,
        datatree,
        delayedtaskblurb,
        repeatingtaskblurb,
        triggeredtaskblurb,
    },
    props: {
        owner: {
            required: true,
        },
        name: {
            required: true,
        },
        branch: {
            required: true,
        },
    },
    data: function () {
        return {
            idVisible: false,
            timeLimitVisible: false,
            tagsVisible: false,
            inputVisible: false,
            outputVisible: false,
            parametersVisible: false,
            projectVisible: false,
            agentVisible: false,
            iterations: 1,
            timeLimit: 1,
            timeLimitUnits: 'Hours',
            selectedProject: null,
            selectedStudy: null,
            togglingPublic: false,
            selectedInput: null,
            selectedInputLoading: false,
            activeTab: 0,
            activeAgentTab: 0,
            submitting: false,
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
            taskGuid: guid().toString(),
            tags: [],
            tagOptions: [],
            params: [],
            input: {
                kind: '',
                from: '',
                filetypes: [],
            },
            inputSelectedPatterns: [],
            outputSelectedPatterns: [],
            outputSelectedNames: [],
            selectedOutput: null,
            outputSync: false,
            outputSpecified: false,
            output: {
                from: '',
                to: '',
                include: {
                    patterns: [],
                    names: [],
                },
                exclude: {
                    patterns: [],
                    names: [],
                },
            },
            selectedAgent: null,
        };
    },
    async mounted() {
        await this.loadWorkflow();
        this.populateComponents();

        if (
            this.getWorkflow.config.jobqueue !== undefined &&
            this.getWorkflow.config.jobqueue.walltime !== undefined
        ) {
            this.timeLimit = Math.max(
                1,
                parseInt(
                    this.getWorkflow.config.jobqueue.walltime.split(':')[0]
                )
            );
            this.timeLimitUnits = 'Hours';
        }

        if (
            this.getWorkflow.config.output !== undefined &&
            this.getWorkflow.config.output.include !== undefined &&
            this.getWorkflow.config.output.include.patterns !== undefined
        )
            this.outputSelectedPatterns =
                this.getWorkflow.config.output.include.patterns;

        if (
            this.getWorkflow.config.input !== undefined &&
            (this.selectedInput === null || !this.inputValid)
        )
            this.inputVisible = true;

        if (this.selectedOutput === null || !this.outputValid)
            this.outputVisible = true;

        if (this.selectedAgent === null) this.agentVisible = true;
    },
    methods: {
        sendFeaturedRequest() {},
        openInNewTab(url) {
            window.open(url);
        },
        // async deleteDelayed(name) {
        //     this.unschedulingDelayed = true;
        //     await axios
        //         .get(
        //             `/apis/v1/tasks/${this.profile.djangoProfile.username}/${name}/unschedule_delayed/`
        //         )
        //         .then(async (response) => {
        //             await Promise.all([
        //                 this.$store.dispatch(
        //                     'tasks/setDelayed',
        //                     response.data.tasks
        //                 ),
        //                 this.$store.dispatch('alerts/add', {
        //                     variant: 'success',
        //                     message: `Unscheduled delayed task`,
        //                     guid: guid().toString(),
        //                 }),
        //             ]);
        //             this.unschedulingDelayed = false;
        //         })
        //         .catch(async (error) => {
        //             Sentry.captureException(error);
        //             await this.$store.dispatch('alerts/add', {
        //                 variant: 'danger',
        //                 message: `Failed to unschedule delayed task`,
        //                 guid: guid().toString(),
        //             });
        //             this.unschedulingDelayed = false;
        //             throw error;
        //         });
        // },
        // async deleteRepeating(name) {
        //     this.unschedulingRepeating = true;
        //     await axios
        //         .get(
        //             `/apis/v1/tasks/${this.profile.djangoProfile.username}/${name}/unschedule_repeating/`
        //         )
        //         .then(async (response) => {
        //             await Promise.all([
        //                 this.$store.dispatch(
        //                     'tasks/setRepeating',
        //                     response.data.tasks
        //                 ),
        //                 this.$store.dispatch('alerts/add', {
        //                     variant: 'success',
        //                     message: `Unscheduled repeating task`,
        //                     guid: guid().toString(),
        //                 }),
        //             ]);
        //             this.unschedulingRepeating = false;
        //         })
        //         .catch(async (error) => {
        //             Sentry.captureException(error);
        //             await this.$store.dispatch('alerts/add', {
        //                 variant: 'danger',
        //                 message: `Failed to unschedule repeating task`,
        //                 guid: guid().toString(),
        //             });
        //             this.unschedulingRepeating = false;
        //             throw error;
        //         });
        // },
        setTimeLimitUnits(units) {
            this.timeLimitUnits = units;
        },
        prettifyDuration: function (dur) {
            return moment.duration(dur, 'seconds').humanize();
        },
        async loadSelectedInput(path) {
            this.selectedInputLoading = true;
            await axios({
                method: 'post',
                url: `https://de.cyverse.org/terrain/secured/filesystem/stat`,
                data: {
                    paths: [path],
                },
                headers: {
                    Authorization: `Bearer ${this.profile.djangoProfile.cyverse_token}`,
                },
            })
                .then(async (response) => {
                    if (response.data.paths !== undefined) {
                        this.selectedInput = response.data.paths[path];
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `This workflow's default input path ${path} does not exist`,
                            guid: guid().toString(),
                        });
                    }
                    this.selectedInputLoading = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to load this workflow's default input path ${path}`,
                        guid: guid().toString(),
                    });
                    this.selectedInputLoading = false;
                    throw error;
                });
        },
        async loadSelectedOutput(path) {
            this.selectedOutputLoading = true;

            await axios({
                method: 'post',
                url: `https://de.cyverse.org/terrain/secured/filesystem/stat`,
                data: {
                    paths: [path],
                },
                headers: {
                    Authorization: `Bearer ${this.profile.djangoProfile.cyverse_token}`,
                },
            })
                .then(async (response) => {
                    if (response.data.paths !== undefined) {
                        this.selectedOutput = response.data.paths[path];
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `The selected output path ${path} does not exist`,
                            guid: guid().toString(),
                        });
                    }
                    this.selectedOutputLoading = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to load the selected output path ${path}`,
                        guid: guid().toString(),
                    });
                    this.selectedOutputLoading = false;
                    throw error;
                });
        },
        async loadWorkflow() {
            await this.$store.dispatch('workflows/load', {
                owner: this.$router.currentRoute.params.owner,
                name: this.$router.currentRoute.params.name,
                branch: this.$router.currentRoute.params.branch,
            });
        },
        async refreshWorkflow() {
            await this.$store.dispatch('workflows/refresh', {
                owner: this.$router.currentRoute.params.owner,
                name: this.$router.currentRoute.params.name,
                branch: this.$router.currentRoute.params.branch,
            });
        },
        async unbindWorkflow() {
            await axios({
                method: 'delete',
                url: `/apis/v1/workflows/${this.$router.currentRoute.params.owner}/u/${this.$router.currentRoute.params.name}/${this.$router.currentRoute.params.branch}/unbind/`,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await Promise.all([
                            this.$store.dispatch(
                                'workflows/setPersonal',
                                response.data.workflows
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Removed binding for workflow ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`,
                                guid: guid().toString(),
                            }),
                        ]);
                        await router.push({
                            name: 'workflows',
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove binding for workflow ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`,
                            guid: guid().toString(),
                        });
                    }
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove binding for workflow ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`,
                        guid: guid().toString(),
                    });
                    throw error;
                });
        },
        parseCronTime(time) {
            let cron = cronstrue.toString(time);
            return cron.charAt(0).toLowerCase() + cron.slice(1);
        },
        prettify: function (date) {
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
                    value: param.default !== undefined ? param.default : '',
                };
            else if (param.type === 'select')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : null,
                    options: param.options,
                };
            else if (param.type === 'number')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : 0,
                    min: param.min,
                    max: param.max,
                    step: param.step,
                };
            else if (param.type === 'boolean')
                return {
                    name: param.name,
                    type: param.type,
                    value:
                        param.default !== undefined
                            ? param.default.toString().toLowerCase() === 'true'
                            : false,
                };
        },
        populateComponents() {
            if (this.getWorkflow !== null) {
                // if a local input path is specified, set it
                if ('input' in this.getWorkflow.config) {
                    this.input.path =
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
                        this.output.include.names =
                            this.getWorkflow.config.output.include.names;
                    if (
                        this.getWorkflow.config.output.include !== undefined &&
                        this.getWorkflow.config.output.include.patterns !==
                            undefined
                    )
                        this.output.include.patterns =
                            this.getWorkflow.config.output.include.patterns;
                    if (
                        this.getWorkflow.config.output.exclude !== undefined &&
                        this.getWorkflow.config.output.exclude.names !==
                            undefined
                    )
                        this.output.exclude.names =
                            this.getWorkflow.config.output.exclude.names;
                    if (
                        this.getWorkflow.config.output.exclude !== undefined &&
                        this.getWorkflow.config.output.exclude.patterns !==
                            undefined
                    )
                        this.output.exclude.patterns =
                            this.getWorkflow.config.output.exclude.patterns;
                }

                // if params are specified, set them
                if ('params' in this.getWorkflow['config'])
                    this.params = this.getWorkflow['config']['params'].map(
                        (param) => this.mapParam(param)
                    );
            }

            // if we have pre-configured values for this flow, populate them
            if ('last_config' in this.getWorkflow) {
                let lastConfig = this.getWorkflow['last_config'];
                this.params =
                    lastConfig.workflow.parameters !== undefined
                        ? lastConfig.workflow.parameters
                        : this.params;
                if (lastConfig.workflow.input !== undefined)
                    this.input = lastConfig.workflow.input;
                if (lastConfig.workflow.output !== undefined)
                    this.output = lastConfig.workflow.output;
                if (lastConfig.agent !== undefined)
                    if (
                        this.getAgents
                            .map((a) => a.name)
                            .includes(lastConfig.agent)
                    )
                        // make sure the agent used in the last submission still exists
                        this.selectedAgent = lastConfig.agent;
            }

            if (
                this.input !== undefined &&
                this.input.path !== undefined &&
                this.input.path !== null &&
                this.input.path !== ''
            )
                this.loadSelectedInput(this.input.path);

            if (
                this.output !== undefined &&
                this.output.to !== undefined &&
                this.output.to !== null &&
                this.output.to !== ''
            )
                this.loadSelectedOutput(this.output.to);
        },
        inputSelected(node) {
            this.input.path = node.path;
            this.loadSelectedInput(node.path);
            this.inputVisible = false;
        },
        outputSelected(node) {
            this.output.to = node.path;
            this.loadSelectedOutput(node.path);
            this.outputVisible = false;
        },
        agentSelected(agent) {
            this.selectedAgent = agent.name;
            this.agentVisible = false;
        },
        agentUnsupported(agent) {
            if (this.getWorkflow.config.jobqueue === undefined) return false;
            return (
                (parseInt(agent.max_mem) !== -1 &&
                    parseInt(agent.max_mem) < parseInt(this.memory)) ||
                parseInt(agent.max_cores) <
                    parseInt(this.getWorkflow.config.jobqueue.cores) ||
                parseInt(agent.max_processes) <
                    parseInt(this.getWorkflow.config.jobqueue.processes)
            );
            // TODO walltime
        },
        async submitImmediate(data) {
            await axios({
                method: 'post',
                url: `/apis/v1/tasks/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.data.created) {
                        await this.$store.dispatch(
                            'tasks/addOrUpdate',
                            response.data.task
                        );
                        await router.push({
                            name: 'task',
                            params: {
                                owner: this.profile.djangoProfile.username,
                                guid: this.taskGuid,
                            },
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to submit task ${this.taskGuid} to ${data.agent}`,
                            guid: guid().toString(),
                        });
                    }
                    this.submitting = false;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.submitting = false;
                    throw error;
                });
        },
        async submitDelayed(data) {
            data['eta'] = {
                units: this.delayUnits,
                delay: this.delayValue,
            };
            await axios({
                method: 'post',
                url: `/apis/v1/tasks/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200 && response.data.created) {
                        await Promise.all([
                            this.$store.dispatch(
                                'tasks/addDelayed',
                                response.data.task
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Scheduled task ${this.$router.currentRoute.params.name} on ${data.agent}`,
                                guid: guid().toString(),
                                time: moment().format(),
                            }),
                        ]);
                    } else
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to schedule task ${this.$router.currentRoute.params.name} on ${data.agent}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    this.submitting = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to schedule task ${this.$router.currentRoute.params.name} on ${data.agent}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.submitting = false;
                    throw error;
                });
        },
        async submitRepeating(data) {
            data['eta'] = {
                units: this.delayUnits,
                delay: this.delayValue,
            };
            await axios({
                method: 'post',
                url: `/apis/v1/tasks/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200 && response.data.created) {
                        await Promise.all([
                            this.$store.dispatch(
                                'tasks/addRepeating',
                                response.data.task
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Scheduled repeating task ${this.$router.currentRoute.params.name} on ${data.agent}`,
                                guid: guid().toString(),
                                time: moment().format(),
                            }),
                        ]);
                    } else
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to schedule task ${this.$router.currentRoute.params.name} on ${data.agent}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    this.submitting = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to schedule repeating task ${this.$router.currentRoute.params.name} on ${data.agent}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.submitting = false;
                    throw error;
                });
        },
        async submitTriggered(data) {
            data['eta'] = {
                units: this.delayUnits,
                delay: this.delayValue,
            };
            await axios({
                method: 'post',
                url: `/apis/v1/tasks/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200 && response.data.created) {
                        await Promise.all([
                            this.$store.dispatch(
                                'tasks/addTriggered',
                                response.data.task
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Scheduled triggered task for ${this.$router.currentRoute.params.name} on ${data.agent}`,
                                guid: guid().toString(),
                                time: moment().format(),
                            }),
                        ]);
                    } else
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to schedule task for ${this.$router.currentRoute.params.name} on ${data.agent}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    this.submitting = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to schedule trigger task ${this.$router.currentRoute.params.name} on ${data.agent}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.submitting = false;
                    throw error;
                });
        },
        async onStart() {
            this.submitting = true;

            // rebuild workflow configuration
            let workflow = {
                name: this.getWorkflow.config.name,
                public: this.getWorkflow.config.public,
                image: this.getWorkflow.config.image,
                parameters: this.params,
                commands: this.getWorkflow.config.commands,
                shell: this.getWorkflow.config.shell,
                logo: this.getWorkflow.config.logo,
                gpu: this.getWorkflow.config.gpu,
                env: this.getWorkflow.config.env,
                mount: this.getWorkflow.config.mount,
                iterations: Number(this.iterations),
                jobqueue:
                    this.getWorkflow.config.jobqueue !== undefined
                        ? this.getWorkflow.config.jobqueue
                        : {
                              walltime: '01:00:00',
                              memory: '10GB',
                              processes: 1,
                              cores: 1,
                          },
            };

            // configure user-selected inputs
            if (this.input !== undefined && this.input.path) {
                workflow.input = this.input;
                workflow.input.patterns =
                    this.inputSelectedPatterns.length > 0
                        ? this.inputSelectedPatterns
                        : this.input.filetypes;
            }

            // configure user-selected outputs
            if (this.output !== undefined && this.output.to) {
                workflow.output = {};
                workflow.output['to'] = this.output.to;
                if (
                    this.getWorkflow.config.output !== undefined &&
                    this.getWorkflow.config.output.path !== undefined
                )
                    workflow.output['from'] =
                        this.getWorkflow.config.output.path;
                else workflow.output['from'] = '';
                if (workflow.output.include === undefined)
                    workflow.output['include'] = {
                        patterns: [],
                        names: [],
                    };
                workflow.output.include.patterns = Array.from(
                    this.outputSelectedPatterns
                );
                workflow.output.include.names = Array.from(
                    this.outputSelectedNames
                );
            }

            // compose the request body
            var postData = {
                name: this.taskName === '' ? this.taskGuid : this.taskName,
                guid: this.taskGuid,
                type: this.submitType,
                time: {
                    limit: this.timeLimit,
                    units: this.timeLimitUnits,
                },
                tags: this.tags,
                workflow: workflow,
                repo: {
                    owner: this.getWorkflow.repo.owner.login,
                    name: this.getWorkflow.repo.name,
                    branch: this.getWorkflow.branch.name,
                },
                agent: this.selectedAgent,
                miappe: {},
            };

            // add MIAPPE project/study, if selected
            if (this.selectedProject !== null) {
                postData['miappe']['project'] = this.selectedProject.title;

                if (this.selectedStudy !== null)
                    postData['miappe']['study'] = this.selectedStudy.title;
            }

            // submit the task
            if (this.submitType === 'Now') await this.submitImmediate(postData);
            else if (this.submitType === 'After')
                await this.submitDelayed(postData);
            else if (this.submitType === 'Every')
                await this.submitRepeating(postData);
            else if (this.submitType === 'Watch')
                await this.submitTriggered(postData);
        },
    },
    watch: {
        userWorkflows: function () {
            // noop
        },
        getWorkflow: function () {
            // noop
        },
        selectedInput: function () {},
        iterations: function () {},
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', [
            'workflow',
            'publicWorkflowsLoading',
            'userWorkflowsLoading',
        ]),
        ...mapGetters('tasks', [
            'tasks',
            'task',
            'tasksLoading',
            'tasksDelayed',
            'tasksRepeating',
            'tasksTriggered',
        ]),
        ...mapGetters('agents', ['agentsLoading', 'agentsPermitted']),
        ...mapGetters('datasets', [
            'userDatasets',
            'publicDatasets',
            'sharedDatasets',
            'sharingDatasets',
            'userDatasetsLoading',
            'publicDatasetsLoading',
            'sharedDatasetsLoading',
            'sharingDatasetsLoading',
        ]),
        ...mapGetters('projects', ['userProjects', 'othersProjects']),
        walltime() {
            return this.getWorkflow.config.jobqueue.walltime !== undefined
                ? this.getWorkflow.config.jobqueue.walltime
                : this.getWorkflow.config.jobqueue.time !== undefined
                ? this.getWorkflow.config.jobqueue.time
                : null;
        },
        memory() {
            return this.getWorkflow.config.jobqueue.memory !== undefined
                ? this.getWorkflow.config.jobqueue.memory
                : this.getWorkflow.config.jobqueue.mem !== undefined
                ? this.getWorkflow.config.jobqueue.mem
                : null;
        },
        delayedTasks() {
            return this.tasksDelayed.filter(
                (t) =>
                    t.workflow_owner === this.getWorkflow.repo.owner.login &&
                    t.workflow_name === this.getWorkflow.repo.name &&
                    t.workflow_branch === this.getWorkflow.branch.name
            );
        },
        repeatingTasks() {
            return this.tasksRepeating.filter(
                (t) =>
                    t.workflow_owner === this.getWorkflow.repo.owner.login &&
                    t.workflow_name === this.getWorkflow.repo.name &&
                    t.workflow_branch === this.getWorkflow.branch.name
            );
        },
        triggeredTasks() {
            return this.tasksTriggered.filter(
                (t) =>
                    t.workflow_owner === this.getWorkflow.repo.owner.login &&
                    t.workflow_name === this.getWorkflow.repo.name &&
                    t.workflow_branch === this.getWorkflow.branch.name
            );
        },
        getAgents() {
            return this.agentsPermitted(this.profile.djangoProfile.username);
        },
        taskHistory() {
            return this.$store.getters['tasks/tasks'];
        },
        getWorkflow() {
            return this.workflow(this.owner, this.name, this.branch);
        },
        ownsWorkflow() {
            return (
                this.getWorkflow.repo.owner.login ===
                this.profile.githubProfile.login
            );
        },
        workflowLoading() {
            return this.publicWorkflowsLoading || this.userWorkflowsLoading;
        },
        scheduledTime() {
            return `${this.submitType === 'After' ? 'in' : 'every'} ${
                this.delayValue
            } ${this.delayUnits.toLowerCase()}`;
            // else return `${this.parseCronTime(this.crontime)}`;  TODO allow direct cron editing
        },
        workflowKey() {
            return `${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.name}`;
        },
        inputFiletypeSelected() {
            return this.inputSelectedPatterns.some((pattern) => pattern !== '');
        },
        taskNameExists() {
            return this.tasks.some((r) => r.name === this.taskName);
        },
        nameValid() {
            return !this.taskNameExists; // && !this.taskNameExists
        },
        paramsValid: function () {
            if (
                this.getWorkflow !== null &&
                this.getWorkflow.config.params !== undefined &&
                this.getWorkflow.config.params.length !== 0
            )
                return this.params.every(
                    (param) =>
                        param !== undefined &&
                        param.value !== undefined &&
                        param.value !== ''
                );
            else return true;
        },
        inputValid() {
            if (
                this.getWorkflow !== null &&
                this.getWorkflow.config.input !== undefined
            ) {
               return (
                    this.getWorkflow.config.input.kind !== undefined &&
                    this.input.kind !== '' &&
                    this.selectedInput !== null &&
                    this.selectedInput.path !== undefined &&
                    this.selectedInput.path !== null &&
                    this.selectedInput.path !== '' &&
                    !this.selectedInput.path.includes(' ') &&
                    ((this.input.kind !== 'directory' &&
                        this.inputFiletypeSelected) ||
                        this.input.kind === 'directory'));
            }
            return true;
        },
        outputValid: function () {
            // if (
            //     this.selectedOutput !== null &&
            //     this.getWorkflow &&
            //     this.getWorkflow.config &&
            //     this.getWorkflow.config.input !== undefined &&
            //     this.getWorkflow.config.output.to !== undefined
            // )
            return (
                this.output.to !== undefined &&
                this.output.to !== null &&
                this.output.to !== '' &&
                !this.output.to.includes(' ')
            );
            // return true;
        },
        agentValid() {
            return this.selectedAgent !== null && this.selectedAgent !== '';
        },
        canSubmit() {
            return (
                this.nameValid &&
                this.paramsValid &&
                this.inputValid &&
                this.outputValid &&
                this.agentValid
            );
        },
        workflowRunningPlotData() {
            return this.workflowTimeseries === null
                ? []
                : [
                      {
                          x: this.workflowTimeseries.x.map((t) =>
                              moment(t).format('YYYY-MM-DD HH:mm:ss')
                          ),
                          y: this.workflowTimeseries.y,
                          type: 'line',
                          line: { color: '#d6df5D', shape: 'spline' },
                      },
                  ];
        },
        workflowRunningPlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                title: {
                    // text: 'Workflow Usage',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    // orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    showticklabels: true,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)',
                        },
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)',
                        },
                    },
                },
                yaxis: {
                    dtick: 1,
                    showticklabels: false,
                },
                height: 300,
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
            };
        },
    },
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
