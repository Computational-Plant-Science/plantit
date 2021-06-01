<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <div v-if="profileLoading">
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
        <div v-else>
            <div v-if="isRootPath">
                <b-row
                    ><b-col
                        ><h2
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            {{ publicContext ? 'Public' : 'Your' }} Workflows
                        </h2></b-col
                    ><b-col md="auto" align-self="center"
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
                        ></b-img
                    ></b-col>
                    <b-col
                        md="auto"
                        class="ml-0"
                        align-self="center"
                        v-if="!publicContext"
                        ><b-button
                            :disabled="workflowsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            title="Connect a new workflow"
                            @click="showConnectWorkflowModal"
                            class="ml-0 mt-0 mr-0"
                        >
                            <b-spinner
                                small
                                v-if="workflowsLoading"
                                label="Connecting..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="mr-1"
                            ></b-spinner
                            ><i v-else class="fas fa-plug mr-1"></i
                            >Connect</b-button
                        ></b-col
                    >
                    <b-col md="auto" class="ml-0" align-self="center"
                        ><b-button
                            :disabled="workflowsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
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
                        ></b-col
                    >
                    <b-col md="auto" align-self="center"
                        ><b-button
                            :disabled="workflowsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            class="ml-0 mt-0 mr-0"
                            @click="toggleContext"
                            :title="
                                publicContext
                                    ? 'View your workflows'
                                    : 'View public workflows'
                            "
                            v-b-tooltip:hover
                            ><span v-if="publicContext"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else
                                ><i class="fas fa-users"></i> Public</span
                            ></b-button
                        ></b-col
                    ></b-row
                >
                <hr class="mt-2 mb-2" style="border-color: gray" />
                <b-row v-if="workflowsLoading" class="mt-2">
                    <b-col class="text-center">
                        <b-spinner
                            type="grow"
                            label="Loading..."
                            variant="secondary"
                        ></b-spinner>
                    </b-col>
                </b-row>
                <b-card-group
                    deck
                    columns
                    v-else-if="getWorkflows.length !== 0"
                >
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
                        <blurb :showPublic="false" :workflow="workflow"></blurb>
                    </b-card>
                </b-card-group>
                <b-row v-else
                    ><b-col class="text-danger">{{
                        publicContext
                            ? 'No workflows have been published by the community yet.'
                            : "You haven't connected any workflows yet."
                    }}</b-col></b-row
                >
            </div>
            <router-view
                v-else
                :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
            ></router-view>
            <b-modal
                id="connectWorkflow"
                :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
                centered
                close
                size="lg"
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-border-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
                title="Connect Workflow"
                @ok="connectWorkflow"
                :ok-disabled="workflowInvalid"
                ok-title="Connect"
            >
                <div class="text-left">
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Specify the GitHub repository containing your workflow.
                        Before a repository can be connected, you must have a
                        file named <code>plantit.yaml</code> in your project
                        root.
                    </p>
                </div>
                <b-form-group
                    description="Type the name of the GitHub repository you'd like to connect."
                >
                    <b-form-input
                        v-model="workflowName"
                        :state="!workflowInvalid"
                        type="text"
                        placeholder="Enter a repository name"
                        required
                        @input="onWorkflowNameChange"
                    ></b-form-input>
                </b-form-group>
                <div class="text-center" v-if="isLoading">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </div>
                <div
                    class="text-center"
                    v-else-if="
                        workflowSearchResult === null && workflowName !== ''
                    "
                >
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Repository <b>{{ workflowName }}</b> not found.
                    </p>
                </div>
                <div
                    class="text-left"
                    v-else-if="workflowSearchResult !== null"
                >
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Repository Details
                    </h5>
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <b-link
                            target="_blank"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :href="workflowSearchResult.repo.html_url"
                            ><i class="fab fa-github fa-fw mr-1"></i
                            >{{ workflowSearchResult.repo.full_name }}</b-link
                        >
                        <br />
                        {{ workflowSearchResult.repo.description }}
                        <br />
                        Last updated:
                        {{ prettify(workflowSearchResult.repo.updated_at) }}
                        <br />
                        Language: {{ workflowSearchResult.repo.language }}
                        <br />
                        Stargazers:
                        {{ workflowSearchResult.repo.stargazers_count }}
                    </p>
                    <div v-if="workflowSearchResult.validation.is_valid">
                        <h5
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Configuration
                        </h5>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            <b-row>
                                <b-col>
                                    <small>Image</small>
                                </b-col>
                                <b-col cols="10">
                                    <b>{{
                                        workflowSearchResult.config.image
                                    }}</b>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>GPU</small>
                                </b-col>
                                <b-col cols="10">
                                    {{
                                        workflowSearchResult.config.gpu
                                            ? 'Yes'
                                            : 'No'
                                    }}
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>Mount</small>
                                </b-col>
                                <b-col cols="10">
                                    {{
                                        workflowSearchResult.config.mount
                                            ? workflowSearchResult.config.mount
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
                                        workflowSearchResult.config.params
                                            ? workflowSearchResult.config.params
                                                  .length
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
                                            ' ' +
                                                workflowSearchResult.config
                                                    .commands
                                        }}</code></b
                                    >
                                </b-col>
                            </b-row>
                            <b-row
                                v-if="
                                    workflowSearchResult.config.input !==
                                        undefined
                                "
                            >
                                <b-col>
                                    <small>Input</small>
                                </b-col>
                                <b-col cols="10">
                                    <b
                                        ><code
                                            >[working directory]/input/{{
                                                workflowSearchResult.config
                                                    .input.filetypes
                                                    ? '[' +
                                                      (workflowSearchResult
                                                          .config.input
                                                          .filetypes
                                                          ? '*.' +
                                                            workflowSearchResult.config.input.filetypes.join(
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
                                    workflowSearchResult.config.output !==
                                        undefined
                                "
                            >
                                <b-col>
                                    <small>Output</small>
                                </b-col>
                                <b-col cols="10">
                                    <b
                                        ><code
                                            >[working directory]/{{
                                                workflowSearchResult.config
                                                    .output.path
                                                    ? workflowSearchResult
                                                          .config.output.path +
                                                      '/'
                                                    : ''
                                            }}{{
                                                workflowSearchResult.config
                                                    .output.include
                                                    ? '[' +
                                                      (workflowSearchResult
                                                          .config.output.exclude
                                                          ? '+ '
                                                          : '') +
                                                      (workflowSearchResult
                                                          .config.output.include
                                                          .patterns
                                                          ? '*.' +
                                                            workflowSearchResult.config.output.include.patterns.join(
                                                                ', *.'
                                                            )
                                                          : []) +
                                                      (workflowSearchResult
                                                          .config.output.include
                                                          .names
                                                          ? ', ' +
                                                            workflowSearchResult.config.output.include.names.join(
                                                                ', '
                                                            )
                                                          : [])
                                                    : ''
                                            }}{{
                                                workflowSearchResult.config
                                                    .output.exclude
                                                    ? ' - ' +
                                                      (workflowSearchResult
                                                          .config.output.exclude
                                                          .patterns
                                                          ? '*.' +
                                                            workflowSearchResult.config.output.exclude.patterns.join(
                                                                ', *.'
                                                            )
                                                          : []) +
                                                      (workflowSearchResult
                                                          .config.output.exclude
                                                          .names
                                                          ? ', ' +
                                                            workflowSearchResult.config.output.exclude.names.join(
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
                    </div>
                    <div v-else>
                        <h5 class="text-danger">
                            <i class="fas fa-exclamation-circle"></i>
                            Configuration Errors
                        </h5>
                        <b-list-group class="mb-2">
                            <b-list-group-item
                                v-for="error in workflowSearchResult.validation
                                    .errors"
                                v-bind:key="error"
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                >{{ error }}</b-list-group-item
                            >
                        </b-list-group>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            You must correct any configuration errors in your
                            <code>plantit.yaml</code> file before connecting
                            your repository.
                        </p>
                    </div>
                </div>
                <div></div>
            </b-modal>
        </div>
    </b-container>
</template>

<script>
import blurb from '@/components/workflows/workflow-blurb.vue';
import { mapGetters } from 'vuex';
import * as Sentry from '@sentry/browser';
import axios from 'axios';
import moment from 'moment';

export default {
    name: 'workflows',
    components: {
        blurb
    },
    data: function() {
        return {
            login: false,
            workflowName: '',
            workflowSearchResult: null,
            workflowExists: false,
            publicContext: false,
            togglingContext: false,
            isOpen: false,
            isLoading: false,
            isAsync: false
        };
    },
    async mounted() {
        // await Promise.all([
        //     this.$store.dispatch(
        //         'workflows/loadPersonal',
        //         this.profile.githubProfile.login
        //     ),
        //     this.$store.dispatch('workflows/loadPublic')
        // ]);
    },
    watch: {
        // TODO get rid of this, it's hacky
        // eslint-disable-next-line no-unused-vars
        publicContext: function(_) {
            this.refreshWorkflows();
        },
        // eslint-disable-next-line no-unused-vars
        items: function(value, _) {
            if (this.isAsync) {
                this.workflowSearchResult = value;
                this.isLoading = false;
            }
        }
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        toggleContext() {
            this.togglingContext = true;
            this.publicContext = !this.publicContext;
            this.togglingContext = false;
        },
        onWorkflowNameChange() {
            this.isLoading = true;
            return axios
                .get(
                    `/apis/v1/workflows/${this.profile.githubProfile.login}/${this.workflowName}/search/`
                )
                .then(response => {
                    this.workflowSearchResult = response.data;
                    this.isLoading = false;
                    this.$emit('input', this.workflowName);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.workflowSearchResult = null;
                    this.isLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        handleClickOutside(event) {
            if (!this.$el.contains(event.target)) {
                this.arrowCounter = -1;
                this.isOpen = false;
            }
        },
        showConnectWorkflowModal() {
            this.$bvModal.show('connectWorkflow');
        },
        async connectWorkflow() {
            await axios({
                method: 'post',
                url: `/apis/v1/workflows/${this.workflowSearchResult.repo.owner.login}/${this.workflowSearchResult.repo.name}/connect/`,
                data: this.workflowSearchResult,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    if (response.status === 200 && response.data.connected)
                        this.$store.dispatch(
                            'workflows/loadPersonal',
                            this.profile.githubProfile.login
                        );
                    else {
                        this.alertMessage = `Failed to connect ${this.workflowSearchResult.repo.owner.login}/${this.workflowSearchResult.repo.name}`;
                        this.alertEnabled = true;
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to connect ${this.workflowSearchResult.repo.owner.login}/${this.workflowSearchResult.repo.name}`;
                    this.alertEnabled = true;
                    throw error;
                });
        },
        sortWorkflows(left, right) {
            if (left.config.name < right.config.name) return -1;
            if (left.config.name > right.config.name) return 1;
            return 0;
        },
        refreshWorkflows() {
            if (this.publicContext)
                this.$store.dispatch('workflows/loadPublic');
            else
                this.$store.dispatch(
                    'workflows/loadPersonal',
                    this.profile.githubProfile.login
                );
        }
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('workflows', [
            'personalWorkflows',
            'personalWorkflowsLoading',
            'publicWorkflows',
            'publicWorkflowsLoading'
        ]),
        isRootPath() {
            return this.$route.name === 'workflows';
        },
        getWorkflows() {
            return this.publicContext
                ? this.publicWorkflows
                : this.personalWorkflows;
        },
        workflowsLoading() {
            return this.publicContext
                ? this.publicWorkflowsLoading
                : this.personalWorkflowsLoading;
        },
        workflowInvalid() {
            return (
                this.workflowSearchResult === null ||
                !this.workflowSearchResult.validation.is_valid
            );
        }
    }
};
</script>
<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
