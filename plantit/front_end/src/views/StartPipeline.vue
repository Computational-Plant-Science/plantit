<template>
    <div class="w-100 p-4">
        <b-card
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            border-variant="white"
            footer-border-variant="white"
            header-border-variant="dark"
            class="mb-4"
        >
            <template slot="header">
                <b-row align-v="center">
                    <b-col>
                        <h2>{{ pipeline.config.name }}</h2>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <b-link
                            class="text-secondary"
                            :href="
                                'https://github.com/' +
                                    pipeline.repo.owner.login +
                                    '/' +
                                    pipeline.repo.name
                            "
                        >
                            {{ pipeline.repo.owner.login }}/{{
                                pipeline.repo.name
                            }}
                        </b-link>
                    </b-col>
                </b-row>
            </template>
            <b-row no-gutters>
                <b-col
                    md="auto"
                    style="min-width: 8em; max-width: 8rem; min-height: 8rem; max-height: 8rem"
                >
                    <b-img
                        v-if="pipeline.icon_url"
                        style="max-width: 8rem"
                        :src="pipeline.icon_url"
                        right
                    >
                    </b-img>
                    <b-img
                        v-else
                        style="max-width: 8rem"
                        :src="require('../assets/logo.png')"
                        right
                    ></b-img>
                </b-col>
                <b-col>
                    <b-card-body>
                        <b-row>
                            <b-col>
                                {{ pipeline.repo.description }}
                            </b-col>
                        </b-row>
                        <br />
                        <br />
                        <b-row>
                            <b-col>
                                Author:
                            </b-col>
                            <b-col cols="11">
                                <b>{{ pipeline.config.author }}</b>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                Image:
                            </b-col>
                            <b-col cols="11">
                                <b>{{ pipeline.config.image }}</b>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                Clone:
                            </b-col>
                            <b-col cols="11">
                                <b>{{
                                    pipeline.config.clone ? 'Yes' : 'No'
                                }}</b>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                Parameters:
                            </b-col>
                            <b-col cols="11">
                                <b>{{
                                    params.length === 0 ? 'None' : params.length
                                }}</b>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                Input:
                            </b-col>
                            <b-col cols="11">
                                <b>{{
                                    pipeline.config.input
                                        ? pipeline.config.input.capitalize()
                                        : 'None'
                                }}</b>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                Output:
                            </b-col>
                            <b-col cols="11">
                                <b>{{
                                    pipeline.config.output
                                        ? pipeline.config.output.capitalize()
                                        : 'None'
                                }}</b>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                Command:
                            </b-col>
                            <b-col cols="11">
                                <b
                                    ><code>{{
                                        ' ' + pipeline.config.commands
                                    }}</code></b
                                >
                            </b-col>
                        </b-row>
                    </b-card-body>
                </b-col>
            </b-row>
        </b-card>
        <b-card
            v-if="params.length !== 0"
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            border-variant="white"
            footer-border-variant="white"
            header-border-variant="dark"
            class="mb-4"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Parameters
                        </h5>
                    </b-col>
                </b-row>
            </template>
            <b-card-body>
                <EditParameters :params="params"></EditParameters>
            </b-card-body>
            <!--<b-card-body>
                <vue-json-editor v-model="params" :show-btns="true" :expandedOnStart="true" @json-change="onJsonChange"></vue-json-editor>
            </b-card-body>-->
        </b-card>
        <b-card
            v-if="pipeline.config.input"
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            border-variant="white"
            footer-border-variant="white"
            header-border-variant="dark"
            class="mb-4"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h4>
                            Input
                            <b>{{ pipeline.config.input.capitalize() }}</b>
                            <i
                                class="fas fa-check ml-2 success"
                                v-if="input.files.length !== 0"
                            ></i>
                        </h4>
                    </b-col>
                    <b-col class="mt-2" md="auto" style="color: white">
                        <h5>
                            iRODS Path:
                            <b>{{ input.path ? input.path : 'None' }}</b>
                        </h5>
                    </b-col>
                    <b-col class="mt-2" md="auto" style="color: white">
                        <h5>
                            iRODS File Count: <b>{{ input.files.length }}</b>
                        </h5>
                    </b-col>
                </b-row>
            </template>
            <b-card-body>
                <EditInput
                    :user="user"
                    v-on:inputSelected="onInputSelected"
                ></EditInput>
            </b-card-body>
        </b-card>
        <b-card
            v-if="pipeline.config.output"
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            border-variant="white"
            footer-border-variant="white"
            header-border-variant="dark"
            class="mb-4"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h4>
                            Output
                            <b>{{ pipeline.config.output.capitalize() }}</b>
                            <i
                                class="fas fa-check ml-2 success"
                                v-if="
                                    output.local_path !== null &&
                                        output.local_path !== '' &&
                                        output.irods_path !== null &&
                                        output.irods_path !== ''
                                "
                            ></i>
                        </h4>
                    </b-col>
                    <b-col md="auto" class="mt-2" style="color: white">
                        <h5>
                            Local Path:
                            <b>{{
                                output.local_path ? output.local_path : 'None'
                            }}</b>
                        </h5>
                    </b-col>
                    <b-col class="mt-2" md="auto" style="color: white">
                        <h5>
                            iRODS Path:
                            <b>{{
                                output.irods_path ? output.irods_path : 'None'
                            }}</b>
                        </h5>
                    </b-col>
                </b-row>
            </template>
            <b-card-body>
                <EditOutput
                    :user="user"
                    v-on:outputSelected="onOutputSelected"
                ></EditOutput>
            </b-card-body>
        </b-card>
        <b-card
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            border-variant="white"
            footer-border-variant="white"
            header-border-variant="dark"
            class="mb-4"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h3>
                            Deployment <b>Target</b>
                            <i
                                class="fas fa-check ml-2 success"
                                v-if="
                                    target.name !== null && target.name !== ''
                                "
                            ></i>
                        </h3>
                    </b-col>
                    <b-col md="auto" class="mt-2" style="color: white">
                        <h5>
                            <h5>Target: <b>{{ target.name }}</b></h5>
                        </h5>
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
        <b-row>
            <b-col>
                <b-button @click="onStart" variant="success" block>
                    Start
                </b-button>
            </b-col>
        </b-row>
    </div>
    <!--<NewCollection>

        </NewCollection>
        <SelectCollection
            class="pb-4"
            selectable="true"
            filterable="true"
            per-page="4"
            v-on:selected="onSelected"
        ></SelectCollection>
        <SetParameters
            class="pb-4"
            :workflow_name="this.name"
            v-on:submit="onSubmit"
        ></SetParameters>-->
</template>

<script>
import EditParameters from '../components/EditParameters';
import EditInput from '../components/EditInput';
import EditOutput from '../components/EditOutput';
import SelectTarget from '../components/SelectTarget';
import Pipelines from '@/services/apiV1/PipelineManager';
import Users from '@/services/apiV1/UserManager';
import router from '../router';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'StartPipeline',
    components: {
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
            user: null,
            pipeline: null,
            params: [],
            input: {
                files: []
            },
            output: {
                local_path: null,
                irods_path: null
            },
            target: {
                name: null
            }
        };
    },
    mounted: function() {
        Users.getCurrentUser().then(user => {
            this.user = user;
        });
        Pipelines.get(this.owner, this.name).then(pipeline => {
            this.pipeline = pipeline;
            if (pipeline.config.params != null) {
                this.params = pipeline.config.params.map(function(param) {
                    return {
                        key: param,
                        value: ''
                    };
                });
            }
        });
    },
    methods: {
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
            Pipelines.start(this.owner, this.name, {
                input: this.input,
                target: this.target
            }).then(result => {
                router.push({
                    name: 'run',
                    params: {
                        id: result.id
                    }
                });
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.success
    color: $success

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

.pipeline-text
    background-color: $dark
    padding: 10px
</style>
