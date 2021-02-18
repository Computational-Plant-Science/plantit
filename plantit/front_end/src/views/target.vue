<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
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
                        :bg-variant="darkMode ? 'dark' : 'white'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        border-variant="default"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :text-variant="darkMode ? 'white' : 'dark'"
                        class="overflow-hidden"
                    >
                        <div :class="darkMode ? 'theme-dark' : 'theme-light'">
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
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                {{ target.name }}
                                            </h2>
                                            <b-badge
                                                class="mr-1"
                                                :variant="
                                                    target.public
                                                        ? 'success'
                                                        : 'warning'
                                                "
                                                >{{
                                                    target.public
                                                        ? 'Public'
                                                        : 'Private'
                                                }}</b-badge
                                            >
                                            <br />
                                            <small>{{
                                                target.description
                                            }}</small>
                                        </b-col>
                                    </b-row>
                                    <hr/>
                                    <h5>Configuration </h5>
                                    <b-row>
                                        <b-col>
                                            <small>Executor</small>
                                        </b-col>
                                        <b-col cols="10">
                                            {{ target.executor }}
                                        </b-col>
                                    </b-row>
                                    <b-row>
                                        <b-col>
                                            <small>Working directory</small>
                                        </b-col>
                                        <b-col cols="10">
                                            {{ target.workdir }}
                                        </b-col>
                                    </b-row>
                                  <b-row>
                                        <b-col>
                                            <small>Pre-commands</small>
                                        </b-col>
                                        <b-col cols="10">
                                            <b
                                                ><code>{{
                                                    ' ' + target.pre_commands
                                                }}</code></b
                                            >
                                        </b-col>
                                    </b-row>
                                    <hr/>
                                    <h5>Resources Available <small>per container</small></h5>
                                    <b-row>
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                            ><b>{{ target.max_cores }}</b>
                                            cores</b-col
                                        >
                                      </b-row>
                                    <b-row>
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                            ><b>{{ target.max_processes }}</b>
                                            processes</b-col
                                        >
                                      </b-row>
                                    <b-row>
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                            ><span
                                                v-if="parseInt(target.max_mem)"
                                                >{{ target.max_mem }} GB
                                                memory</span
                                            >
                                            <span
                                                v-else-if="
                                                    parseInt(target.max_mem) > 0
                                                "
                                                class="text-danger"
                                                >{{ target.max_mem }} GB
                                                memory</span
                                            >
                                            <span
                                                v-else-if="
                                                    parseInt(target.max_mem) ===
                                                        -1
                                                "
                                                >virtual memory</span
                                            ></b-col
                                        >
                                      </b-row>
                                    <b-row>
                                        <b-col
                                            align-self="center"
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            cols="1"
                                        >
                                            <span v-if="target.gpu">
                                                GPU
                                                <i
                                                    :class="
                                                        target.gpu
                                                            ? 'text-warning'
                                                            : ''
                                                    "
                                                    class="far fa-check-circle"
                                                ></i>
                                            </span>
                                            <span v-else
                                                >No GPU
                                                <i
                                                    class="far fa-times-circle"
                                                ></i
                                            ></span>
                                        </b-col>
                                    </b-row>
                                    <hr />
                                    <b-row>
                                        <b-col align-self="center text-left"
                                            ><small
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                >{{
                                                    `You ${
                                                        target.role === 'own'
                                                            ? target.role
                                                            : 'can ' +
                                                              target.role
                                                    }`
                                                }}
                                                this deployment target.</small
                                            ></b-col
                                        >
                                        <b-col md="auto" align-self="end"
                                            ><b-button
                                                :variant="
                                                    darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                title="Check Connection Status"
                                                @click="checkStatus"
                                            >
                                                <i
                                                    class="fas fa-network-wired"
                                                ></i>
                                                Check Status
                                            </b-button></b-col
                                        >
                                    </b-row>
                                </b-col>
                            </b-row>
                        </div>
                    </b-card>
                </b-col>
                <b-col md="auto">
                    <b-row>
                        <b-col></b-col>
                        <b-col md="auto"><h5>Settings</h5></b-col>
                    </b-row>
                    <b-row>
                        <b-col
                            md="auto"
                            v-if="target.role === 'own'"
                            align-self="start"
                            :class="darkMode ? 'text-white' : 'text-dark'"
                        >
                            <b-form-checkbox
                                v-model="singularityCacheCleaning"
                                @change="toggleSingularityCacheCleaning(target)"
                                switch
                                size="md"
                            >
                            </b-form-checkbox
                        ></b-col>
                        <b-col
                            md="auto"
                            align-self="start"
                            :class="
                                darkMode
                                    ? 'text-white text-right'
                                    : 'text-dark text-right'
                            "
                        >
                            <small v-if="target.singularity_cache_clean_enabled"
                                >Cleaning Singularity cache every
                                {{
                                    prettifyDuration(
                                        target.singularity_cache_clean_delay
                                    )
                                }}</small
                            >
                            <small v-else>Not cleaning Singularity cache</small>
                        </b-col>
                    </b-row>
                </b-col>
            </b-row>
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
        </b-container>
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'target.vue',
    data: function() {
        return {
            target: null,
            targetLoading: false,
            checkingStatus: false,
            showStatusAlert: false,
            statusAlertMessage: '',
            singularityCacheCleaning: false
        };
    },
    mounted() {
        this.loadTarget();
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
            'flowConfigs',
            'loggedIn',
            'darkMode'
        ])
    },
    methods: {
        prettifyDuration: function(dur) {
            return moment.duration(dur, 'seconds').humanize();
        },
        loadTarget: function() {
            this.targetLoading = true;
            return axios
                .get(
                    `/apis/v1/targets/get_by_name/?name=${this.$route.params.name}`
                )
                .then(response => {
                    this.target = response.data;
                    this.singularityCacheCleaning = response.data.singularity_cache_clean_enabled;
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
                .get(`/apis/v1/targets/status/?name=${this.$route.params.name}`)
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
        toggleSingularityCacheCleaning: function(target) {
            if (target.singularity_cache_clean_enabled)
                axios
                    .get(
                        `/apis/v1/targets/unschedule_singularity_cache_cleaning/?name=${target.name}`
                    )
                    .then(() => {
                      this.loadTarget();
                        this.statusAlertMessage = `Disabled Singularity cache cleaning on ${target.name}`;
                        this.showStatusAlert = true;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        if (error.response.status === 500) {
                            this.statusAlertMessage = `Failed to disable Singularity cache cleaning on ${target.name}`;
                            this.showStatusAlert = true;
                            throw error;
                        }
                    });
            else
                axios
                    .get(
                        `/apis/v1/targets/schedule_singularity_cache_cleaning/?name=${
                            target.name
                        }&delay=${moment
                            .duration(
                                target.singularity_cache_clean_delay,
                                'seconds'
                            )
                            .asSeconds()}`
                    )
                    .then(() => {
                        this.loadTarget();
                        this.statusAlertMessage = `Enabled Singularity cache cleaning on ${target.name}`;
                        this.showStatusAlert = true;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        if (error.response.status === 500) {
                            this.statusAlertMessage = `Failed to enable Singularity cache cleaning on ${target.name}`;
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
