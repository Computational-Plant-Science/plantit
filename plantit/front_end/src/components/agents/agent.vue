<template>
    <div>
        <b-container class="vl" fluid>
            <b-row no-gutters v-if="!authorized"
                ><b-col
                    ><p :class="profile.darkMode ? 'text-white' : 'text-dark'">
                        <i class="fas fa-exclamation-circle fa-3x fa-fw"></i>
                        <br />
                        <br />
                        You do not have access to this agent.
                        <br /></p></b-col
            ></b-row>
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
                <b-row v-if="agentLoading">
                    <b-col
                        ><b-spinner
                            small
                            label="Loading..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><span
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            >Loading agent...</span
                        ></b-col
                    >
                </b-row>
                <b-row v-else>
                    <b-col
                        ><b-card
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            :header-bg-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            border-variant="secondary"
                            :header-border-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            :text-variant="profile.darkMode ? 'white' : 'dark'"
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
                                    style="
                                        max-height: 3rem;
                                        position: absolute;
                                        right: 20px;
                                        top: 20px;
                                        z-index: 1;
                                    "
                                    right
                                    :src="getAgent.logo"
                                ></b-img>
                                <b-row no-gutters>
                                    <b-col>
                                        <b-row>
                                            <b-col md="auto">
                                                <h4
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    {{ getAgent.name }}
                                                    <small>
                                                        <i
                                                            v-if="
                                                                getAgent.is_healthy
                                                            "
                                                            v-b-tooltip:hover
                                                            title="Healthy"
                                                            class="fas fa-heartbeat text-success fa-fw"
                                                        ></i
                                                        ><i
                                                            v-else
                                                            v-b-tooltip:hover
                                                            title="Unhealthy"
                                                            class="fas fa-heart-broken text-danger fa-fw"
                                                        ></i>
                                                        <i
                                                            v-if="agent.public"
                                                            title="Public"
                                                            class="fas fa-unlock-alt text-success fa-fw"
                                                        ></i>
                                                        <i
                                                            v-else
                                                            title="Protected"
                                                            class="fas fa-lock text-warning fa-fw"
                                                        ></i>
                                                        <i
                                                            v-if="
                                                                getAgent.disabled
                                                            "
                                                            v-b-tooltip:hover
                                                            title="Disabled"
                                                            class="fas fa-exclamation-circle text-secondary fa-fw"
                                                        ></i>
                                                    </small>
                                                </h4>
                                            </b-col>
                                        </b-row>
                                        <b-row
                                            ><b-col
                                                ><small>{{
                                                    getAgent.description
                                                }}</small></b-col
                                            ></b-row
                                        >

                                        <div
                                            v-if="
                                                !getAgent.is_healthy &&
                                                healthcheckOutput.length > 0
                                            "
                                        >
                                            <br />
                                            <b-row
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-container-dark m-0 p-1'
                                                        : 'theme-container-light m-0 p-1'
                                                "
                                            >
                                                <b-col
                                                    class="m-0 p-0 pl-3 pr-3 pt-1 text-danger"
                                                    style="
                                                        white-space: pre-line;
                                                    "
                                                >
                                                    <span
                                                        v-for="line in healthcheckOutput"
                                                        v-bind:key="line"
                                                        v-show="
                                                            line !==
                                                                undefined &&
                                                            line !== null
                                                        "
                                                        >{{ line + '\n' }}</span
                                                    >
                                                </b-col></b-row
                                            >
                                        </div>
                                        <br />
                                        <b-row
                                            ><b-col>
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Configuration
                                                </h5>
                                                <b-row>
                                                    <b-col>
                                                        <small>scheduler</small>
                                                        <br/>
                                                        <b class="ml-3">
                                                            {{
                                                                getAgent.executor
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
                                                      <br/>
                                                        <b class="ml-3">
                                                            {{
                                                                getAgent.workdir
                                                            }}
                                                        </b>
                                                    </b-col>
                                                </b-row>
                                                <b-row>
                                                    <b-col>
                                                        <small
                                                            >setup commands</small
                                                        >
                                                      <br/>
                                                        <b class="ml-3"
                                                            ><code>{{
                                                                getAgent.pre_commands
                                                            }}</code></b
                                                        ></b-col
                                                    >
                                                </b-row>
                                            </b-col>
                                        </b-row>
                                        <br />
                                        <b-row>
                                            <b-col>
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Resources
                                                    <small
                                                        >(per container)</small
                                                    >
                                                </h5>
                                                <b>{{ getAgent.max_cores }}</b>
                                                <small> core(s)</small>
                                                <br />
                                                <b>{{
                                                    getAgent.max_processes
                                                }}</b>
                                                <small> process(es)</small>
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
                                                    ><b>{{ getAgent.max_mem
                                                  }}</b><small>
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
                                        <br />
                                        <b-row>
                                            <b-col md="auto">
                                                <h5>Connection Status</h5> </b-col
                                            ><b-col></b-col
                                            ><b-col class="ml-0" md="auto"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    :disabled="checkingConnection"
                                                    v-b-tooltip.hover
                                                    :title="
                                                        'Verify connection to ' +
                                                        getAgent.name
                                                    "
                                                    @click="checkConnection"
                                                >
                                                    <b-spinner
                                                        small
                                                        v-if="
                                                            checkingConnection
                                                        "
                                                        label="Loading..."
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'light'
                                                                : 'dark'
                                                        "
                                                        class="ml-2"
                                                    ></b-spinner>
                                                    <i
                                                        v-else
                                                        class="fas fa-wave-square fa-fw"
                                                    ></i>
                                                    Check</b-button
                                                ></b-col
                                            >
                                        </b-row>
                                        <Plotly
                                            v-if="healthchecks.length > 0"
                                            :data="healthchecksTimeseriesData"
                                            :layout="
                                                healthchecksTimeseriesLayout
                                            "
                                        ></Plotly>
                                    </b-col>
                                </b-row>
                            </div>
                        </b-card>
                    </b-col>
                </b-row>
            </div>
        </b-container>
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
import moment from 'moment';
import { guid } from '@/utils';
import { Plotly } from 'vue-plotly';

export default {
    name: 'agent',
    components: {
        Plotly,
    },
    data: function () {
        return {
            checkingConnection: false,
            alertEnabled: false,
            alertMessage: '',
            healthcheckOutput: [],
            healthchecks: [],
            loadingHealthchecks: false,
        };
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
        ...mapGetters('workflows', [
            'userWorkflowsLoading',
            'userWorkflows',
            'publicWorkflowsLoading',
            'publicWorkflows',
        ]),
        ...mapGetters('agents', ['agent', 'agentsLoading', 'agentsPermitted']),
        authorized() {
            return this.getAgent.users_authorized.some(
                (u) => u.username === this.profile.djangoProfile.username
            );
        },
        agentLoading() {
            return this.agentsLoading;
        },
        ownsAgent() {
            return (
                this.getAgent.user !== undefined &&
                this.getAgent.user === this.profile.djangoProfile.username
            );
        },
        getAgent() {
            return this.agent(this.$router.currentRoute.params.name);
        },
        mustAuthenticate() {
            return (
                this.getAgent.role !== 'admin' ||
                this.getAgent.authentication === 'password'
            );
        },
        healthchecksTimeseriesData() {
            return [
                {
                    x: this.healthchecks.map((t) =>
                        moment(t.timestamp).format('YYYY-MM-DD HH:mm:ss')
                    ),
                    y: this.healthchecks.map(
                        () =>
                            //t.healthy ? 'Healthy' : 'Unhealthy'
                            ''
                    ),
                    hovertemplate: '<br>%{text}<br><extra></extra>',
                    text: this.healthchecks.map((t) =>
                        t.healthy ? `Succeeded` : `Failed`
                    ),
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        color: this.healthchecks.map((t) =>
                            t.healthy
                                ? 'rgb(214, 223, 93)'
                                : 'rgb(255, 114, 114)'
                        ),
                        line: {
                            color: 'rgba(156, 165, 196, 1.0)',
                            width: 1,
                        },
                        symbol: 'circle',
                        size: 16,
                    },
                },
            ];
        },
        healthchecksTimeseriesLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                height: 150,
                title: {
                    // text: 'Recent Healthchecks',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    showline: false,
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
                    showticklabels: false,
                    showline: false,
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
            };
        },
    },
    async mounted() {
        this.workflowPolicyType = 'none';
        // this.workflowPolicyType =
        //     this.getAgent.workflows_authorized.length > 0
        //         ? 'authorized'
        //         : this.getAgent.workflows_blocked.length > 0
        //         ? 'blocked'
        //         : 'none';

        await this.loadHealthchecks();
    },
    watch: {
        workflowPolicyType() {
            // noop
        },
        agent() {
            // noop
        },
    },
    methods: {
        async loadHealthchecks() {
            this.loadingHealthchecks = true;
            await axios
                .get(
                    `/apis/v1/agents/${this.$router.currentRoute.params.name}/checks/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken,
                        },
                    }
                )
                .then((response) => {
                    this.healthchecks = response.data.healthchecks;
                    this.loadingHealthchecks = false;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.loadingHealthchecks = false;
                    throw error;
                });
        },
        async refreshWorkflows() {
            await Promise.all([
                this.$store.dispatch('workflows/refreshPublic'),
                this.$store.dispatch(
                    'workflows/refreshUser',
                    this.profile.githubProfile.login
                ),
            ]);
        },
        async refreshUsers() {
            await this.$store.dispatch('users/loadAll');
        },
        async authorizeUser(user) {
            this.authorizingUser = true;
            let data = { user: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/authorize_user/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Authorized user ${user.username} for agent ${this.getAgent.name}`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to authorize user ${user.username} for agent ${this.getAgent.name}`,
                            guid: guid().toString(),
                        });
                    }
                    this.$bvModal.hide('authorizeUser');
                    this.authorizingUser = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to authorize user ${user.username} for agent ${this.getAgent.name}`,
                        guid: guid().toString(),
                    });
                    this.$bvModal.hide('authorizeUser');
                    this.authorizingUser = false;
                    throw error;
                });
        },
        async unauthorizeUser(user) {
            this.authorizingUser = true;
            let data = { user: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/unauthorize_user/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Revoked user ${user.username}'s access to agent ${this.getAgent.name}`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to revoke user ${user.username}'s access to agent ${this.getAgent.name}`,
                            guid: guid().toString(),
                        });
                    }
                    this.authorizingUser = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to revoke user ${user.username}'s access to agent ${this.getAgent.name}`,
                        guid: guid().toString(),
                    });
                    this.authorizingUser = false;
                    throw error;
                });
        },
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        async checkConnection() {
            this.checkingConnection = true;
            let data =
                this.getAgent.authentication === 'password'
                    ? {
                          auth: {
                              username: this.authenticationUsername,
                              password: this.authenticationPassword,
                          },
                      }
                    : {
                          auth: {
                              username: this.authenticationUsername,
                          },
                      };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$route.params.name}/health/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        if (response.data.healthy) {
                            await this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Connection to ${this.getAgent.name} succeeded`,
                                guid: guid().toString(),
                                time: moment().format(),
                            });
                            this.healthchecks.push(response.data);
                            var agent = this.getAgent;
                            agent.is_healthy = true;
                            await this.$store.dispatch(
                                'agents/addOrUpdate',
                                agent
                            );
                        } else
                            await this.$store.dispatch('alerts/add', {
                                variant: 'danger',
                                message: `Failed to connect to ${this.getAgent.name}`,
                                guid: guid().toString(),
                                time: moment().format(),
                            });
                    }
                    this.healthcheckOutput = response.data.output;
                    this.checkingConnection = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to connect to ${this.getAgent.name}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.checkingConnection = false;
                    throw error;
                });
        },
        toggleTask: function (task) {
            axios
                .get(`/apis/v1/agents/toggle_task/?name=${task.name}`)
                .then((response) => {
                    this.loadTarget();
                    this.alertMessage = `${
                        response.data.enabled ? 'Enabled' : 'Disabled'
                    } task ${task.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.alertMessage = `Failed to disable task ${task.name} on ${this.getAgent.name}`;
                        this.alertEnabled = true;
                        throw error;
                    }
                });
        },
    },
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
