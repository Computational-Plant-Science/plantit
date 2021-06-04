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
                            <i class="fas fa-stream fa-fw"></i>
                            {{ contextPublic ? 'Public' : 'Your' }} Workflows
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
                        v-if="!contextPublic"
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
                                contextPublic
                                    ? 'View your workflows'
                                    : 'View public workflows'
                            "
                            v-b-tooltip:hover
                            ><span v-if="contextPublic"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else
                                ><i class="fas fa-users"></i> Public</span
                            ></b-button
                        ></b-col
                    ></b-row
                >
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
                        contextPublic
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
                :ok-disabled="searchResultInvalid"
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
                <b-alert variant="danger" :show="searchResultAlreadyConnected"
                    >This workflow is already connected!</b-alert
                >
                <b-form-group
                    description="Type the name of the GitHub repository you'd like to connect."
                >
                    <b-form-input
                        v-model="searchName"
                        :state="!searchResultInvalid"
                        type="text"
                        placeholder="Enter a repository name"
                        required
                        @input="onWorkflowNameChange"
                    ></b-form-input>
                </b-form-group>
                <div class="text-center" v-if="searching">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </div>
                <div
                    class="text-center"
                    v-else-if="searchResult === null && name !== ''"
                >
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Repository <b>{{ name }}</b> not found.
                    </p>
                </div>
                <div class="text-left" v-else-if="searchResult !== null">
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Repository Details
                    </h5>
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <b-link
                            target="_blank"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :href="searchResult.repo.html_url"
                            ><i class="fab fa-github fa-fw mr-1"></i
                            >{{ searchResult.repo.full_name }}</b-link
                        ><i class="far fa-star fa-fw ml-2 mr-1">{{
                            searchResult.repo.stargazers_count
                        }}</i>
                        <br />
                        {{ searchResult.repo.description }}
                        <br />
                        Last updated:
                        {{ prettify(searchResult.repo.updated_at) }}
                        <br />
                        Language: {{ searchResult.repo.language }}
                    </p>
                    <div v-if="searchResult.validation.is_valid">
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
                                    <b>{{ searchResult.config.image }}</b>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>GPU</small>
                                </b-col>
                                <b-col cols="10">
                                    {{ searchResult.config.gpu ? 'Yes' : 'No' }}
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>Mount</small>
                                </b-col>
                                <b-col cols="10">
                                    {{
                                        searchResult.config.mount
                                            ? searchResult.config.mount
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
                                        searchResult.config.params
                                            ? searchResult.config.params.length
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
                                            ' ' + searchResult.config.commands
                                        }}</code></b
                                    >
                                </b-col>
                            </b-row>
                            <b-row
                                v-if="searchResult.config.input !== undefined"
                            >
                                <b-col>
                                    <small>Input</small>
                                </b-col>
                                <b-col cols="10">
                                    <b
                                        ><code
                                            >[working directory]/input/{{
                                                searchResult.config.input
                                                    .filetypes
                                                    ? '[' +
                                                      (searchResult.config.input
                                                          .filetypes
                                                          ? '*.' +
                                                            searchResult.config.input.filetypes.join(
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
                                v-if="searchResult.config.output !== undefined"
                            >
                                <b-col>
                                    <small>Output</small>
                                </b-col>
                                <b-col cols="10">
                                    <b
                                        ><code
                                            >[working directory]/{{
                                                searchResult.config.output.path
                                                    ? searchResult.config.output
                                                          .path + '/'
                                                    : ''
                                            }}{{
                                                searchResult.config.output
                                                    .include
                                                    ? '[' +
                                                      (searchResult.config
                                                          .output.exclude
                                                          ? '+ '
                                                          : '') +
                                                      (searchResult.config
                                                          .output.include
                                                          .patterns
                                                          ? '*.' +
                                                            searchResult.config.output.include.patterns.join(
                                                                ', *.'
                                                            )
                                                          : []) +
                                                      (searchResult.config
                                                          .output.include.names
                                                          ? ', ' +
                                                            searchResult.config.output.include.names.join(
                                                                ', '
                                                            )
                                                          : [])
                                                    : ''
                                            }}{{
                                                searchResult.config.output
                                                    .exclude
                                                    ? ' - ' +
                                                      (searchResult.config
                                                          .output.exclude
                                                          .patterns
                                                          ? '*.' +
                                                            searchResult.config.output.exclude.patterns.join(
                                                                ', *.'
                                                            )
                                                          : []) +
                                                      (searchResult.config
                                                          .output.exclude.names
                                                          ? ', ' +
                                                            searchResult.config.output.exclude.names.join(
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
                                v-for="error in searchResult.validation.errors"
                                v-bind:key="error"
                                :variant="profile.darkMode ? 'dark' : 'light'"
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
import debounce from 'lodash/debounce';
import axios from 'axios';
import moment from 'moment';
import { guid } from '@/utils';

export default {
    name: 'workflows',
    components: {
        blurb
    },
    data: function() {
        return {
            login: false,
            name: '',
            contextPublic: false,
            contextToggling: false,
            searching: false,
            searchName: '',
            searchResult: null
        };
    },
    watch: {
        // TODO get rid of this, it's hacky
        // eslint-disable-next-line no-unused-vars
        contextPublic: function(_) {
            this.refreshWorkflows();
        }
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        toggleContext() {
            this.contextToggling = true;
            this.contextPublic = !this.contextPublic;
            this.contextToggling = false;
        },
        onWorkflowNameChange: debounce(function() {
            this.searching = true;
            return axios
                .get(
                    `/apis/v1/workflows/${this.profile.githubProfile.login}/${this.searchName}/search/`
                )
                .then(response => {
                    this.searchResult = response.data;
                    this.searching = false;
                    this.$emit('input', this.searchName);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.searchResult = null;
                    this.searching = false;
                    if (error.response.status === 500) throw error;
                });
        }, 500),
        showConnectWorkflowModal() {
            this.$bvModal.show('connectWorkflow');
        },
        async connectWorkflow() {
            await axios({
                method: 'post',
                url: `/apis/v1/workflows/${this.searchResult.repo.owner.login}/${this.searchResult.repo.name}/connect/`,
                data: this.searchResult,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    if (response.status === 200 && response.data.connected) {
                        this.$store.dispatch(
                            'workflows/loadPersonal',
                            this.profile.githubProfile.login
                        );
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Added workflow ${this.searchResult.repo.name}`,
                            guid: guid().toString()
                        });
                    } else {
                        this.alertMessage = `Failed to connect ${this.searchResult.repo.owner.login}/${this.searchResult.repo.name}`;
                        this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to add workflow ${this.searchResult.repo.name}`,
                            guid: guid().toString()
                        });
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to connect ${this.searchResult.repo.owner.login}/${this.searchResult.repo.name}`;
                    this.alertEnabled = true;
                    throw error;
                });
        },
        sortWorkflows(left, right) {
            if (left.config.name < right.config.name) return -1;
            if (left.config.name > right.config.name) return 1;
            return 0;
        },
        async refreshWorkflows() {
            if (this.contextPublic)
                await this.$store.dispatch('workflows/loadPublic');
            else
                await this.$store.dispatch(
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
            return (this.contextPublic
                ? this.publicWorkflows
                : this.personalWorkflows
            ).filter(workflow =>
                workflow.config.name.includes(this.searchName)
            );
        },
        workflowsLoading() {
            return this.contextPublic
                ? this.publicWorkflowsLoading
                : this.personalWorkflowsLoading;
        },
        searchResultAlreadyConnected() {
            return (
                this.searchResult !== null &&
                (this.personalWorkflows.some(
                    wf => wf.config.name === this.searchResult.config.name
                ) ||
                    this.publicWorkflows.some(
                        wf =>
                            wf.config.name === this.searchResult.config.name &&
                            wf.repo.owner.login ===
                                this.searchResult.repo.owner.login
                    ))
            );
        },
        searchResultInvalid() {
            return (
                this.searchResult === null ||
                (this.searchResult.validation !== null &&
                    !this.searchResult.validation.is_valid) ||
                this.searchResultAlreadyConnected
            );
        }
    }
};
</script>
<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
