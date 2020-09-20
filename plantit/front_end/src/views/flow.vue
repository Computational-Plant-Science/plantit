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
                    <runparams :params="flow.config.params"></runparams>
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
                    ></runoutput>
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
import runparams from '../components/run-params';
import runinput from '../components/run-input';
import runoutput from '../components/run-output';
import runtarget from '../components/run-target';
import { mapGetters } from 'vuex';
import axios from 'axios';
// import router from '../router';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'flow',
    components: {
        flowdetail,
        runparams,
        runinput,
        runoutput,
        runtarget
    },
    props: {
        owner: {
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
            }
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
                .get(`/apis/v1/flows/${this.owner}/${this.name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flow = response.data;
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
            // TODO start workflow
            // Workflows.start({
            //     repo: this.workflow.repo,
            //     config: {
            //         name: this.workflow.config.name,
            //         image: this.workflow.config.image,
            //         clone: this.workflow.config.clone,
            //         input: this.input.irods_path ? this.input : null,
            //         output: this.output,
            //         params: this.params,
            //         target: this.target,
            //         commands: this.workflow.config.commands
            //     }
            // }).then(result => {
            //     router.push({
            //         name: 'run',
            //         params: {
            //             id: result.data.id
            //         }
            //     });
            // });
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
