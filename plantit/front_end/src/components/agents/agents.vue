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
                            {{ publicContext ? 'Public' : 'Your' }} Agents
                        </h2></b-col
                    >
                    <b-col
                        md="auto"
                        class="ml-0"
                        align-self="center"
                        v-if="!publicContext"
                        ><b-button
                            :disabled="agentsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            title="Connect a new agent"
                            @click="showConnectAgentModal"
                            class="ml-0 mt-0 mr-0"
                        >
                            <b-spinner
                                small
                                v-if="agentsLoading"
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
                            :disabled="agentsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            title="Refresh agents"
                            @click="refreshAgents"
                            class="ml-0 mt-0 mr-0"
                        >
                            <b-spinner
                                small
                                v-if="agentsLoading"
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
                            :disabled="agentsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            class="ml-0 mt-0 mr-0"
                            @click="toggleContext"
                            :title="
                                publicContext
                                    ? 'View your agents'
                                    : 'View public agents'
                            "
                            v-b-tooltip:hover
                            ><span v-if="publicContext"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else
                                ><i class="fas fa-users"></i> Public</span
                            ></b-button
                        ></b-col
                    >
                </b-row>
                <b-row v-if="agentsLoading" class="mt-2">
                    <b-col class="text-center">
                        <b-spinner
                            type="grow"
                            label="Loading..."
                            variant="secondary"
                        ></b-spinner>
                    </b-col>
                </b-row>
                <b-card-group deck columns v-else-if="getAgents.length !== 0">
                    <b-card
                        v-for="agent in getAgents"
                        v-bind:key="agent.guid"
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
                        <b-row style="z-index: 10">
                            <b-col cols="10">
                                <h2>
                                    <b-link
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        variant="outline-dark"
                                        v-b-tooltip.hover
                                        :to="{
                                            name: 'agent',
                                            params: {
                                                guid: agent.guid
                                            }
                                        }"
                                    >
                                        {{ agent.name }}
                                    </b-link>
                                </h2>
                                <b-badge
                                    v-if="!agent.public"
                                    class="mr-1"
                                    variant="info"
                                    ><i class="fas fa-lock fa-fw"></i>
                                    Private</b-badge
                                >
                                <b-badge v-else variant="success" class="mr-1"
                                    ><i class="fas fa-lock-open fa-fw"></i>
                                    Public</b-badge
                                >
                                <b-badge variant="warning">{{
                                    agent.role === 'admin' ? 'Admin' : 'Guest'
                                }}</b-badge>

                                <br />
                                <small>
                                    {{ agent.description }}
                                </small>
                                <br />
                            </b-col>
                            <b-col cols="1"></b-col>
                        </b-row>
                        <b-img
                            v-if="agent.logo"
                            rounded
                            class="card-img-right overflow-hidden"
                            style="max-height: 4rem;position: absolute;right: 20px;top: 20px;z-index:1"
                            right
                            :src="agent.logo"
                        ></b-img>
                        <i
                            v-else
                            style="max-width: 7rem;position: absolute;right: 20px;top: 20px;"
                            right
                            class="card-img-left fas fa-server fa-2x fa-fw"
                        ></i>
                    </b-card>
                </b-card-group>
                <b-row v-else
                    ><b-col
                        ><span class="text-danger">{{
                            publicContext
                                ? 'No public agents available.'
                                : "You haven't connected any agents yet."
                        }}</span>
                        <br />
                        <span v-if="!publicContext">
                            View
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                @click="toggleContext"
                                ><i class="fas fa-users fa-1x fa-fw"></i>
                                Public</b-link
                            >
                            agents to request guest access to a public server,
                            cluster, or supercomputer, or
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                @click="showConnectAgentModal"
                                ><i class="fas fa-plug fa-1x fa-fw"></i> connect
                                an agent</b-link
                            >
                            of your own.</span
                        ></b-col
                    ></b-row
                >
            </div>
            <router-view
                v-else
                :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
            ></router-view>
        </div>
        <b-modal
            id="connectAgent"
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
            title="Connect a new agent"
            @ok="showAuthenticateModal"
            :ok-disabled="agentInvalid"
            ok-title="Connect"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                Your agent must be reachable by password-authenticated SSH on
                port 22. You will be prompted for your username and password
                after this form is submitted. If you elect to make this agent
                public, other users will receive an authentication prompt prior
                to submitting workflows.
            </p>
            <b-form-group label="Name" description="A name for this agent.">
                <b-form-input
                    :state="agentName !== ''"
                    v-model="agentName"
                    type="text"
                    placeholder="Enter a name"
                    required
                ></b-form-input>
            </b-form-group>
            <b-form-group
                label="Host"
                description="This agent's FQDN or IP address."
            >
                <b-form-input
                    :state="agentHost !== ''"
                    v-model="agentHost"
                    type="text"
                    placeholder="Enter a host or IP address"
                    required
                ></b-form-input>
            </b-form-group>
            <b-form-group
                label="Description"
                description="A plain-text description of this agent."
            >
                <b-form-textarea
                    :state="agentDescription !== ''"
                    v-model="agentDescription"
                    placeholder="Enter a description"
                    required
                ></b-form-textarea>
            </b-form-group>
            <b-form-group
                label="Working directory"
                description="Working directory within which to run user workflows."
            >
                <b-form-input
                    :state="agentWorkdir !== ''"
                    v-model="agentWorkdir"
                    type="text"
                    placeholder="Enter a directory path"
                    required
                ></b-form-input>
            </b-form-group>
            <b-form-group
                label="Pre-commands"
                description="Commands to run before user commands (e.g., loading modules, setting environment variables). Frequently useful but not required."
            >
                <b-form-textarea
                    v-model="agentPrecommands"
                    type="text"
                    rows="3"
                    placeholder="Enter commands"
                    required
                ></b-form-textarea>
            </b-form-group>
            <b-form-group
                label="Maximum runtime (minutes)"
                description="Maximum runtime (in minutes) permitted before the workflow is aborted."
                ><b-form-spinbutton
                    v-model="agentMaxTime"
                    value="10"
                    min="1"
                    max="1440"
                ></b-form-spinbutton
            ></b-form-group>
            <b-form-group
                label="Executor"
                description="Select an executor to orchestrate workflows."
            >
                <b-form-select
                    v-model="agentExecutor"
                    :options="agentExecutorOptions"
                    type="text"
                    placeholder="Select an executor"
                    required
                ></b-form-select
            ></b-form-group>
            <b-form-group
                v-if="isSLURM(agentExecutor)"
                description="Should this SLURM agent use job arrays for parallelization instead of Dask?"
                ><b-form-checkbox
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    v-model="agentJobArray"
                >
                    Enable job arrays
                </b-form-checkbox>
            </b-form-group>
            <b-form-group
                v-if="isSLURM(agentExecutor)"
                description="Should this SLURM agent use the TACC launcher instead of Dask?"
            >
                <b-form-checkbox
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    v-model="agentLauncher"
                >
                    Enable TACC launcher parameter sweep utility (for
                    Dask-incompatible hosts)
                </b-form-checkbox>
            </b-form-group>
            <b-form-group
                v-if="isJobQueue(agentExecutor)"
                label="Queue"
                description="Enter a scheduler queue name to use."
            >
                <b-form-input
                    v-model="agentQueue"
                    :state="agentQueue !== ''"
                    type="text"
                    placeholder="Enter a scheduler queue name"
                    required
                ></b-form-input
            ></b-form-group>
            <b-form-group
                v-if="isJobQueue(agentExecutor)"
                label="Project ID"
                description="Enter a scheduler project ID or allocation number to use."
            >
                <b-form-input
                    v-model="agentProject"
                    :state="agentProject !== ''"
                    type="text"
                    placeholder="Enter a scheduler project name"
                    required
                ></b-form-input
            ></b-form-group>
            <b-form-group
                v-if="isJobQueue(agentExecutor)"
                label="Maximum walltime (minutes)"
                description="Maximum walltime (in minutes) workflows can request from the agent scheduler."
                ><b-form-spinbutton
                    v-model="agentMaxWalltime"
                    value="10"
                    min="1"
                    max="1440"
                ></b-form-spinbutton
            ></b-form-group>
            <b-form-group
                v-if="isJobQueue(agentExecutor)"
                label="Maximum processes"
                description="Maximum number of processes workflows can request from the agent scheduler."
                ><b-form-spinbutton
                    v-model="agentMaxProcesses"
                    value="1"
                    min="1"
                    max="100"
                ></b-form-spinbutton
            ></b-form-group>
            <b-form-group
                v-if="isJobQueue(agentExecutor)"
                label="Maximum cores"
                description="Maximum number of cores workflows can request from the agent scheduler."
                ><b-form-spinbutton
                    v-model="agentMaxCores"
                    value="1"
                    min="1"
                    max="1000"
                ></b-form-spinbutton
            ></b-form-group>
            <b-form-group
                v-if="isJobQueue(agentExecutor)"
                label="Maximum nodes"
                description="Maximum number of nodes workflows can request from the agent scheduler."
                ><b-form-spinbutton
                    v-model="agentMaxNodes"
                    value="1"
                    min="1"
                    max="1000"
                ></b-form-spinbutton
            ></b-form-group>
            <b-form-group
                v-if="isJobQueue(agentExecutor)"
                label="Maximum memory"
                description="Maximum memory (in GB) workflows can request from the agent scheduler."
                ><b-form-spinbutton
                    v-model="agentMaxMem"
                    value="1"
                    min="1"
                    max="1000"
                ></b-form-spinbutton
            ></b-form-group>
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
            :title="'Authenticate with ' + this.agentName"
            @ok="connectAgent"
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
    </b-container>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'agents',
    data: function() {
        return {
            agentName: '',
            agentHost: '',
            agentDescription: '',
            agentWorkdir: '',
            agentPrecommands: '',
            agentMaxTime: 0,
            agentExecutor: 'Local',
            agentExecutorOptions: [
                { value: 'Local', text: 'Local' },
                { value: 'SLURM', text: 'SLURM' },
                { value: 'PBS', text: 'PBS' }
            ],
            agentQueue: '',
            agentProject: '',
            agentMaxWalltime: 0,
            agentMaxMem: 0,
            agentMaxCores: 0,
            agentMaxProcesses: 0,
            agentMaxNodes: 0,
            agentHeaderSkip: '',
            agentLauncher: false,
            agentJobArray: false,
            agentPublic: false,
            agentLogo: '',
            authenticationUsername: '',
            authenticationPassword: '',
            publicContext: false,
            togglingContext: false,
            isOpen: false,
            isLoading: false,
            isAsync: false
        };
    },
    async mounted() {
        await Promise.all([
            this.$store.dispatch(
                'agents/loadPersonal',
                this.profile.djangoProfile.username
            ),
            this.$store.dispatch('agents/loadPublic')
        ]);
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('agents', [
            'personalAgents',
            'personalAgentsLoading',
            'publicAgents',
            'publicAgentsLoading'
        ]),
        isRootPath() {
            return this.$route.name === 'agents';
        },
        getAgents() {
            return this.publicContext ? this.publicAgents : this.personalAgents;
        },
        agentsLoading() {
            return this.publicContext
                ? this.publicAgentsLoading
                : this.personalAgentsLoading;
        },
        agentInvalid() {
            return (
                this.agentName === '' ||
                this.agentDescription === '' ||
                this.agentHost === '' ||
                this.agentWorkdir === '' ||
                this.agentPrecommands === '' ||
                this.agentExecutor === '' ||
                (this.agentExecutor !== 'Local' &&
                    (this.agentQueue === '' ||
                        // this.agentProject === '' ||   not all SLURM configurations require this
                        this.agentMaxWalltime <= 0 ||
                        this.agentMaxProcesses <= 0 ||
                        this.agentMaxCores <= 0 ||
                        this.agentMaxNodes <= 0 ||
                        this.agentMaxMem <= 0))
            );
        }
    },
    watch: {
        // TODO get rid of this, it's hacky
        // eslint-disable-next-line no-unused-vars
        publicContext: function(_) {
            this.refreshAgents();
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
        resetAgentInfo() {
            this.agentName = '';
            this.agentDescription = '';
            this.agentWorkdir = '';
            this.agentHost = '';
            this.agentPrecommands = '';
            this.agentMaxTime = 0;
            this.agentPublic = false;
            this.agentLogo = '';
            this.executor = 'Local';
            this.agentProject = '';
            this.agentQueue = '';
            this.agentMaxCores = 0;
            this.agentMaxProcesses = 0;
            this.agentMaxNodes = 0;
            this.agentMaxMem = 0;
            this.agentMaxWalltime = 0;
            this.agentJobArray = false;
            this.agentLauncher = false;
        },
        refreshAgents() {
            if (this.publicContext) this.$store.dispatch('agents/loadPublic');
            else
                this.$store.dispatch(
                    'agents/loadPersonal',
                    this.profile.djangoProfile.username
                );
        },
        showAuthenticateModal() {
            this.$bvModal.show('authenticate');
        },
        showConnectAgentModal() {
            this.$bvModal.show('connectAgent');
        },
        async connectAgent() {
            let data = {
                auth: {
                    username: this.authenticationUsername,
                    password: this.authenticationPassword
                },
                config: {
                    name: this.agentName,
                    description: this.agentDescription,
                    workdir: this.agentWorkdir,
                    username: this.profile.djangoProfile.username,
                    hostname: this.agentHost,
                    pre_commands: this.agentPrecommands,
                    max_time: this.agentMaxTime,
                    public: this.agentPublic,
                    logo: this.agentLogo,
                    executor: this.agentExecutor
                }
            };

            await axios({
                method: 'post',
                url: `/apis/v1/agents/connect/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    alert(response.data.created);
                    this.$store.dispatch(
                        'agents/addOrUpdate',
                        response.data.agent
                    );
                    this.resetAgentInfo();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    // TODO probably an auth error: display info and allow user to edit info and retry connection
                    throw error;
                });
        },
        isJobQueue(executor) {
            return executor !== 'Local';
        },
        isSLURM(executor) {
            return executor === 'SLURM';
        }
    }
};
</script>

<style scoped></style>
