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
                    <WorkflowDetail
                        :show-public="
                            workflow.repo.owner.login ===
                                user.profile.github_username
                        "
                        :workflow="workflow"
                        :selectable="false"
                    ></WorkflowDetail>
                </b-card>
            </b-col>
        </b-row>
        <br />
        <b-row v-if="params.length !== 0">
            <b-col>
                <b-card
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="white"
                >
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h2>
                                    Configure <b>Parameters</b>
                                    <i
                                        class="ml-2 fas fa-exclamation text-warning"
                                        v-if="parametersUnready"
                                    ></i>
                                    <i
                                        class="ml-2 fas fa-check text-success"
                                        v-if="!parametersUnready"
                                    ></i>
                                </h2>
                            </b-col>
                        </b-row>
                    </template>
                    <EditParameters :params="params"></EditParameters>
                </b-card>
                <br />
            </b-col>
        </b-row>
        <b-row v-if="workflow && workflow.config.from">
            <b-col>
                <b-card
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="white"
                >
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h2>
                                    Configure <b>Input</b>
                                    <!--<b>{{
                                        workflow.config.from.capitalize()
                                    }}</b>-->
                                    <i
                                        class="ml-2 fas fa-exclamation text-warning"
                                        v-if="inputUnready"
                                    ></i>
                                    <i
                                        class="ml-2 fas fa-check text-success"
                                        v-if="!inputUnready"
                                    ></i>
                                </h2>
                            </b-col>
                        </b-row>
                    </template>
                    <EditInput
                        :user="user"
                        :kind="workflow.config.from"
                        v-on:inputSelected="onInputSelected"
                    ></EditInput>
                </b-card>
                <br />
            </b-col>
        </b-row>
        <b-row v-if="workflow.config && workflow.config.to">
            <b-col>
                <b-card
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="white"
                >
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h2>
                                    Configure <b>Output</b>
                                    <!--<b>{{ workflow.config.to.capitalize() }}</b>-->
                                    <i
                                        class="ml-2 fas fa-exclamation text-warning"
                                        v-if="outputUnready"
                                    ></i>
                                    <i
                                        class="ml-2 fas fa-check text-success"
                                        v-if="!outputUnready"
                                    ></i>
                                </h2>
                            </b-col>
                        </b-row>
                    </template>
                    <EditOutput
                        :user="user"
                        v-on:outputSelected="onOutputSelected"
                    ></EditOutput>
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
                    header-border-variant="white"
                >
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h2>
                                    Deployment <b>Target</b>
                                    <i
                                        class="ml-2 fas fa-exclamation text-warning"
                                        v-if="targetUnready"
                                    ></i>
                                    <i
                                        class="ml-2 fas fa-check text-success"
                                        v-if="!targetUnready"
                                    ></i>
                                </h2>
                            </b-col>
                        </b-row>
                    </template>
                    <b-card-body>
                        <SelectTarget
                            :selected="target"
                            v-on:targetSelected="onTargetSelected"
                        ></SelectTarget>
                    </b-card-body>
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
import WorkflowDetail from '../components/WorkflowDetail';
import EditParameters from '../components/RunParams';
import EditInput from '../components/RunInput';
import EditOutput from '../components/RunOutput';
import SelectTarget from '../components/RunTarget';
import { mapGetters } from 'vuex';
// import router from '../router';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'Workflow',
    components: {
        WorkflowDetail,
        EditParameters,
        EditInput,
        EditOutput,
        SelectTarget
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
            workflow: null,
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
        ...mapGetters(['currentUserDjangoProfile']),
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
