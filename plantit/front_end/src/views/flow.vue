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
                                <h4
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    <i class="fas fa-keyboard fa-fw"></i>
                                    Configure Parameters
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <b-row
                            ><b-col
                                ><b
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    Configure parameters for this run.
                                </b>
                                <br /><b-table
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
                                        {{
                                            param.item.key
                                                .split('=')[0]
                                                .toLowerCase()
                                        }}
                                    </template>
                                    <template v-slot:cell(value)="param">
                                        <!--<multiselect
                                            v-if="
                                                param.key === 'filetype' &&
                                                    this.input.patterns.length >
                                                        0
                                            "
                                            :multiple="true"
                                            :close-on-select="false"
                                            :clear-on-select="false"
                                            :preserve-search="true"
                                            :preselect-first="true"
                                            v-model="inputSelectedPatterns"
                                            :options="input.patterns"
                                        ></multiselect>-->
                                        <b-form-input
                                            size="sm"
                                            v-model="param.item.value"
                                            :placeholder="
                                                param.item.key.split('=')
                                                    .length === 1
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
                                    </template> </b-table></b-col
                        ></b-row>
                    </b-card>
                </b-col>
            </b-row>
            <b-row
                v-if="
                    flow !== null &&
                        flow.config.input !== undefined &&
                        flow.config.input.path !== undefined
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
                                    <i class="fas fa-download fa-fw"></i>
                                    Select Input
                                    {{
                                        this.input.kind[0].toUpperCase() +
                                            this.input.kind.substr(1)
                                    }}
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runinput
                            :default-path="flow.config.input.path"
                            :user="user"
                            :kind="input.kind"
                            v-on:inputSelected="inputSelected"
                        ></runinput>
                        <b-row v-if="input.filetypes.length > 0">
                            <b-col>
                                <b
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    Select one or more input filetypes.
                                </b>
                                <multiselect
                                    :multiple="true"
                                    :close-on-select="false"
                                    :clear-on-select="false"
                                    :preserve-search="true"
                                    :preselect-first="true"
                                    v-model="inputSelectedPatterns"
                                    :options="input.filetypes"
                                ></multiselect>
                            </b-col>
                        </b-row>
                        <b-alert
                            class="mt-1"
                            :variant="
                                inputFiletypeSelected ? 'success' : 'danger'
                            "
                            :show="true"
                            >Selected:
                            {{
                                inputFiletypeSelected
                                    ? '*.' + inputSelectedPatterns.join(', *.')
                                    : 'None'
                            }}
                            <i
                                v-if="inputFiletypeSelected"
                                class="fas fa-check text-success"
                            ></i>
                            <i
                                v-else
                                class="fas fa-exclamation text-danger"
                            ></i>
                        </b-alert>
                    </b-card>
                </b-col>
            </b-row>
            <b-row
                v-if="
                    flow &&
                        flow.config &&
                        flow.config.input !== undefined &&
                        flow.config.output.path !== undefined
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
                                    <i class="fas fa-upload fa-fw"></i>
                                    Select Output Directory
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runoutput
                            :user="user"
                            v-on:outputSelected="outputSelected"
                        ></runoutput>
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
                                    <i class="fas fa-server fa-fw"></i> Select
                                    Deployment Target
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
                        :disabled="!flowReady"
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
import Multiselect from 'vue-multiselect';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'flow',
    components: {
        Multiselect,
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
                filetypes: []
            },
            inputSelectedPatterns: [],
            outputSpecified: false,
            output: {
                from: '',
                to: '',
                include: {
                    patterns: [],
                    names: []
                },
                exclude: {
                    patterns: [],
                    names: []
                }
            },
            includedFile: '',
            excludedFile: '',
            includedPattern: '',
            excludedPattern: '',
            output_include_fields: [
                {
                    key: 'name',
                    label: 'Included File Names'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            output_include_pattern_fields: [
                {
                    key: 'name',
                    label: 'Included File Patterns'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            output_exclude_fields: [
                {
                    key: 'name',
                    label: 'Excluded File Names'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            output_exclude_pattern_fields: [
                {
                    key: 'name',
                    label: 'Excluded File Patterns'
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
        addIncludedFile(name) {
            let index = this.output.include.names.indexOf(name);
            if (index > -1) {
                alert("You've already included this file name.");
                return;
            }
            this.output.include.names.push(name);
        },
        removeIncludedFile(name) {
            let index = this.output.include.names.indexOf(name);
            if (index > -1) this.output.include.names.splice(index, 1);
        },
        addExcludedFile(name) {
            let index = this.output.exclude.names.indexOf(name);
            if (index > -1) {
                alert("You've already excluded this file name.");
                return;
            }
            this.output.exclude.names.push(name);
        },
        removeExcludedFile(name) {
            let index = this.output.exclude.names.indexOf(name);
            if (index > -1) this.output.exclude.names.splice(index, 1);
        },
        addIncludedPattern(pattern) {
            let index = this.output.include.patterns.indexOf(pattern);
            if (index > -1) {
                alert("You've already included this file pattern.");
                return;
            }
            this.output.include.patterns.push(pattern);
        },
        removeIncludedPattern(pattern) {
            let index = this.output.include.patterns.indexOf(pattern);
            if (index > -1) this.output.include.patterns.splice(index, 1);
        },
        addExcludedPattern(pattern) {
            let index = this.output.exclude.patterns.indexOf(pattern);
            if (index > -1) {
                alert("You've already excluded this file pattern.");
                return;
            }
            this.output.exclude.patterns.push(pattern);
        },
        removeExcludedPattern(pattern) {
            let index = this.output.exclude.patterns.indexOf(pattern);
            if (index > -1) this.output.exclude.patterns.splice(index, 1);
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
                    if (!this.flowValidated)
                        this.flowValidationErrors = response.data.errors;
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
                        'input' in response.data.config &&
                        response.data.config.input !== undefined &&
                        response.data.config.input.path !== undefined &&
                        response.data.config.input.kind !== undefined
                    ) {
                        this.input.from =
                            response.data.config.input.path !== null
                                ? response.data.config.input.path
                                : '';
                        this.input.kind = response.data.config.input.kind;
                        this.input.filetypes =
                            response.data.config.input.filetypes !==
                                undefined &&
                            response.data.config.input.filetypes !== null
                                ? response.data.config.input.filetypes
                                : [];
                        if (this.input.filetypes.length > 0)
                            this.inputSelectedPatterns = this.input.filetypes;
                    }

                    // if a local output path is specified, add it to included files
                    if (
                        response.data.config.output !== undefined &&
                        response.data.config.output.path !== undefined
                    ) {
                        this.output.from =
                            response.data.config.output.path !== null
                                ? response.data.config.output.path
                                : '';
                        if (
                            response.data.config.output.include !== undefined &&
                            response.data.config.output.include.names !==
                                undefined
                        )
                            this.output.include.names =
                                response.data.config.output.include.names;
                        if (
                            response.data.config.output.include !== undefined &&
                            response.data.config.output.include.patterns !==
                                undefined
                        )
                            this.output.include.patterns =
                                response.data.config.output.include.patterns;
                        if (
                            response.data.config.output.exclude !== undefined &&
                            response.data.config.output.exclude.names !==
                                undefined
                        )
                            this.output.exclude.names =
                                response.data.config.output.exclude.names;
                        if (
                            response.data.config.output.exclude !== undefined &&
                            response.data.config.output.exclude.patterns !==
                                undefined
                        )
                            this.output.exclude.patterns =
                                response.data.config.output.exclude.patterns;
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
            if ('gpu' in this.flow.config) config['gpu'] = this.flow.config.gpu;
            if ('branch' in this.flow.config)
                config['branch'] = this.flow.config.branch;
            if (this.flow.config.mount !== null)
                config['mount'] = this.flow.config.mount;
            if (this.input !== undefined && this.input.from) {
                config.input = this.input;
                config.input.patterns =
                    this.inputSelectedPatterns.length > 0
                        ? this.inputSelectedPatterns
                        : this.input.filetypes;
                // if (config.input.kind === '')
                //     config.input.kind =
                //         'from_directory' in this.flow.config
                //             ? this.flow.config.from_directory
                //                 ? 'directory'
                //                 : '.' in this.input.from
                //                 ? 'file'
                //                 : 'files'
                //             : this.input.from.indexOf('.') !== -1
                //             ? 'file'
                //             : 'files';
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
        },
        inputFiletypeSelected: function() {
            return this.inputSelectedPatterns.some(pattern => pattern !== '');
        },
        inputReady: function() {
            if (this.flow !== null && this.flow.config.input !== undefined)
                return (
                    this.flow.config.input.path !== undefined &&
                    this.input.from !== '' &&
                    this.input.kind !== '' &&
                    this.inputFiletypeSelected
                );
            return true;
        },
        outputReady: function() {
            if (
                this.flow &&
                this.flow.config &&
                this.flow.config.input !== undefined &&
                this.flow.config.output.path !== undefined
            )
                return this.output.to !== '';
            return true;
        },
        flowReady: function() {
            return (
                !this.flowLoading &&
                this.flowValidated &&
                this.inputReady &&
                this.outputReady &&
                this.target.name !== ''
            );
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
