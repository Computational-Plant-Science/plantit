<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            profile.darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
            <b-row
                no-gutters
                v-if="
                    target.role !== 'own' &&
                        target.role !== 'run' &&
                        !target.public
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
                        You do not have access to this resource.
                        <br />
                        <b-button
                            v-if="!accessRequested"
                            class="ml-0"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            :title="'Request access to ' + target.name"
                            @click="requestAccess"
                        >
                            <i class="fas fa-key fa-fw"></i>
                            Request Access
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
                            You requested access
                            {{ prettify(accessRequest.created) }}. Your request
                            is pending.
                        </b-button>
                    </p></b-col
                ></b-row
            >
            <div v-else>
                <b-row no-gutters class="mt-3">
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
                    align-v="center"
                    align-content="center"
                    v-if="targetLoading"
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
                                    v-if="target.logo"
                                    rounded
                                    class="card-img-right overflow-hidden"
                                    style="max-height: 5rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                    right
                                    :src="target.logo"
                                ></b-img>
                                <i
                                    v-else
                                    style="max-width: 7rem;position: absolute;right: 20px;top: 20px;"
                                    right
                                    class="card-img-left fas fa-server fa-2x fa-fw"
                                ></i>
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
                                                    {{ target.name }}
                                                </h2>
                                                <small>{{
                                                    target.description
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
                                                            {{
                                                                target.executor
                                                            }}
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
                                                            {{ target.workdir }}
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
                                                                target.pre_commands
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
                                                <b>{{ target.max_cores }}</b>
                                                <small> cores</small>
                                                <br />
                                                <b>{{
                                                    target.max_processes
                                                }}</b>
                                                <small> processes</small>
                                                <br />
                                                <span
                                                    v-if="
                                                        parseInt(
                                                            target.max_mem
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
                                                            target.max_mem
                                                        ) > 0
                                                    "
                                                    class="text-danger"
                                                    >{{ target.max_mem
                                                    }}<small>
                                                        GB memory</small
                                                    ></span
                                                >
                                                <span
                                                    v-else-if="
                                                        parseInt(
                                                            target.max_mem
                                                        ) === -1
                                                    "
                                                    ><small
                                                        >virtual memory</small
                                                    ></span
                                                >
                                                <br />
                                                <span v-if="target.gpu">
                                                    <i
                                                        :class="
                                                            target.gpu
                                                                ? 'text-warning'
                                                                : ''
                                                        "
                                                        class="far fa-check-circle"
                                                    ></i>
                                                    <small>GPU</small>
                                                </span>
                                                <span v-else
                                                    ><i
                                                        class="far fa-times-circle"
                                                    ></i
                                                    ><small>
                                                        No GPU
                                                    </small></span
                                                >
                                            </b-col>
                                        </b-row>
                                        <hr />
                                        <b-row>
                                            <b-col
                                                v-if="target.role === 'own'"
                                                class="mr-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-form-checkbox
                                                    v-model="target.public"
                                                    button
                                                    class="mr-0"
                                                    size="sm"
                                                    button-variant="warning"
                                                    @change="togglePublic"
                                                >
                                                    <i
                                                        v-if="target.public"
                                                        class="fas fa-lock-open fa-fw"
                                                    ></i>
                                                    <i
                                                        v-else
                                                        class="fas fa-lock fa-fw"
                                                    ></i>
                                                    {{
                                                        target.public
                                                            ? 'Public'
                                                            : 'Private'
                                                    }}
                                                </b-form-checkbox>
                                            </b-col>
                                            <b-col
                                                v-else-if="
                                                    target.role === 'none' &&
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
                                                            target.name
                                                    "
                                                    @click="requestAccess"
                                                >
                                                    <i
                                                        class="fas fa-key fa-fw"
                                                    ></i>
                                                    Request Access
                                                </b-button></b-col
                                            >
                                            <b-col
                                                v-if="target.role !== 'none'"
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
                                                        target.role === 'none'
                                                    "
                                                    @click="checkStatus"
                                                >
                                                    <i
                                                        class="fas fa-network-wired fa-fw"
                                                    ></i>
                                                    Check Status
                                                </b-button></b-col
                                            >
                                            <b-col></b-col>
                                            <b-col
                                                v-if="!accessRequested"
                                                md="auto"
                                                align-self="center text-right"
                                                ><small
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                    >{{
                                                        `You ${
                                                            target.role ===
                                                            'own'
                                                                ? target.role
                                                                : target.role ===
                                                                  'none'
                                                                ? 'do not have access to'
                                                                : 'can ' +
                                                                  target.role
                                                        }`
                                                    }}
                                                    this server.</small
                                                ></b-col
                                            >
                                            <b-col
                                                v-if="
                                                    target.role === 'none' &&
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
                                        </b-row>
                                    </b-col>
                                </b-row>
                            </div>
                        </b-card>
                        <br />
                        <div v-if="target.policies && target.role === 'own'">
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
                                            !targetLoading &&
                                                target.policies.length === 1
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
                                        v-for="policy in target.policies.filter(
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
                                                this server.</small
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
                        <div v-if="target.role === 'own'">
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
                            <b-row v-if="target.access_requests.length === 0"
                                ><b-col
                                    ><small
                                        >No pending access requests.</small
                                    ></b-col
                                ></b-row
                            >
                            <b-row v-else
                                ><b-col align-self="end">
                                    <b-row
                                        v-for="request in target.access_requests"
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
                                    :disabled="target.role !== 'own'"
                                    v-b-modal.createTask
                                >
                                    <i class="fas fa-plus fa-fw"></i>
                                    Create
                                </b-button></b-col
                            ></b-row
                        >
                        <div
                            v-for="task in target.tasks"
                            v-bind:key="task.name"
                            class="pb-2"
                        >
                            <b-row class="pt-1">
                                <b-col
                                    md="auto"
                                    v-if="target.role === 'own'"
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
                                    v-if="task.name !== `Healthcheck`"
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
    name: 'server',
    components: {
        VueCronEditorBuefy
    },
    data: function() {
        return {
            target: null,
            targetLoading: false,
            checkingStatus: false,
            showStatusAlert: false,
            statusAlertMessage: '',
            singularityCacheCleaning: false,
            workdirCleaning: false,
            createTaskForm: {
                name: '',
                description: '',
                command: '',
                once: '',
                time: ''
            }
        };
    },
    mounted() {
        this.loadTarget();
    },
    computed: {
        ...mapGetters(['profile', 'workflowsRecentlyRun']),
        accessRequested: function() {
            return this.target.access_requests.some(
                r => r.user === this.profile.djangoProfile.username
            );
        },
        accessRequest: function() {
            return this.target.access_requests.find(
                r => r.user === this.profile.djangoProfile.username
            );
        }
    },
    methods: {
        revokeAccess(user) {
            axios
                .get(
                    `/apis/v1/servers/revoke_access/?name=${this.$route.params.name}&user=${user}`
                )
                .then(() => {
                    this.loadTarget();
                    this.statusAlertMessage = `Revoked user ${user}'s access to ${this.$route.params.name}`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.statusAlertMessage = `Failed to revoke user ${user}'s access to ${this.$route.params.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    }
                });
        },
        grantAccess(user) {
            axios
                .get(
                    `/apis/v1/servers/grant_access/?name=${this.$route.params.name}&user=${user}`
                )
                .then(response => {
                    this.loadTarget();
                    if (response.data.granted)
                        this.statusAlertMessage = `Granted user ${user} access to ${this.$route.params.name}`;
                    else
                        this.statusAlertMessage = `User ${user} already has access to ${this.$route.params.name}`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.statusAlertMessage = `Failed to grant user ${user} access to ${this.$route.params.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    }
                });
        },
        requestAccess() {
            axios
                .get(
                    `/apis/v1/servers/request_access/?name=${this.$route.params.name}`
                )
                .then(response => {
                    this.loadTarget();
                    if (response.data.created)
                        this.statusAlertMessage = `Requested access to server ${this.$route.params.name}`;
                    else
                        this.statusAlertMessage = `You've already requested access to server ${this.$route.params.name}`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.statusAlertMessage = `Failed to request access to server ${this.$route.params.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    }
                });
        },
        togglePublic() {
            axios
                .get(
                    `/apis/v1/servers/toggle_public/?name=${this.$route.params.name}`
                )
                .then(response => {
                    this.target.public = response.data.public;
                    this.statusAlertMessage = `Server ${
                        this.$route.params.name
                    } is now ${this.target.public ? 'public' : 'private'}`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.statusAlertMessage = `Failed to toggle server ${this.$route.params.name} visibility`;
                        this.showStatusAlert = true;
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
                .get(`/apis/v1/servers/remove_task/?name=${task.name}`)
                .then(() => {
                    this.loadTarget();
                    this.statusAlertMessage = `Deleted task ${task.name} on ${this.target.name}`;
                    this.showStatusAlert = true;
                    this.checkingStatus = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.statusAlertMessage = `Failed to delete ${task.name} on ${this.target.name}`;
                    this.showStatusAlert = true;
                    this.checkingStatus = false;
                    throw error;
                });
        },
        createTask(event) {
            event.preventDefault();
            axios({
                method: 'post',
                url: `/apis/v1/servers/create_task/`,
                data: {
                    name: this.createTaskForm.name,
                    target: this.target.name,
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
                    this.statusAlertMessage =
                        response.status === 200 && response.data.created
                            ? `Created task ${this.createTaskForm.name} on ${this.target.name}`
                            : response.status === 200 && !response.data.created
                            ? `Task ${this.createTaskForm.name} already exists on ${this.target.name}`
                            : `Failed to create task ${this.createTaskForm.name} on ${this.target.name}`;
                    this.showStatusAlert = true;
                    this.checkingStatus = false;
                    this.$bvModal.hide('createTask');
                    this.loadTarget();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.statusAlertMessage = `Failed to create task ${this.createTaskForm.name} on ${this.target.name}`;
                    this.showStatusAlert = true;
                    this.checkingStatus = false;
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
        loadTarget: function() {
            this.targetLoading = true;
            return axios
                .get(
                    `/apis/v1/servers/get_by_name/?name=${this.$route.params.name}`
                )
                .then(response => {
                    this.target = response.data;
                    this.singularityCacheCleaning =
                        response.data.singularity_cache_clean_enabled;
                    this.targetLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        checkStatus: function() {
            this.checkingStatus = true;
            return axios
                .get(`/apis/v1/servers/status/?name=${this.$route.params.name}`)
                .then(response => {
                    this.statusAlertMessage = response.data.healthy
                        ? `Connection to ${this.target.name} succeeded`
                        : `Failed to connect to ${this.target.name}`;
                    this.showStatusAlert = true;
                    this.checkingStatus = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.statusAlertMessage = `Failed to connect to ${this.target.name}`;
                    this.showStatusAlert = true;
                    this.checkingStatus = false;
                    throw error;
                });
        },
        toggleTask: function(task) {
            axios
                .get(`/apis/v1/servers/toggle_task/?name=${task.name}`)
                .then(response => {
                    this.loadTarget();
                    this.statusAlertMessage = `${
                        response.data.enabled ? 'Enabled' : 'Disabled'
                    } task ${task.name} on ${this.target.name}`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.statusAlertMessage = `Failed to disable task ${task.name} on ${this.target.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    }
                });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
</style>
