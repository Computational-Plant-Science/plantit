<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <div v-if="isRootPath">
            <b-row
                ><b-col
                    ><h2 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <i class="fas fa-stream fa-fw"></i>
                        Workflows
                    </h2></b-col
                >
                <b-col align-self="center" class="mb-1" md="auto">
                    <b-dropdown
                        dropleft
                        id="switch-workflow-context"
                        :disabled="workflowsLoading || bindingWorkflow"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        class="ml-0 mt-0 mr-0"
                        :title="context"
                        ><template #button-content>
                            <span v-if="context === profile.githubProfile.login"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else-if="context === ''"
                                ><i class="fas fa-users"></i> Public</span
                            ><span v-else
                                ><i class="fas fa-building"></i>
                                {{ context }}</span
                            >
                        </template>
                        <b-dropdown-item
                            @click="switchContext(profile.githubProfile.login)"
                            ><i class="fas fa-user fa-fw"></i>
                            Yours</b-dropdown-item
                        >
                        <b-dropdown-item @click="switchContext('')"
                            ><i class="fas fa-users fa-fw"></i>
                            Public</b-dropdown-item
                        >
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-header
                            >Your Organizations</b-dropdown-header
                        >
                        <b-dropdown-item
                            @click="switchContext(org.login)"
                            v-for="org in profile.githubOrganizations"
                            v-bind:key="org.login"
                            ><i class="fas fa-building fa-fw"></i>
                            {{ org.login }}</b-dropdown-item
                        >
                    </b-dropdown>
                    <b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="topleft"
                        target="switch-workflow-context"
                        title="Workflow Context"
                        >Click here to toggle between public, organization, and
                        your own personal workflow context.</b-popover
                    >
                </b-col>
                <b-col
                    md="auto"
                    class="ml-0 mb-1"
                    align-self="center"
                    v-if="context !== ''"
                    ><b-button
                        id="bind-workflow"
                        :disabled="bindingWorkflow || workflowsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Bind a new workflow"
                        @click="showBindWorkflowModal"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="bindingWorkflow"
                            label="Binding..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-plug mr-1"></i>Bind</b-button
                    ><b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="bottomleft"
                        target="bind-workflow"
                        title="Bind Workflow"
                        >Click here to bind a GitHub repository to a PlantIT
                        workflow.</b-popover
                    ></b-col
                >
                <b-col md="auto" class="ml-0 mb-1" align-self="center"
                    ><b-button
                        id="refresh-workflows"
                        :disabled="workflowsLoading || bindingWorkflow"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Refresh workflows"
                        @click="refreshWorkflows"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="workflowsLoading"
                            label="Refreshing..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i
                        >Refresh</b-button
                    ><b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="bottomright"
                        target="refresh-workflows"
                        title="Refresh Workflows"
                        >Click here to re-synchronize your workflows with GitHub
                        (helpful if you have introduced changes to a
                        <code>plantit.yaml</code> file).</b-popover
                    ></b-col
                >
                <b-col md="auto" align-self="center" class="mb-1"
                    ><small
                        >powered by
                        <i class="fab fa-github fa-fw fa-1x"></i></small
                    ><b-img
                        class="mt-1"
                        rounded
                        style="max-height: 1.2rem;"
                        right
                        :src="
                            profile.darkMode
                                ? require('../../assets/logos/github_white.png')
                                : require('../../assets/logos/github_black.png')
                        "
                    ></b-img></b-col
            ></b-row>
            <b-row v-if="workflowsLoading || bindingWorkflow" class="mt-2">
                <b-col>
                    <b-spinner
                        small
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading workflows...</span
                    >
                </b-col>
            </b-row>
            <b-card-group deck columns v-else-if="getWorkflows.length !== 0">
                <b-card
                    v-for="workflow in getWorkflows"
                    :key="workflow.repo.name"
                    :bg-variant="profile.darkMode ? 'dark' : 'white'"
                    :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                    border-variant="default"
                    :header-border-variant="
                        profile.darkMode ? 'secondary' : 'default'
                    "
                    :text-variant="profile.darkMode ? 'white' : 'dark'"
                    style="min-width: 30rem;"
                    class="overflow-hidden mb-4"
                >
                    <blurb :linkable="true" :workflow="workflow"></blurb>
                </b-card>
            </b-card-group>
            <b-row v-else
                ><b-col
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    >{{
                        context === ''
                            ? 'No workflows have been published by the community yet.'
                            : context === profile.githubProfile.login
                            ? "You haven't created any workflow bindings yet."
                            : 'This organization has no workflow bindings yet.'
                    }}</b-col
                ></b-row
            >
        </div>
        <router-view
            v-else
            :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
        ></router-view>
        <b-modal
            id="bindWorkflow"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            size="lg"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            hide-header
            hide-header-close
        >
            <template #modal-footer
                ><b-row v-if="bindingSelected">
                    <b-col md="auto"
                        ><b-button
                            :disabled="bindingWorkflow"
                            variant="outline-danger"
                            @click="unselectBinding"
                            ><i class="fas fa-arrow-left fa-fw"></i><br />Go
                            Back</b-button
                        ></b-col
                    ><b-col
                        ><b-button variant="success" @click="bindWorkflow"
                            ><i
                                v-if="!bindingWorkflow"
                                class="fas fa-check fa-fw"
                            ></i
                            ><b-spinner
                                small
                                v-else
                                label="Binding..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="mr-1"
                            ></b-spinner
                            ><br />Bind</b-button
                        ></b-col
                    ></b-row
                ><b-row v-else></b-row
            ></template>
            <!--<b-alert variant="danger" :show="searchResultAlreadyConnected"
                    >This workflow is already connected!</b-alert
                >-->
            <!--<b-form-group
                    description="Type the name of the GitHub repository you'd like to connect."
                >
                    <b-form-input
                        v-model="searchName"
                        :state="!searchResultInvalid"
                        type="text"
                        placeholder="Enter a repository name"
                        required
                    ></b-form-input>
                </b-form-group>
                <div class="text-center" v-if="searching">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </div>-->
            <b-row class="mb-2" v-if="!bindingSelected"
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Bind a workflow
                    </h4></b-col
                ><!--<b-col md="auto"
                    ><b-button
                        :disabled="personalWorkflowsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Rescan workflows"
                        @click="refreshWorkflows"
                        class="text-right"
                    >
                        <b-spinner
                            small
                            v-if="workflowsLoading"
                            label="Rescanning..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i>Rescan
                        Workflows</b-button
                    ></b-col
                >--></b-row
            >
            <div v-if="personalWorkflowsLoading">
                <b-row>
                    <b-col class="text-center">
                        <b-spinner
                            type="grow"
                            label="Loading..."
                            variant="secondary"
                        ></b-spinner>
                    </b-col>
                </b-row>
            </div>
            <div v-else-if="bindingSelected">
                <!--<b-row
                        ><b-col class="text-center"
                            ><span v-if="workflowToConnectSelected"
                                ><i
                                    class="fas fa-check fa-fw fa-3x text-success"
                                ></i>
                                </span
                            >
                        </b-col></b-row
                    ><b-row>-->
                <b-row>
                    <b-col
                        ><blurb :linkable="false" :workflow="binding"></blurb
                    ></b-col>
                </b-row>
            </div>
            <div class="text-center" v-else-if="bindableWorkflows.length === 0">
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    <!--Repository <b>{{ name }}</b> not found.-->
                    No connectable workflows found. Add a
                    <code>plantit.yaml</code> file to one of your repositories,
                    then click
                    <b-badge
                        :variant="profile.darkMode ? 'dark' : 'outline-light'"
                        ><i class="fas fa-redo mr-1"></i> Rescan
                        Workflows</b-badge
                    >
                    and it will appear here.
                </p>
            </div>
            <div v-else>
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    Select a <i class="fab fa-github fa-fw"></i>GitHub
                    repository and branch corresponding to your workflow. To
                    connect a workflow you must have a configuration file named
                    <code>plantit.yaml</code> in your project root.
                    <!-- If you don't
                    see your repo listed here, click
                    <b-badge
                        :variant="profile.darkMode ? 'dark' : 'outline-light'"
                        ><i class="fas fa-redo mr-1"></i> Rescan
                        Workflows</b-badge
                    >
                    to run a fresh scan for repositories with configuration
                    files.-->
                </p>
                <b-row class="mb-1"
                    ><b-col
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        ><small
                            >{{ bindableWorkflows.length }} workflow(s)
                            found</small
                        ></b-col
                    ></b-row
                >
                <b-card
                    :bg-variant="profile.darkMode ? 'dark' : 'white'"
                    :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                    border-variant="secondary"
                    :header-border-variant="profile.darkMode ? 'dark' : 'white'"
                    :text-variant="profile.darkMode ? 'white' : 'dark'"
                    class="overflow-hidden"
                    v-for="workflow in sortedBindableWorkflows"
                    v-bind:key="workflow.config.name + workflow.branch.name"
                    no-body
                    ><b-card-body class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
                        ><!--<b-row
                                ><b-col
                                    ><h4
                                        v-if="
                                            workflow.config.name !== undefined
                                        "
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        <i class="fas fa-stream text-success fa-fw"></i>
                                        {{ workflow.config.name }}
                                    </h4>
                                    <h4 v-else :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        ">
                                        <i
                                            class="fas fa-stream text-danger mr-2"
                                            ></i
                                            >
                                      <small>(name not provided)</small>
                                    </h4></b-col
                                ><b-col md="auto"
                                    ><b-button
                                        block
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        v-if="workflow.validation.is_valid"
                                        @click="
                                            selectWorkflowToConnect(workflow)
                                        "
                                        >Select</b-button
                                    ></b-col
                                ></b-row
                            >-->
                        <blurb :workflow="workflow" :linkable="false"></blurb>
                        <div v-if="workflow.validation.is_valid" class="mt-1">
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <b-row>
                                    <b-col>
                                        <small>Image</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{ workflow.config.image }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>GPU</small>
                                    </b-col>
                                    <b-col cols="10">
                                        {{ workflow.config.gpu ? 'Yes' : 'No' }}
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Mount</small>
                                    </b-col>
                                    <b-col cols="10">
                                        {{
                                            workflow.config.mount
                                                ? workflow.config.mount
                                                : 'None'
                                        }}
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Parameters</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            workflow.config.params
                                                ? workflow.config.params.length
                                                : 'None'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Command</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b
                                            ><code>{{
                                                ' ' + workflow.config.commands
                                            }}</code></b
                                        >
                                    </b-col>
                                </b-row>
                                <b-row
                                    v-if="workflow.config.input !== undefined"
                                >
                                    <b-col>
                                        <small>Input</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b
                                            ><code
                                                >[working directory]/input/{{
                                                    workflow.config.input
                                                        .filetypes
                                                        ? '[' +
                                                          (workflow.config.input
                                                              .filetypes
                                                              ? '*.' +
                                                                workflow.config.input.filetypes.join(
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
                                    v-if="workflow.config.output !== undefined"
                                >
                                    <b-col>
                                        <small>Output</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b
                                            ><code
                                                >[working directory]/{{
                                                    workflow.config.output.path
                                                        ? workflow.config.output
                                                              .path + '/'
                                                        : ''
                                                }}{{
                                                    workflow.config.output
                                                        .include
                                                        ? '[' +
                                                          (workflow.config
                                                              .output.exclude
                                                              ? '+ '
                                                              : '') +
                                                          (workflow.config
                                                              .output.include
                                                              .patterns
                                                              ? '*.' +
                                                                workflow.config.output.include.patterns.join(
                                                                    ', *.'
                                                                )
                                                              : []) +
                                                          (workflow.config
                                                              .output.include
                                                              .names
                                                              ? ', ' +
                                                                workflow.config.output.include.names.join(
                                                                    ', '
                                                                )
                                                              : [])
                                                        : ''
                                                }}{{
                                                    workflow.config.output
                                                        .exclude
                                                        ? ' - ' +
                                                          (workflow.config
                                                              .output.exclude
                                                              .patterns
                                                              ? '*.' +
                                                                workflow.config.output.exclude.patterns.join(
                                                                    ', *.'
                                                                )
                                                              : []) +
                                                          (workflow.config
                                                              .output.exclude
                                                              .names
                                                              ? ', ' +
                                                                workflow.config.output.exclude.names.join(
                                                                    ', '
                                                                )
                                                              : [])
                                                        : '' + ']'
                                                }}
                                            </code></b
                                        >
                                    </b-col>
                                </b-row>
                            </p>
                            <b-row>
                                <b-col
                                    ><b-button
                                        block
                                        variant="success"
                                        v-if="workflow.validation.is_valid"
                                        @click="selectBinding(workflow)"
                                        >Select</b-button
                                    ></b-col
                                >
                            </b-row>
                        </div>
                        <div v-else>
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <b class="text-danger">
                                    <i class="fas fa-exclamation-circle"></i>
                                    This workflow has configuration errors.
                                </b>
                                You must correct any configuration errors in
                                your <code>plantit.yaml</code> file before
                                connecting your repository.
                            </p>
                            <b-list-group class="mb-2">
                                <b-list-group-item
                                    v-for="error in workflow.validation.errors"
                                    v-bind:key="error"
                                    :variant="
                                        profile.darkMode ? 'dark' : 'light'
                                    "
                                    >{{ error }}</b-list-group-item
                                >
                            </b-list-group>
                            <json-viewer
                                :value="workflow.config"
                                :expand-depth="5"
                                copyable
                                boxed
                                sort
                                :theme="profile.darkMode ? 'darkjson' : 'light'"
                            ></json-viewer>
                        </div>
                    </b-card-body>
                </b-card>
            </div>
            <!--<div class="text-left" v-else-if="singleSearchResult">
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Repository Details
                    </h5>
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <b-link
                            target="_blank"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :href="searchResult[0].repo.html_url"
                            ><i class="fab fa-github fa-fw mr-1"></i
                            >{{ searchResult[0].repo.full_name }}</b-link
                        ><i class="far fa-star fa-fw ml-2 mr-1">{{
                            searchResult[0].repo.stargazers_count
                        }}</i>
                        <br />
                        {{ searchResult[0].repo.description }}
                        <br />
                        Last updated:
                        {{ prettify(searchResult[0].repo.updated_at) }}
                        <br />
                        Language: {{ searchResult[0].repo.language }}
                    </p>
                </div>-->
        </b-modal>
    </b-container>
</template>

<script>
import blurb from '@/components/workflows/workflow-blurb.vue';
import { mapGetters } from 'vuex';
import * as Sentry from '@sentry/browser';
import axios from 'axios';
import moment from 'moment';
import { guid } from '@/utils';
import JsonViewer from 'vue-json-viewer';

export default {
    name: 'workflows',
    components: {
        blurb,
        JsonViewer
    },
    data: function() {
        return {
            login: false,
            name: '',
            binding: null,
            bindingWorkflow: false,
            // bindingBranch: '',
            // bindingBranchOptions: [],
            loadingBranchOptions: false,
            context: '',
            contextToggling: false
        };
    },
    watch: {
        // TODO get rid of this, it's hacky
        // eslint-disable-next-line no-unused-vars
        boundWorkflows: function() {
            // noop
        },
        publicWorkflows: function() {
            // noop
        }
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        switchContext(ctx) {
            this.contextToggling = true;
            this.context = ctx;
            this.contextToggling = false;
        },
        // onWorkflowNameChange: debounce(function() {
        //     this.searching = true;
        //     return axios
        //         .get(
        //             `/apis/v1/workflows/${this.profile.githubProfile.login}/?connectable=${this.searchName}`
        //         )
        //         .then(response => {
        //             this.searchResult = response.data.workflows;
        //             this.searching = false;
        //             this.$emit('input', this.searchName);
        //         })
        //         .catch(error => {
        //             Sentry.captureException(error);
        //             this.searchResult = null;
        //             this.searching = false;
        //             if (error.response.status === 500) throw error;
        //         });
        // }, 500),
        // async loadBindingWorkflowRepoBranches() {
        //     this.bindingBranch = '';
        //     this.loadingBranchOptions = true;
        //     await axios
        //         .get(
        //             `/apis/v1/workflows/${this.binding.repo.owner.login}/${this.binding.repo.name}/branches/`
        //         )
        //         .then(async response => {
        //             if (response.status === 200) {
        //                 await Promise.all([
        //                     this.$store.dispatch('alerts/add', {
        //                         variant: 'success',
        //                         message: `Listed repository branches for ${this.binding.repo.owner.login}/${this.binding.repo.name}`,
        //                         guid: guid().toString(),
        //                         time: moment().format()
        //                     })
        //                 ]);
        //                 this.bindingBranchOptions = response.data.branches;
        //                 this.loadingBranchOptions = false;
        //             } else {
        //                 await this.$store.dispatch('alerts/add', {
        //                     variant: 'danger',
        //                     message: `Failed to list repository branches for ${this.binding.repo.owner.login}/${this.binding.repo.name}`,
        //                     guid: guid().toString(),
        //                     time: moment().format()
        //                 });
        //                 this.bindingBranchOptions = [];
        //                 this.loadingBranchOptions = false;
        //             }
        //         })
        //         .catch(async error => {
        //             Sentry.captureException(error);
        //             await this.$store.dispatch('alerts/add', {
        //                 variant: 'danger',
        //                 message: `Failed to list repository branches for ${this.binding.repo.owner.login}/${this.binding.repo.name}`,
        //                 guid: guid().toString(),
        //                 time: moment().format()
        //             });
        //             this.bindingBranchOptions = [];
        //             this.loadingBranchOptions = false;
        //             throw error;
        //         });
        // },
        showBindWorkflowModal() {
            this.$bvModal.show('bindWorkflow');
        },
        async bindWorkflow() {
            this.bindingWorkflow = true;
            // this.binding['branch'] = this.bindingBranch;
            await axios({
                method: 'post',
                url: `/apis/v1/workflows/${this.binding.repo.owner.login}/u/${this.binding.repo.name}/bind/`,
                data: this.binding,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        this.$bvModal.hide('bindWorkflow');
                        await Promise.all([
                            this.$store.dispatch(
                                'workflows/setPersonal',
                                response.data.workflows
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Created binding for workflow ${this.binding.repo.owner.login}/${this.binding.repo.name}`,
                                guid: guid().toString(),
                                time: moment().format()
                            })
                        ]);
                        this.binding = null;
                        this.bindingWorkflow = false;
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to bind workflow ${this.binding.repo.owner.login}/${this.binding.repo.name}`,
                            guid: guid().toString(),
                            time: moment().format()
                        });
                        this.$bvModal.hide('bindWorkflow');
                        this.binding = null;
                        this.bindingWorkflow = false;
                    }
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to connect ${this.binding.repo.owner.login}/${this.binding.repo.name}`,
                        guid: guid().toString(),
                        time: moment().format()
                    });
                    this.binding = null;
                    this.bindingWorkflow = false;
                    throw error;
                });
        },
        sortWorkflows(left, right) {
            if (left.config.name < right.config.name) return -1;
            if (left.config.name > right.config.name) return 1;
            return 0;
        },
        async refreshWorkflows() {
            if (this.context === '')
                await this.$store.dispatch('workflows/refreshPublic');
            else if (this.context === this.profile.githubProfile.login)
                await this.$store.dispatch(
                    'workflows/refreshPersonal',
                    this.profile.githubProfile.login
                );
            else
                await this.$store.dispatch(
                    'workflows/refreshOrg',
                    this.context
                );
        },
        selectBinding(workflow) {
            this.binding = workflow;
            this.loadBindingWorkflowRepoBranches();
        },
        unselectBinding() {
            this.binding = null;
        }
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('workflows', [
            'boundWorkflows',
            'orgWorkflows',
            'orgWorkflowsLoading',
            'personalWorkflowsLoading',
            'publicWorkflows',
            'publicWorkflowsLoading',
            'boundWorkflows',
            'bindableWorkflows'
        ]),
        sortedBindableWorkflows() {
            let bindable =
                this.context === this.profile.githubProfile.login
                    ? this.bindableWorkflows
                    : this.context === ''
                    ? []
                    : this.orgWorkflows[this.context].filter(wf => {
                          return wf.bound;
                      });
            return [...bindable].sort(function(a, b) {
                if (a.config.name === b.config.name) {
                    if (a.branch.name < b.branch.name) return -1;
                    if (a.branch.name > b.branch.name) return 1;
                    return 0;
                } else {
                    if (a.config.name < b.config.name) return -1;
                    if (a.config.name > b.config.name) return 1;
                    return 0;
                }
            });
        },
        isRootPath() {
            return this.$route.name === 'workflows';
        },
        getWorkflows() {
            return this.context === ''
                ? this.publicWorkflows
                : this.context === this.profile.githubProfile.login
                ? this.boundWorkflows
                : this.orgWorkflows[this.context];
            // return (this.contextPublic
            //     ? this.publicWorkflows
            //     : this.personalWorkflows
            // ).filter(workflow =>
            //     workflow.config.name.includes(this.searchName)
            // );
        },
        workflowsLoading() {
            return this.context === ''
                ? this.publicWorkflowsLoading
                : this.context === this.profile.githubProfile.login
                ? this.personalWorkflowsLoading
                : this.orgWorkflowsLoading;
        },
        bindingSelected() {
            return this.binding !== null;
        }
        // bindingBranchSelected() {
        //   return this.bindingBranch !== '';
        // }
    }
};
</script>
<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.darkjson
  background: #fff
  white-space: nowrap
  color: #525252
  font-size: 14px
  font-family: Consolas, Menlo, Courier, monospace

  .jv-ellipsis
    color: #999
    background-color: #eee
    display: inline-block
    line-height: 0.9
    font-size: 0.9em
    padding: 0px 4px 2px 4px
    border-radius: 3px
    vertical-align: 2px
    cursor: pointer
    user-select: none

  .jv-button
    color: #49b3ff
  .jv-key
    color: #111111
  .jv-item
    &.jv-array
      color: #111111
    &.jv-boolean
      color: #fc1e70
    &.jv-function
      color: #067bca
    &.jv-number
      color: #fc1e70
    &.jv-number-float
      color: #fc1e70
    &.jv-number-integer
      color: #fc1e70
    &.jv-object
      color: #111111
    &.jv-undefined
      color: #e08331
    &.jv-string
      color: #42b983
      word-break: break-word
      white-space: normal
  .jv-code
    .jv-toggle
      &:before
        padding: 0px 2px
        border-radius: 2px
      &:hover
        &:before
          background: #eee
</style>
