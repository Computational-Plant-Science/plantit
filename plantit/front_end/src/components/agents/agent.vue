<template>
    <div>
        <b-container class="vl" fluid>
            <b-row
                no-gutters
                v-if="
                    getAgent.role !== 'admin' &&
                        getAgent.role !== 'run' &&
                        !getAgent.public
                "
                ><b-col class="text-center"
                    ><p
                        :class="
                            profile.darkMode
                                ? 'text-center text-white'
                                : 'text-center text-dark'
                        "
                    >
                        <i class="fas fa-exclamation-circle fa-3x fa-fw"></i>
                        <br />
                        <br />
                        You do not have access to this agent.
                        <br />
                        <b-button
                            v-if="!accessRequested"
                            class="ml-0"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            :title="'Request guest access for ' + getAgent.name"
                            @click="requestAccess"
                        >
                            <i class="fas fa-key fa-fw"></i>
                            Request Guest Access
                        </b-button>
                        <b-button
                            v-else
                            class="ml-0"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="sm"
                            v-b-tooltip.hover
                            :disabled="true"
                        >
                            <i class="fas fa-key fa-fw"></i>
                            You requested guest access
                            {{ prettify(accessRequest.created) }}. Your request
                            is pending.
                        </b-button>
                    </p></b-col
                ></b-row
            >
            <div v-else>
                <b-row no-gutters class="mt-3">
                    <b-col v-if="alertEnabled">
                        <b-alert
                            :show="alertEnabled"
                            :variant="
                                alertMessage.startsWith('Failed')
                                    ? 'danger'
                                    : 'success'
                            "
                            dismissible
                            @dismissed="alertEnabled = false"
                        >
                            {{ alertMessage }}
                        </b-alert>
                    </b-col>
                </b-row>
                <b-row
                    align-h="center"
                    align-v="center"
                    align-content="center"
                    v-if="agentLoading"
                    class="text-center"
                >
                    <b-col
                        ><b-spinner
                            type="grow"
                            label="Loading..."
                            variant="success"
                        ></b-spinner
                    ></b-col>
                </b-row>
                <b-row v-else>
                    <b-col
                        ><b-card
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            :header-bg-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            border-variant="default"
                            :header-border-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            :text-variant="profile.darkMode ? 'white' : 'dark'"
                            class="overflow-hidden"
                        >
                            <div
                                :class="
                                    profile.darkMode
                                        ? 'theme-dark'
                                        : 'theme-light'
                                "
                            >
                                <b-img
                                    v-if="getAgent.logo"
                                    rounded
                                    class="card-img-right overflow-hidden"
                                    style="max-height: 5rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                    right
                                    :src="getAgent.logo"
                                ></b-img>
                                <b-row no-gutters>
                                    <b-col>
                                        <b-row>
                                            <b-col>
                                                <h2
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    <i class="fas fa-robot fa-fw"></i> {{ getAgent.name }}
                                                </h2>
                                                <b-badge
                                                    v-if="getAgent.role === 'guest'"
                                                    variant="warning"
                                                    >Guest</b-badge
                                                >
                                                <b-badge
                                                    v-else-if="
                                                        getAgent.role === 'admin'
                                                    "
                                                    variant="success"
                                                    >Owner</b-badge
                                                >
                                                <br />
                                                <small>{{
                                                    getAgent.description
                                                }}</small>
                                            </b-col>
                                        </b-row>
                                        <hr />
                                        <b-row
                                            ><b-col>
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Scheduler Configuration
                                                </h5>
                                                <b-row>
                                                    <b-col>
                                                        <small>executor</small>
                                                    </b-col>
                                                    <b-col cols="9">
                                                        <b class="ml-3">
                                                            {{ getAgent.executor }}
                                                        </b>
                                                    </b-col>
                                                </b-row>
                                                <b-row>
                                                    <b-col>
                                                        <small
                                                            >working
                                                            directory</small
                                                        >
                                                    </b-col>
                                                    <b-col cols="9">
                                                        <b class="ml-3">
                                                            {{ getAgent.workdir }}
                                                        </b>
                                                    </b-col>
                                                </b-row>
                                                <b-row>
                                                    <b-col>
                                                        <small
                                                            >pre-commands</small
                                                        >
                                                    </b-col>
                                                    <b-col cols="9"
                                                        ><b class="ml-3"
                                                            ><code>{{
                                                                getAgent.pre_commands
                                                            }}</code></b
                                                        ></b-col
                                                    >
                                                </b-row>
                                            </b-col>
                                            <b-col>
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Resources Available
                                                    <small>per container</small>
                                                </h5>
                                                <b>{{ getAgent.max_cores }}</b>
                                                <small> cores</small>
                                                <br />
                                                <b>{{ getAgent.max_processes }}</b>
                                                <small> processes</small>
                                                <br />
                                                <span
                                                    v-if="
                                                        parseInt(
                                                            getAgent.max_mem
                                                        ) < 0
                                                    "
                                                >
                                                    <small
                                                        >Virtual memory</small
                                                    ></span
                                                >
                                                <span
                                                    v-else-if="
                                                        parseInt(
                                                            getAgent.max_mem
                                                        ) > 0
                                                    "
                                                    >{{ getAgent.max_mem
                                                    }}<small>
                                                        GB memory</small
                                                    ></span
                                                >
                                                <span
                                                    v-else-if="
                                                        parseInt(
                                                            getAgent.max_mem
                                                        ) === -1
                                                    "
                                                    ><small
                                                        >virtual memory</small
                                                    ></span
                                                >
                                                <br />
                                                <span v-if="getAgent.gpu">
                                                    <i
                                                        :class="
                                                            getAgent.gpu
                                                                ? 'text-warning'
                                                                : ''
                                                        "
                                                        class="far fa-check-circle"
                                                    ></i>
                                                    <small>GPU</small>
                                                </span>
                                                <span v-else
                                                    ><small>
                                                        No GPU
                                                    </small></span
                                                >
                                            </b-col>
                                        </b-row>
                                        <hr />
                                        <b-row>
                                            <b-col
                                                v-if="getAgent.role === 'admin'"
                                                class="mr-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-form-checkbox
                                                    v-model="getAgent.public"
                                                    button
                                                    class="mr-0"
                                                    size="sm"
                                                    button-variant="warning"
                                                    @change="togglePublic"
                                                >
                                                    <i
                                                        v-if="getAgent.public"
                                                        class="fas fa-lock-open fa-fw"
                                                    ></i>
                                                    <i
                                                        v-else
                                                        class="fas fa-lock fa-fw"
                                                    ></i>
                                                    {{
                                                        getAgent.public
                                                            ? 'Public'
                                                            : 'Private'
                                                    }}
                                                </b-form-checkbox>
                                            </b-col>
                                            <b-col
                                                v-else-if="
                                                    getAgent.role === 'none' &&
                                                        !accessRequested
                                                "
                                                class="ml-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    :title="
                                                        'Request access to ' +
                                                            getAgent.name
                                                    "
                                                    @click="requestAccess"
                                                >
                                                    <i
                                                        class="fas fa-key fa-fw"
                                                    ></i>
                                                    Request Guest Access
                                                </b-button></b-col
                                            >
                                            <b-col></b-col>
                                            <b-col
                                                v-if="getAgent.role !== 'none'"
                                                class="ml-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    title="Check Connection Status"
                                                    :disabled="
                                                        getAgent.role === 'none' ||
                                                            statusChecking
                                                    "
                                                    @click="checkStatus"
                                                >
                                                    <i
                                                        class="fas fa-network-wired fa-fw"
                                                    ></i>
                                                    Check Status<b-spinner
                                                        small
                                                        v-if="statusChecking"
                                                        label="Loading..."
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'light'
                                                                : 'dark'
                                                        "
                                                        class="ml-2 mb-1"
                                                    ></b-spinner> </b-button
                                            ></b-col>
                                            <b-col
                                                v-if="
                                                    getAgent.role === 'none' &&
                                                        accessRequested
                                                "
                                                class="ml-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    :disabled="true"
                                                >
                                                    <i
                                                        class="fas fa-key fa-fw"
                                                    ></i>
                                                    You requested access
                                                    {{
                                                        prettify(
                                                            accessRequest.created
                                                        )
                                                    }}. Your request is pending.
                                                </b-button></b-col
                                            >
                                            <!--<b-col></b-col>
                                            <b-col md="auto"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    :disabled="
                                                        (session !== null &&
                                                            session !==
                                                                undefined) ||
                                                            sessionLoading
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    title="Start interactive datasets"
                                                    @click="
                                                        tryOpenDataset
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-tasks fa-fw"
                                                    ></i>
                                                    Start Session
                                                </b-button></b-col
                                            >-->
                                        </b-row>
                                    </b-col>
                                </b-row>
                            </div>
                        </b-card>
                        <br />
                        <div v-if="getAgent.policies && getAgent.role === 'admin'">
                            <b-row no-gutters>
                                <b-col align-self="end"
                                    ><h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        Users
                                    </h5></b-col
                                >
                            </b-row>
                            <b-row
                                ><b-col align-self="end">
                                    <b-row
                                        v-if="
                                            !agentLoading &&
                                                getAgent.policies.length < 2
                                        "
                                        ><b-col
                                            ><small
                                                >You are the only user with
                                                access.</small
                                            ></b-col
                                        ></b-row
                                    >
                                    <b-row
                                        v-else
                                        v-for="policy in getAgent.policies.filter(
                                            p =>
                                                p.user !==
                                                profile.djangoProfile.username
                                        )"
                                        v-bind:key="policy.user"
                                    >
                                        <b-col
                                            >{{ policy.user
                                            }}<small>
                                                can
                                                {{ policy.role.toLowerCase() }}
                                                this agent.</small
                                            ></b-col
                                        ><b-col
                                            class="ml-0"
                                            md="auto"
                                            align-self="end"
                                            ><b-button
                                                class="ml-0"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                :title="
                                                    'Revoke access from ' +
                                                        policy.user
                                                "
                                                @click="
                                                    revokeAccess(policy.user)
                                                "
                                            >
                                                <i
                                                    class="fas fa-lock fa-fw"
                                                ></i>
                                                Revoke Access
                                            </b-button></b-col
                                        >
                                    </b-row>
                                </b-col></b-row
                            >
                            <hr />
                        </div>
                        <div v-if="getAgent.role === 'admin'">
                            <b-row no-gutters>
                                <b-col align-self="end"
                                    ><h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        Access Requests
                                    </h5></b-col
                                >
                            </b-row>
                            <b-row v-if="getAgent.access_requests.length === 0"
                                ><b-col
                                    ><small
                                        >No pending access requests.</small
                                    ></b-col
                                ></b-row
                            >
                            <b-row v-else
                                ><b-col align-self="end">
                                    <b-row
                                        v-for="request in getAgent.access_requests"
                                        v-bind:key="request.user"
                                    >
                                        <b-col md="auto">{{
                                            request.user
                                        }}</b-col
                                        ><b-col align-self="middle"
                                            ><small
                                                >Requested
                                                {{
                                                    prettify(request.created)
                                                }}</small
                                            ></b-col
                                        ><b-col
                                            class="ml-0"
                                            md="auto"
                                            align-self="end"
                                            ><b-button
                                                class="ml-0"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                :title="
                                                    'Grant access to ' +
                                                        request.user
                                                "
                                                @click="
                                                    grantAccess(request.user)
                                                "
                                            >
                                                <i
                                                    class="fas fa-unlock fa-fw"
                                                ></i>
                                                Grant Access
                                            </b-button></b-col
                                        ></b-row
                                    >
                                </b-col></b-row
                            >
                        </div>
                    </b-col>
                    <b-col md="auto">
                        <b-row
                            ><b-col align-self="end"
                                ><h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Periodic Tasks
                                </h5></b-col
                            ><b-col class="mb-1" align-self="start" md="auto"
                                ><b-button
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    title="Create Periodic Task"
                                    :disabled="getAgent.role !== 'admin'"
                                    v-b-modal.createTask
                                >
                                    <i class="fas fa-plus fa-fw"></i>
                                    Create
                                </b-button></b-col
                            ></b-row
                        >
                        <div
                            v-for="task in getAgent.tasks"
                            v-bind:key="task.name"
                            class="pb-2"
                        >
                            <b-row class="pt-1">
                                <b-col
                                    md="auto"
                                    v-if="getAgent.role === 'admin'"
                                    align-self="end"
                                    :class="
                                        profile.darkMode
                                            ? 'text-white mb-1'
                                            : 'text-dark mb-1'
                                    "
                                >
                                    <b-form-checkbox
                                        v-model="task.enabled"
                                        @change="toggleTask(task)"
                                        switch
                                        size="md"
                                    >
                                    </b-form-checkbox
                                ></b-col>
                                <b-col align-self="end" class="mb-1">{{
                                    task.name
                                }}</b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="getAgent.role === 'admin'"
                                    ><b-button
                                        size="sm"
                                        variant="outline-danger"
                                        @click="deleteTask(task)"
                                        ><i class="fas fa-trash fa-fw"></i>
                                        Remove</b-button
                                    ></b-col
                                ></b-row
                            >
                            <b-row
                                ><b-col md="auto" align-self="end" class="mb-1"
                                    ><small v-if="task.enabled"
                                        >Next running {{ cronTime(task)
                                        }}<br /></small
                                    ><small v-if="task.last_run !== null"
                                        >Last ran
                                        {{ prettify(task.last_run) }}</small
                                    ><small v-else
                                        >Task has not run yet</small
                                    ></b-col
                                >
                            </b-row>
                        </div>
                    </b-col>
                </b-row>
            </div>
        </b-container>
        <b-modal
            centered
            id="createTask"
            title="Create Periodic Task"
            @ok="createTask"
            size="xl"
        >
            <b-form @submit="createTask" @reset="resetCreateTaskForm">
                <b-form-group id="input-group-1" label-for="input-1">
                    <b-input-group size="md" prepend="Name">
                        <b-form-input
                            id="input-1"
                            v-model="createTaskForm.name"
                            required
                        ></b-form-input>
                        <b-form-invalid-feedback
                            :state="this.createTaskForm.name !== ''"
                        >
                            Give this task a name.
                        </b-form-invalid-feedback>
                    </b-input-group>
                </b-form-group>
                <b-form-group id="input-group-3" label-for="input-3">
                    <b-input-group size="md" prepend="Command">
                        <b-form-input
                            id="input-3"
                            v-model="createTaskForm.command"
                            required
                        ></b-form-input>
                        <b-form-invalid-feedback
                            :state="this.createTaskForm.command !== ''"
                        >
                            Enter a command for this task to run.
                        </b-form-invalid-feedback>
                    </b-input-group>
                </b-form-group>
                <b-form-group
                    id="input-group-4"
                    label-for="input-4"
                    description="Configure when this task should run."
                >
                    <VueCronEditorBuefy
                        v-model="createTaskForm.time"
                    ></VueCronEditorBuefy>
                </b-form-group>
            </b-form>
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
            :title="'Authenticate with ' + this.getAgent.name"
            @ok="openDataset"
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
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
import moment from 'moment';
import VueCronEditorBuefy from 'vue-cron-editor-buefy';
import parser from 'cron-parser';

export default {
    name: 'agent',
    components: {
        VueCronEditorBuefy
    },
    data: function() {
        return {
            authenticationUsername: '',
            authenticationPassword: '',
            statusChecking: false,
            alertEnabled: false,
            alertMessage: '',
            createTaskForm: {
                name: '',
                description: '',
                command: '',
                once: '',
                time: ''
            },
            sessionSocket: null
        };
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['recentlyRunWorkflows']),
        ...mapGetters('agents', ['agent', 'personalAgentsLoading', 'publicAgentsLoading']),
        getAgent() {
            return this.agent(this.$router.currentRoute.params.name);
        },
        mustAuthenticate() {
            return (
                this.getAgent.policies.length === 0 ||
                (this.getAgent.policies.length > 0 &&
                    !this.getAgent.policies.some(
                        p =>
                            p.user === this.profile.djangoProfile.username &&
                            (p.role.toLowerCase() === 'guest' ||
                                p.role.toLowerCase() === 'admin')
                    ))
            );
        },
        accessRequested: function() {
            return this.getAgent.access_requests.some(
                r => r.user === this.profile.djangoProfile.username
            );
        },
        accessRequest: function() {
            return this.getAgent.access_requests.find(
                r => r.user === this.profile.djangoProfile.username
            );
        }
    },
    methods: {
        tryOpenDataset() {
            if (this.mustAuthenticate) this.showAuthenticateModal();
            else this.openDataset();
        },
        showAuthenticateModal() {
            this.$bvModal.show('authenticate');
        },
        // openDataset() {
        //     this.$store.dispatch('updateSessionLoading', true);
        //     let data = { getAgent: this.getAgent.name };
        //     if (this.mustAuthenticate)
        //         data['auth'] = {
        //             username: this.authenticationUsername,
        //             password: this.authenticationPassword
        //         };

        //     axios({
        //         method: 'post',
        //         url: `/apis/v1/datasets/open/`,
        //         data: data,
        //         headers: { 'Content-Type': 'application/json' }
        //     })
        //         .then(async response => {
        //             await this.$store.dispatch(
        //                 'updateDatasetSession',
        //                 response.data.session
        //             );
        //         })
        //         .catch(error => {
        //             Sentry.captureException(error);
        //             throw error;
        //         });
        // },
        revokeAccess(user) {
            axios
                .get(
                    `/apis/v1/agents/revoke_access/?name=${this.$route.params.name}&user=${user}`
                )
                .then(() => {
                    this.loadTarget();
                    this.alertMessage = `Revoked user ${user}'s access to ${this.$route.params.name}`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.alertMessage = `Failed to revoke user ${user}'s access to ${this.$route.params.name}`;
                        this.alertEnabled = true;
                        throw error;
                    }
                });
        },
        grantAccess(user) {
            axios
                .get(
                    `/apis/v1/agents/grant_access/?name=${this.$route.params.name}&user=${user}`
                )
                .then(response => {
                    this.loadTarget();
                    if (response.data.granted)
                        this.alertMessage = `Granted user ${user} access to ${this.$route.params.name}`;
                    else
                        this.alertMessage = `User ${user} already has access to ${this.$route.params.name}`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.alertMessage = `Failed to grant user ${user} access to ${this.$route.params.name}`;
                        this.alertEnabled = true;
                        throw error;
                    }
                });
        },
        requestAccess() {
            axios
                .get(
                    `/apis/v1/agents/request_access/?name=${this.$route.params.name}`
                )
                .then(response => {
                    this.loadTarget();
                    if (response.data.created)
                        this.alertMessage = `Requested access to${this.$route.params.name}`;
                    else
                        this.alertMessage = `You've already requested access to ${this.$route.params.name}`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.alertMessage = `Failed to request access to ${this.$route.params.name}`;
                        this.alertEnabled = true;
                        throw error;
                    }
                });
        },
        togglePublic() {
            axios
                .get(
                    `/apis/v1/agents/toggle_public/?name=${this.$route.params.name}`
                )
                .then(response => {
                    this.getAgent.public = response.data.public;
                    this.alertMessage = `${this.$route.params.name} is now ${
                        this.getAgent.public ? 'public' : 'private'
                    }`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.alertMessage = `Failed to toggle ${this.$route.params.name} visibility`;
                        this.alertEnabled = true;
                        throw error;
                    }
                });
        },
        cronTime(task) {
            if (
                task.crontab === null ||
                task.crontab === undefined ||
                task.crontab === 'None'
            )
                return '';
            return moment(
                parser
                    .parseExpression(task.crontab)
                    .next()
                    .toString()
            ).format('MMMM Do YYYY, h:mm a');
        },
        deleteTask(task) {
            return axios
                .get(`/apis/v1/agents/remove_task/?name=${task.name}`)
                .then(() => {
                    this.loadTarget();
                    this.alertMessage = `Deleted task ${task.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.statusChecking = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to delete ${task.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.statusChecking = false;
                    throw error;
                });
        },
        createTask(event) {
            event.preventDefault();
            axios({
                method: 'post',
                url: `/apis/v1/agents/create_task/`,
                data: {
                    name: this.createTaskForm.name,
                    agent: this.getAgent.name,
                    description: this.createTaskForm.description,
                    command: this.createTaskForm.command,
                    delay: this.createTaskForm.time
                    // delay: moment
                    //     .duration(
                    //         this.createTaskForm.timeIntervalValue,
                    //         this.createTaskForm.timeInterval
                    //     )
                    //     .asSeconds()
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    this.alertMessage =
                        response.status === 200 && response.data.created
                            ? `Created task ${this.createTaskForm.name} on ${this.getAgent.name}`
                            : response.status === 200 && !response.data.created
                            ? `Task ${this.createTaskForm.name} already exists on ${this.getAgent.name}`
                            : `Failed to create task ${this.createTaskForm.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.statusChecking = false;
                    this.$bvModal.hide('createTask');
                    this.loadTarget();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to create task ${this.createTaskForm.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.statusChecking = false;
                    this.$bvModal.hide('createTask');
                    throw error;
                });
        },
        resetCreateTaskForm() {
            this.form = {
                name: '',
                description: '',
                command: '',
                interval: moment.duration(1, 'days')
            };
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        prettifyDuration: function(dur) {
            moment.relativeTimeThreshold('m', 1);
            return moment.duration(dur, 'seconds').humanize(true);
        },
        checkStatus: function() {
            this.statusChecking = true;
            return axios
                .get(`/apis/v1/agents/status/?name=${this.$route.params.name}`)
                .then(response => {
                    this.alertMessage = response.data.healthy
                        ? `Connection to ${this.getAgent.name} succeeded`
                        : `Failed to connect to ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.statusChecking = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to connect to ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.statusChecking = false;
                    throw error;
                });
        },
        toggleTask: function(task) {
            axios
                .get(`/apis/v1/agents/toggle_task/?name=${task.name}`)
                .then(response => {
                    this.loadTarget();
                    this.alertMessage = `${
                        response.data.enabled ? 'Enabled' : 'Disabled'
                    } task ${task.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.alertMessage = `Failed to disable task ${task.name} on ${this.getAgent.name}`;
                        this.alertEnabled = true;
                        throw error;
                    }
                });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
