<template>
    <div class="w-100 p-4">
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
                    header-border-variant="white"
                    class="overflow-hidden"
                >
                    <flowdetail
                        :show-public="
                            flow.repository.owner.login ===
                                currentUserDjangoProfile.profile.github_username
                        "
                        :workflow="flow"
                        :selectable="false"
                    ></flowdetail>
                </b-card>
            </b-col>
        </b-row>
        <br />
        <b-row v-if="flow.config.params.length !== 0">
            <b-col>
                <b-card
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="default"
                >
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h4>
                                    Params
                                </h4>
                            </b-col>
                        </b-row>
                    </template>
                    <b-card
                        border-variant="white"
                        footer-bg-variant="white"
                        sub-title="Configure parameters."
                    >
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
                                {{ param.item.key.toLowerCase() }}
                            </template>
                            <template v-slot:cell(value)="param">
                                <b-form-input
                                    size="sm"
                                    v-model="param.item.value"
                                    :placeholder="
                                        'Enter a value for \'' +
                                            param.item.key.toLowerCase() +
                                            '\''
                                    "
                                ></b-form-input>
                            </template>
                        </b-table>
                    </b-card>
                </b-card>
                <br />
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
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h4>
                                    Input
                                </h4>
                            </b-col>
                        </b-row>
                    </template>
                    <runinput
                        :user="user"
                        :kind="flow.config.from"
                        v-on:inputSelected="onInputSelected"
                    ></runinput>
                </b-card>
                <br />
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
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h4>
                                    Output
                                </h4>
                            </b-col>
                        </b-row>
                    </template>
                    <runoutput
                        :user="user"
                        v-on:outputSelected="onOutputSelected"
                     :kind="output.kind"></runoutput>
                </b-card>
                <br />
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
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h4>
                                    Target
                                </h4>
                            </b-col>
                        </b-row>
                    </template>
                    <runtarget
                        :selected="target"
                        v-on:targetSelected="onTargetSelected"
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
                files: []
            },
            output: null,
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
        // TODO load workflows
        // Workflows.get(this.owner, this.name).then(pipeline => {
        //     this.workflow = pipeline;
        //     if (pipeline.config.params != null) {
        //         this.params = pipeline.config.params.map(function(param) {
        //             return {
        //                 key: param,
        //                 value: ''
        //             };
        //         });
        //     }
        // });
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
                    this.params = response.data['config']['params'].map(
                        param => {
                            return {
                                key: param,
                                value: ''
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
        onInputSelected(input) {
            this.input = input;
        },
        onOutputSelected(output) {
            this.output = output;
        },
        onTargetSelected(target) {
            this.target = target;
        },
        onStart() {
            this.params['config'] = {};
            this.params['config']['api_url'] = '/apis/v1/runs/status/';
            axios({
                method: 'post',
                url: `/apis/v1/runs/`,
                data: {
                    repository: this.flow.repository,
                    config: {
                        name: this.flow.config.name,
                        image: this.flow.config.image,
                        clone: this.flow.config.clone,
                        input: this.input
                            ? {
                                  kind: this.input.kind,
                                  path: this.input.path
                              }
                            : null,
                        output: this.output
                            ? {
                                  kind: this.output.kind,
                                  path: this.output.path
                              }
                            : null,
                        params: this.params,
                        target: this.target,
                        commands: this.flow.config.commands
                    }
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
