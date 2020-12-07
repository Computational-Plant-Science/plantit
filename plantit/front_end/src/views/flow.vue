<template>
    <div
        class="w-100 h-100 p-3"
        :style="
            darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <b-container fluid class="p-3 vl">
            <b-row>
                <b-col>
                    <b-card
                        :bg-variant="darkMode ? 'dark' : 'white'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        :border-variant="darkMode ? 'dark' : 'white'"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :text-variant="darkMode ? 'white' : 'dark'"
                        class="overflow-hidden"
                    >
                        <b-alert :show="flowIsValid" variant="danger"
                            >This flow's configuration is invalid. It cannot be
                            run in this state.
                            <b-link
                                :href="
                                    'https://github.com/' +
                                        this.username +
                                        '/' +
                                        this.name +
                                        '/issues/new'
                                "
                                ><i class="fab fa-github fa-1x mr-1 fa-fw"></i
                                >File an issue?</b-link
                            ></b-alert
                        >
                        <flowdetail
                            :show-public="true"
                            :flow="flow"
                            :selectable="false"
                        ></flowdetail>
                    </b-card>
                </b-col>
            </b-row>
            <b-row
                v-if="
                    flow.config.params !== undefined
                        ? flow.config.params.length !== 0
                        : false
                "
            >
                <b-col>
                    <b-card
                        :bg-variant="darkMode ? 'dark' : 'white'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        :border-variant="darkMode ? 'dark' : 'white'"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :text-variant="darkMode ? 'white' : 'dark'"
                    >
                        <b-row align-v="center">
                            <b-col>
                                <h4
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    Parameters
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <b-row><b-col>Configure parameters.</b-col></b-row>
                        <br />
                        <b-table
                            :items="params"
                            :fields="fields"
                            responsive="sm"
                            borderless
                            small
                            sticky-header="true"
                            caption-top
                            :table-variant="darkMode ? 'dark' : 'white'"
                        >
                            <template v-slot:cell(name)="param">
                                {{ param.item.key.split('=')[0].toLowerCase() }}
                            </template>
                            <template v-slot:cell(value)="param">
                                <b-form-input
                                    size="sm"
                                    v-model="param.item.value"
                                    :placeholder="
                                        param.item.key.split('=').length === 1
                                            ? 'Enter a value for \'' +
                                              param.item.key
                                                  .split('=')[0]
                                                  .toLowerCase() +
                                              '\''
                                            : param.item.key
                                                  .split('=')[1]
                                                  .toLowerCase()
                                    "
                                ></b-form-input>
                            </template>
                        </b-table>
                    </b-card>
                </b-col>
            </b-row>
            <b-row v-if="flow && flow.config.from">
                <b-col>
                    <b-card
                        :bg-variant="darkMode ? 'dark' : 'white'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        :border-variant="darkMode ? 'dark' : 'white'"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :text-variant="darkMode ? 'white' : 'dark'"
                    >
                        <b-row align-v="center">
                            <b-col>
                                <h4
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    Input
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runinput
                            :default-path="flow.config.from"
                            :user="user"
                            :kind="flow.config.from"
                            v-on:inputSelected="inputSelected"
                        ></runinput>
                        <br />
                        <b-form-group
                            v-if="input.kind === 'directory'"
                            description="All files in the input directory matching this pattern will be selected."
                        >
                            <b-form-input
                                size="sm"
                                v-model="input.pattern"
                                :placeholder="'Enter a file pattern'"
                            ></b-form-input>
                        </b-form-group>
                    </b-card>
                </b-col>
            </b-row>
            <b-row v-if="flow.config && flow.config.to !== undefined">
                <b-col>
                    <b-card
                        :bg-variant="darkMode ? 'dark' : 'white'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        :border-variant="darkMode ? 'dark' : 'white'"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :text-variant="darkMode ? 'white' : 'dark'"
                    >
                        <b-row align-v="center">
                            <b-col>
                                <h4
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    Output
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runoutput
                            :user="user"
                            v-on:outputSelected="outputSelected"
                        ></runoutput>
                        <div v-if="!outputSpecified">
                            <br />
                            <b-row
                                ><b-col
                                    >Specify an output path (required) and file
                                    pattern (optional).</b-col
                                ></b-row
                            >
                            <br />
                            <b-form-group
                                description="The directory in which the flow will deposit output files."
                            >
                                <b-form-input
                                    size="sm"
                                    v-model="output.from"
                                    :placeholder="'Enter a filesystem path'"
                                ></b-form-input>
                            </b-form-group>
                            <b-form-group
                                description="All files in the output directory matching this pattern will be selected."
                            >
                                <b-form-input
                                    size="sm"
                                    v-model="output.pattern"
                                    :placeholder="'Enter a file pattern'"
                                ></b-form-input>
                            </b-form-group>
                        </div>
                    </b-card>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <b-card
                        :bg-variant="darkMode ? 'dark' : 'white'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        :border-variant="darkMode ? 'dark' : 'white'"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :text-variant="darkMode ? 'white' : 'dark'"
                    >
                        <b-row align-v="center">
                            <b-col>
                                <h4
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    Target
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runtarget
                            :selected="target"
                            v-on:targetSelected="targetSelected"
                        ></runtarget>
                    </b-card>
                </b-col>
            </b-row>
            <br />
            <b-row>
                <b-col>
                    <b-button
                        :disabled="!flowIsValid"
                        @click="onStart"
                        variant="success"
                        block
                    >
                        Start
                    </b-button>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import flowdetail from '../components/flow-detail';
import runinput from '../components/run-input';
import runoutput from '../components/run-output';
import runtarget from '../components/run-target';
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '../router';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'flow',
    components: {
        flowdetail,
        runinput,
        runoutput,
        runtarget
    },
    props: {
        username: {
            required: true
        },
        name: {
            required: true
        }
    },
    data: function() {
        return {
            flow: null,
            flowLoading: true,
            flowValidated: false,
            params: [],
            input: {
                kind: '',
                from: '',
                pattern: ''
            },
            outputSpecified: false,
            output: {
                from: '',
                to: '',
                pattern: ''
            },
            target: {
                name: ''
            },
            fields: [
                {
                    key: 'name',
                    label: 'Name'
                },
                {
                    key: 'value',
                    label: 'Value'
                }
            ]
        };
    },
    mounted: function() {
        this.loadFlow();
    },
    methods: {
        validate() {
            axios
                .get(`/apis/v1/flows/${this.username}/${this.name}/validate/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flowValidated = response.data.result;
                    this.flowLoading = false;
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        loadFlow() {
            axios
                .get(`/apis/v1/flows/${this.username}/${this.name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flow = response.data;

                    this.validate();

                    // if a local input path is specified, set it
                    if (
                        'from' in response.data.config &&
                        response.data.config.from !== undefined &&
                        response.data.config.from !== null
                    ) {
                        this.input.from = response.data.config.from;
                    }

                    // if a local output path is specified, set it and don't show options
                    if (
                        'to' in response.data.config &&
                        response.data.config.to !== undefined &&
                        response.data.config.to !== null
                    ) {
                        this.output.from = response.data.config.to;
                        this.outputSpecified = true;
                    }

                    // if params are specified, set them
                    if ('params' in response.data['config'])
                        this.params = response.data['config']['params'].map(
                            param => {
                                let split = param.split('=');
                                return {
                                    key: split[0],
                                    value: split.length === 2 ? split[1] : ''
                                };
                            }
                        );

                    // if we have pre-configured values for this flow, populate them
                    if (
                        `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}` in
                        this.flowConfigs
                    ) {
                        let flowConfig = this.flowConfigs[
                            `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`
                        ];
                        this.params = flowConfig.params;
                        this.input = flowConfig.input;
                        this.output = flowConfig.output;
                        this.target = flowConfig.target;
                    }
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        inputSelected(node) {
            this.input.from = node.path;
            this.input.many = this.flow.config.from_directory;
            this.input.kind =
                node.hasSubDirs !== undefined ? 'directory' : 'file';
        },
        outputSelected(node) {
            this.output.to = node.path;
        },
        targetSelected(target) {
            this.target = target;
        },
        onStart() {
            if (!this.flow.config.resources && this.target.name !== 'Sandbox') {
                alert('This flow can only run in the Sandbox.');
                return;
            }

            // prepare run definition
            this.params['config'] = {};
            this.params['config']['api_url'] = '/apis/v1/runs/status/';
            let target = this.target;
            if (this.flow.config.resources)
                target['resources'] = this.flow.config.resources;
            let config = {
                name: this.flow.config.name,
                image: this.flow.config.image,
                clone:
                    this.flow.config.clone !== null
                        ? this.flow.config.clone
                        : false,
                params: this.params,
                target: target,
                commands: this.flow.config.commands
            };
            if (this.flow.config.from) {
                config.input = this.input;
                config.input.many =
                    'from_directory' in this.flow.config
                        ? this.flow.config.from_directory
                        : false;
            }
            if (this.flow.config.to) {
                config.output = this.output;
            }

            // save config
            this.$store.dispatch('setFlowConfig', {
                name: this.flowKey,
                config: config
            });

            // submit run
            axios({
                method: 'post',
                url: `/apis/v1/runs/`,
                data: {
                    repo: this.flow.repo,
                    config: config
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    router.push({
                        name: 'run',
                        params: {
                            username: this.currentUserDjangoProfile.username,
                            id: response.data.id
                        }
                    });
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
            'flowConfigs',
            'loggedIn',
            'darkMode'
        ]),
        flowIsValid: function() {
            return !this.flowLoading && !this.flowValidated;
        },
        flowKey: function() {
            return `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`;
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: white
    padding: 24px

    img
        margin-top: 20px
        max-width: 140px
        max-height: 190px
</style>
