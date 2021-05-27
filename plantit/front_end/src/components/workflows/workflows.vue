<template>
    <b-container fluid>
        <div v-if="selected === null">
            <b-row
                ><b-col md="auto"
                    ><h2 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Workflows
                    </h2></b-col
                ><b-col md="auto" class="ml-0" align-self="middle"
                    ><b-button
                        :disabled="personalLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="md"
                        v-b-tooltip.hover
                        title="Refresh workflows"
                        @click="refreshWorkflows"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="personalLoading"
                            label="Refreshing..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i
                        >Refresh</b-button
                    ></b-col
                ><b-col class="ml-0" align-self="middle"
                    ><b-button
                        :disabled="personalLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="md"
                        v-b-tooltip.hover
                        title="Connect a new workflow"
                        @click="showConnectWorkflowModal"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="personalLoading"
                            label="Connecting..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-plug mr-1"></i
                        >Connect</b-button
                    ></b-col
                ></b-row
            >
            <hr class="mt-2 mb-2" style="border-color: gray" />
            <b-card-group deck columns>
                <b-card
                    v-for="workflow in workflows"
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
                    <blurb
                        :showPublic="false"
                        :workflow="workflow"
                        v-on:selectWorkflow="selectWorkflow"
                    ></blurb>
                </b-card>
            </b-card-group>
        </div>
        <div v-else class="p-2">
            <b-row>
                <b-col>
                    <b-button
                        @click="back"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="md"
                        v-b-tooltip.hover
                        title="Back to workflows"
                        class="text-left"
                        ><i class="fas fa-caret-left fa-fw"></i
                        >Workflows</b-button
                    >
                </b-col>
            </b-row>
            <hr class="mt-2 mb-2" style="border-color: gray" />
            <workflow :owner="selected.owner" :name="selected.name" v-on:runSubmitted="runSubmitted"></workflow>
        </div>
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
                    Before a repository can be connected, you must have a file
                    named <code>plantit.yaml</code> in your project root.
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
                v-else-if="workflowSearchResult === null && workflowName !== ''"
            >
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    Repository <b>{{ workflowName }}</b> not found.
                </p>
            </div>
            <div class="text-left" v-else-if="workflowSearchResult !== null">
                <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    Repository
                </h5>
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    <b-link
                        target="_blank"
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
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
                    Stars: {{ workflowSearchResult.repo.stargazers_count }}
                </p>
                <hr class="mt-2 mb-2" style="border-color: gray" />
                <div v-if="workflowSearchResult.validation.is_valid">
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Configuration
                    </h5>
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <b-row>
                            <b-col>
                                <small>Image</small>
                            </b-col>
                            <b-col cols="10">
                                <b>{{ workflowSearchResult.config.image }}</b>
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
                                            workflowSearchResult.config.commands
                                    }}</code></b
                                >
                            </b-col>
                        </b-row>
                        <b-row
                            v-if="
                                workflowSearchResult.config.input !== undefined
                            "
                        >
                            <b-col>
                                <small>Input</small>
                            </b-col>
                            <b-col cols="10">
                                <b
                                    ><code
                                        >[working directory]/input/{{
                                            workflowSearchResult.config.input
                                                .filetypes
                                                ? '[' +
                                                  (workflowSearchResult.config
                                                      .input.filetypes
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
                                workflowSearchResult.config.output !== undefined
                            "
                        >
                            <b-col>
                                <small>Output</small>
                            </b-col>
                            <b-col cols="10">
                                <b
                                    ><code
                                        >[working directory]/{{
                                            workflowSearchResult.config.output
                                                .path
                                                ? workflowSearchResult.config
                                                      .output.path + '/'
                                                : ''
                                        }}{{
                                            workflowSearchResult.config.output
                                                .include
                                                ? '[' +
                                                  (workflowSearchResult.config
                                                      .output.exclude
                                                      ? '+ '
                                                      : '') +
                                                  (workflowSearchResult.config
                                                      .output.include.patterns
                                                      ? '*.' +
                                                        workflowSearchResult.config.output.include.patterns.join(
                                                            ', *.'
                                                        )
                                                      : []) +
                                                  (workflowSearchResult.config
                                                      .output.include.names
                                                      ? ', ' +
                                                        workflowSearchResult.config.output.include.names.join(
                                                            ', '
                                                        )
                                                      : [])
                                                : ''
                                        }}{{
                                            workflowSearchResult.config.output
                                                .exclude
                                                ? ' - ' +
                                                  (workflowSearchResult.config
                                                      .output.exclude.patterns
                                                      ? '*.' +
                                                        workflowSearchResult.config.output.exclude.patterns.join(
                                                            ', *.'
                                                        )
                                                      : []) +
                                                  (workflowSearchResult.config
                                                      .output.exclude.names
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
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >{{ error }}</b-list-group-item
                        >
                    </b-list-group>
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        You must correct any configuration errors in your
                        <code>plantit.yaml</code> file before connecting your
                        repository.
                    </p>
                </div>
            </div>
            <div></div>
        </b-modal>
    </b-container>
</template>

<script>
import blurb from '@/components/workflows/workflow-blurb.vue';
import workflow from '@/components/workflows/workflow.vue';
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from "moment";

export default {
    name: 'workflows',
    components: {
        blurb,
        workflow
    },
    props: {
        workflows: {
            required: true,
            type: Array
        }
    },
    data: function() {
        return {
            login: false,
            selected: null,
            workflowName: '',
            workflowSearchResult: null,
            workflowExists: false
        };
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        back() {
            this.selected = null;
        },
        selectWorkflow: function(wf) {
            this.selected = {
                owner: wf['repo']['owner']['login'],
                name: wf['repo']['name']
            };
            // router.push({
            //     name: 'workflow',
            //     params: {
            //         username: workflow['repo']['owner']['login'],
            //         name: workflow['repo']['name']
            //     }
            // });
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
            this.$store.dispatch(
                'workflows/loadPersonal',
                this.profile.githubProfile.login
            );
        }
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['personal', 'personalLoading']),
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
