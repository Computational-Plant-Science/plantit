<template>
    <div class="w-100 p-3">
        <br />
        <br />
        <b-row>
            <b-col>
                <b-card
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="default"
                    class="overflow-hidden"
                >
                    <flowdetail
                        :show-public="
                            flow.repo.owner.login ===
                                currentUserDjangoProfile.profile.github_username
                        "
                        :workflow="flow"
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
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="white"
                >
                    <b-row align-v="center">
                        <b-col style="color: white">
                            <h4>
                                Parameters
                            </h4>
                        </b-col>
                    </b-row>
                    <hr />
                    <b-row
                        ><b-col>Configure this flow's parameters.</b-col></b-row
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
                                        : param.item.key.split('=')[1].toLowerCase()
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
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="default"
                >
                    <b-row align-v="center">
                        <b-col style="color: white">
                            <h4>Input {{ flow.config.from }}</h4>
                        </b-col>
                    </b-row>
                    <hr />
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
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="default"
                >
                    <b-row align-v="center">
                        <b-col style="color: white">
                            <h4>Output {{ flow.config.to }}</h4>
                        </b-col>
                    </b-row>
                    <hr />
                    <runoutput
                        :user="user"
                        kind="Directory"
                        v-on:outputSelected="outputSelected"
                    ></runoutput>
                    <br />
                    <b-row
                        ><b-col
                            >Specify an output path (required) and file pattern
                            (optional).</b-col
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
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="default"
                >
                    <b-row align-v="center">
                        <b-col style="color: white">
                            <h4>
                                Deployment Target
                            </h4>
                        </b-col>
                    </b-row>
                    <hr />
                    <runtarget
                        :selected="target"
                        v-on:targetSelected="targetSelected"
                    ></runtarget>
                    <b-card
                        v-if="target.max_walltime && target.name !== 'Sandbox'"
                        border-variant="white"
                        footer-bg-variant="white"
                        sub-title="Configure resource requests."
                    >
                        <br />
                        <b-form-group
                            :state="target.walltime <= target.max_walltime"
                            description="Walltime to be requested from the cluster resource scheduler."
                            label="Walltime"
                        >
                            <b-form-input
                                size="sm"
                                v-model="target.walltime"
                                :placeholder="'Max: 01:00:00'"
                            ></b-form-input>
                        </b-form-group>
                        <b-form-group
                            :state="target.memory <= target.max_mem"
                            description="Memory to be requested from the cluster resource scheduler."
                            label="Memory"
                        >
                            <b-form-input
                                size="sm"
                                v-model="target.memory"
                                :placeholder="
                                    'Max: ' + target.max_mem + 'GB'
                                "
                            ></b-form-input>
                        </b-form-group>
                    </b-card>
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
            this.target = target;
        },
        onStart() {
            this.params['config'] = {};
            this.params['config']['api_url'] = '/apis/v1/runs/status/';
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
        ...mapGetters(['currentUserDjangoProfile']),
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
