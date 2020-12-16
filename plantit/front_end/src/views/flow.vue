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
                        <b-alert
                            id="flowInvalid"
                            :show="!this.flowLoading && !this.flowValidated"
                            variant="danger"
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
                            ><br />
                            Errors: {{ this.flowValidationErrors.join(', ') }}
                        </b-alert>
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
                    flow !== null && flow.config.params !== undefined
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
                                <h3
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    <i class="fas fa-keyboard fa-fw"></i> Parameters
                                </h3>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <h5 :class="darkMode ? 'text-white' : 'text-dark'">Configure parameters for this run.</h5>
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
            <b-row v-if="flow !== null && flow.config.from !== undefined">
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
                                <h3
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    <i class="fas fa-download fa-fw"></i> Input
                                </h3>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runinput
                            :default-path="flow.config.from"
                            :user="user"
                            :kind="input.kind"
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
            <b-row v-if="flow && flow.config && flow.config.to !== undefined">
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
                                <h3
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    <i class="fas fa-upload fa-fw"></i> Output
                                </h3>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runoutput
                            :user="user"
                            v-on:outputSelected="outputSelected"
                        ></runoutput>
                        <div v-if="!outputSpecified">
                            <br />
                            <h5 :class="darkMode ? 'text-white' : 'text-dark'">
                                Specify an output path (defaults to your run's
                                working directory).
                            </h5>
                            <b-form-group
                            >
                                <b-form-input
                                    size="sm"
                                    v-model="output.from"
                                    :placeholder="'Enter a directory path'"
                                ></b-form-input>
                            </b-form-group>
                            <h5 :class="darkMode ? 'text-white' : 'text-dark'">Specify a file pattern and/or names to include.</h5>
                            <b-form-group
                            >
                                <b-form-input
                                    size="sm"
                                    v-model="output.include_pattern"
                                    :placeholder="'Enter a file pattern'"
                                ></b-form-input>
                            </b-form-group>
                            <b-row
                                ><b-col md="auto"
                                    ><b-button
                                        variant="success"
                                        @click="addIncludedFile(includedFile)"
                                        ><i class="fas fa-plus fa-1x fa-fw"></i>
                                        Add included file</b-button
                                    ></b-col
                                ><b-col
                                    ><b-form-group>
                                        <b-form-input
                                            v-model="includedFile"
                                            :placeholder="
                                                'Enter a file name'
                                            "
                                        ></b-form-input> </b-form-group></b-col
                            ></b-row>
                            <b-table
                                v-if="output.include.length > 0"
                                :items="output.include"
                                :fields="output_include_fields"
                                class="text-left"
                                responsive="sm"
                                borderless
                                small
                                sticky-header="true"
                                caption-top
                                :table-variant="darkMode ? 'dark' : 'white'"
                            >
                                <template v-slot:cell(name)="include">
                                    {{ include.item }}
                                </template>
                                <template v-slot:cell(actions)="include">
                                    <b-button
                                        size="sm"
                                        variant="outline-danger"
                                        @click="
                                            removeIncludedFile(include.item)
                                        "
                                        ><i
                                            class="fas fa-trash fa-1x fa-fw"
                                        ></i>
                                        Remove</b-button
                                    >
                                </template>
                            </b-table>
                            <h5 :class="darkMode ? 'text-white' : 'text-dark'">Specify a file pattern and/or names to exclude.</h5>
                            <b-form-group>
                                <b-form-input
                                    size="sm"
                                    v-model="output.exclude_pattern"
                                    :placeholder="'Enter a file pattern'"
                                ></b-form-input>
                            </b-form-group>
                            <b-row
                                ><b-col md="auto"
                                    ><b-button
                                        variant="success"
                                        @click="addExcludedFile(excludedFile)"
                                        ><i class="fas fa-plus fa-1x fa-fw"></i>
                                        Add excluded file</b-button
                                    ></b-col
                                ><b-col
                                    ><b-form-group>
                                        <b-form-input
                                            v-model="excludedFile"
                                            :placeholder="
                                                'Enter a file name'
                                            "
                                        ></b-form-input> </b-form-group></b-col
                            ></b-row>
                            <b-table
                                v-if="output.exclude.length > 0"
                                :items="output.exclude"
                                :fields="output_exclude_fields"
                                class="text-left"
                                responsive="sm"
                                borderless
                                small
                                sticky-header="true"
                                caption-top
                                :table-variant="darkMode ? 'dark' : 'white'"
                            >
                                <template v-slot:cell(name)="exclude">
                                    {{ exclude.item }}
                                </template>
                                <template v-slot:cell(actions)="exclude">
                                    <b-button
                                        size="sm"
                                        variant="outline-danger"
                                        @click="
                                            removeExcludedFile(exclude.item)
                                        "
                                        ><i
                                            class="fas fa-trash fa-1x fa-fw"
                                        ></i>
                                        Remove</b-button
                                    >
                                </template>
                            </b-table>
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
                                <h3
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    <i class="fas fa-server fa-fw"></i> Target
                                </h3>
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
                        :disabled="!this.flowLoading && !this.flowValidated"
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
            flowValidationErrors: [],
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
                include_pattern: '',
                include: [],
                exclude_pattern: '',
                exclude: []
            },
            includedFile: '',
            excludedFile: '',
            output_include_fields: [
                {
                    key: 'name',
                    label: 'Included'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            output_exclude_fields: [
                {
                    key: 'name',
                    label: 'Excluded'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
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
        addIncludedFile(path) {
            let index = this.output.include.indexOf(path);
            if (index > -1) {
                alert("You've already included this file.");
                return;
            }
            this.output.include.push(path);
        },
        removeIncludedFile(path) {
            let index = this.output.include.indexOf(path);
            if (index > -1) this.output.include.splice(index, 1);
        },
        addExcludedFile(path) {
            let index = this.output.exclude.indexOf(path);
            if (index > -1) {
                alert("You've already excluded this file.");
                return;
            }
            this.output.exclude.push(path);
        },
        removeExcludedFile(path) {
            let index = this.output.exclude.indexOf(path);
            if (index > -1) this.output.exclude.splice(index, 1);
        },
        validate() {
            axios
                .get(`/apis/v1/flows/${this.username}/${this.name}/validate/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flowValidated = response.data.result;
                    if (this.flowValidated) {
                        if (
                            response.data.from !== 'none' &&
                            this.input.from === '' &&
                            this.input.kind === ''
                        ) {
                            this.input.from = this.flow.config.from;
                            this.input.kind = response.data.from;
                        }
                    } else {
                        this.flowValidationErrors = response.data.errors;
                    }

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
                        response.data.config.from !== undefined
                    ) {
                        this.input.from =
                            response.data.config.from !== null
                                ? response.data.config.from
                                : '';
                    }

                    // if a local output path is specified, set it and don't show options
                    if (
                        'to' in response.data.config &&
                        response.data.config.to !== undefined &&
                        response.data.config.to !== null
                    ) {
                        this.output.from = response.data.config.to;
                        //this.outputSpecified = true;
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
                node['kind'] === 'directory'
                    ? this.flow.config.from_directory
                        ? 'directory'
                        : 'files'
                    : 'file';
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
            if (this.flow.config.mount !== null)
                config['mount'] = this.flow.config.mount;
            if (this.input.from) {
                config.input = this.input;
                if (config.input.kind === '')
                    config.input.kind =
                        'from_directory' in this.flow.config
                            ? this.flow.config.from_directory
                                ? 'directory'
                                : '.' in this.input.from
                                ? 'file'
                                : 'files'
                            : this.input.from.indexOf('.') !== -1
                            ? 'file'
                            : 'files';
            }
            if (this.output.to) {
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
