<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent">
        <div v-if="isRootPath">
            <b-row
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <i class="fas fa-server fa-fw"></i>
                        Agents
                    </h4></b-col
                >
                <b-col md="auto" class="ml-0 mb-1" align-self="center"
                    ><b-button
                        id="refresh-agents"
                        :disabled="agentsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
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
                    ><b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="topright"
                        target="refresh-agents"
                        title="Refresh Agents"
                        >Click here to refresh the list of agents.</b-popover
                    ></b-col
                >
            </b-row>
            <b-row v-if="agentsLoading" class="mt-2">
                <b-col>
                    <b-spinner
                        small
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading agents...</span
                    >
                </b-col>
            </b-row>
            <b-card-group deck columns v-else-if="getAgents.length !== 0">
                <b-card
                    v-for="agent in getAgents"
                    v-bind:key="agent.name"
                    :bg-variant="profile.darkMode ? 'dark' : 'white'"
                    :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                    border-variant="secondary"
                    :header-border-variant="
                        profile.darkMode ? 'secondary' : 'default'
                    "
                    :text-variant="profile.darkMode ? 'white' : 'dark'"
                    style="min-width: 30rem"
                    class="overflow-hidden mb-4"
                >
                    <b-row style="z-index: 10">
                        <b-col cols="10">
                            <h4>
                                <b-link
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    variant="outline-dark"
                                    :to="{
                                        name: 'agent',
                                        params: {
                                            name: agent.name,
                                        },
                                    }"
                                >
                                    {{ agent.name }}
                                </b-link>
                                <small>
                                    <i
                                        v-if="agent.is_healthy"
                                        title="Healthy"
                                        class="fas fa-heartbeat text-success fa-fw"
                                    ></i
                                    ><i
                                        v-else
                                        title="Unhealthy"
                                        class="fas fa-heart-broken text-danger fa-fw"
                                    ></i
                                    ><i
                                        v-if="agent.public"
                                        title="Public"
                                        class="fas fa-unlock text-secondary fa-fw"
                                    ></i>
                                    <i
                                        v-else
                                        title="Protected"
                                        class="fas fa-lock text-secondary fa-fw"
                                    ></i>
                                    <i
                                        v-if="agent.disabled"
                                        title="Disabled"
                                        class="fas fa-exclamation-circle text-secondary fa-fw"
                                    ></i>
                                </small>
                            </h4>
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
                        style="
                            max-height: 4rem;
                            position: absolute;
                            right: 20px;
                            top: 20px;
                            z-index: 1;
                        "
                        right
                        :src="agent.logo"
                    ></b-img>
                </b-card>
            </b-card-group>
            <b-row v-else
                ><b-col
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >No agents available.</span
                    >
                    <br /> </b-col
            ></b-row>
        </div>
        <router-view
            v-else
            :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
        ></router-view>
    </b-container>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
import moment from 'moment';
import { guid } from '@/utils';

export default {
    name: 'agents',
    data: function () {
        return {
            checkingConnection: false,
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('agents', ['agentsPermitted', 'agentsLoading']),
        isRootPath() {
            return this.$route.name === 'agents';
        },
        getAgents() {
            return this.agentsPermitted(this.profile.djangoProfile.username);
        },
    },
    methods: {
        async checkAgentConnection() {
            this.checkingConnection = true;
            let data =
                this.agentAuthentication === 'password'
                    ? {
                          hostname: this.agentHost,
                          port: this.agentPort,
                          username: this.agentUsername,
                          password: this.authenticationPassword,
                      }
                    : {
                          hostname: this.agentHost,
                          port: this.agentPort,
                          username: this.agentUsername,
                      };
            await axios({
                method: 'post',
                url: `/apis/v1/users/check_connection/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200 && response.data.success) {
                        this.agentConnectionComplete = true;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Connection to ${this.agentName} succeeded`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    } else {
                        this.agentConnectionComplete = false;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to connect to ${this.agentName}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    }
                    this.checkingConnection = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to connect to ${this.agentName}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.agentConnectionComplete = false;
                    this.checkingConnection = false;
                    throw error;
                });
        },
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        refreshAgents() {
            this.$store.dispatch('agents/loadAll');
        },
        isJobQueue(executor) {
            return executor !== 'Local';
        },
        isSLURM(executor) {
            return executor === 'SLURM';
        },
    },
};
</script>

<style scoped></style>
