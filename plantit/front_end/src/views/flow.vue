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
        <b-container fluid>
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
                        <b-row
                            ><b-col
                                >Configure this flow's parameters.</b-col
                            ></b-row
                        >
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
                                    Input {{ flow.config.from }}
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runinput
                            :user="user"
                            :kind="flow.config.from"
                            v-on:inputSelected="inputSelected"
                        ></runinput>
                        <br />
                        <b-row
                            ><b-col
                                >Enter an input file pattern (optional).</b-col
                            ></b-row
                        >
                        <br />
                        <b-form-group
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
            <b-row v-if="flow.config && flow.config.to">
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
                                    Output {{ flow.config.to }}
                                </h4>
                            </b-col>
                        </b-row>
                        <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                        <runoutput
                            :user="user"
                            kind="Directory"
                            v-on:outputSelected="outputSelected"
                        ></runoutput>
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
                    <b-button @click="onStart" variant="success" block>
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
            params: [],
            input: {
                kind: '',
                from: '',
                pattern: ''
            },
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
        loadFlow() {
            axios
                .get(`/apis/v1/flows/${this.username}/${this.name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flow = response.data;
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
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        inputSelected(path) {
            this.input.from = path;
            this.input.kind = this.flow.config.from;
        },
        outputSelected(path) {
            this.output.to = path;
        },
        targetSelected(target) {
            if (this.targetIsJobqueue) {
                this.target.walltime = this.target.max_walltime;
                this.target.mem = this.target.max_mem;
                this.target.cores = this.target_max_cores;
                this.target.processes = this.target.max_processes;
                this.target.queue = this.target.queue;
                this.target.project = this.target.project;
            }
            this.target = target;
        },
        onStart() {
            this.params['config'] = {};
            this.params['config']['api_url'] = '/apis/v1/runs/status/';
            if (this.targetIsJobqueue) {
                this.target.jobqueue = {
                    walltime: this.target.walltime
                        ? this.target.walltime
                        : '01:00:00',
                    cores: this.target.cores ? this.target.cores : 1,
                    processes: this.target.processes ? this.target.cores : 1,
                    queue: this.target.queue
                        ? this.target.queue
                        : this.target.queue
                };
                if (this.target.mem !== undefined && this.target.mem > 0)
                    this.target.jobqueue['mem'] = this.target.mem;
                if (
                    this.target.project !== undefined &&
                    this.target.project !== ''
                )
                    this.target.jobqueue['project'] = this.target.project;
            }
            let config = {
                name: this.flow.config.name,
                image: this.flow.config.image,
                clone:
                    this.flow.config.clone !== null
                        ? this.flow.config.clone
                        : false,
                params: this.params,
                target: this.target,
                commands: this.flow.config.commands
            };
            if (this.flow.config.from) config.input = this.input;
            if (this.flow.config.to) {
                config.output = this.output;
            }
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
            'loggedIn',
            'darkMode'
        ]),
        targetIsJobqueue() {
            return (
                this.target.executor === 'slurm' ||
                this.target.executor === 'pbs'
            );
        },
        parametersUnready() {
            return this.params.some(param => param.value === '');
        },
        inputUnready() {
            return (
                this.input.irods_path === null || this.input.irods_path === ''
            );
        },
        outputUnready() {
            return (
                this.output === null ||
                this.output.path === null ||
                this.output.path === '' ||
                this.output.name === null ||
                this.output.name === ''
            );
        },
        targetUnready() {
            return this.target.name === '';
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
