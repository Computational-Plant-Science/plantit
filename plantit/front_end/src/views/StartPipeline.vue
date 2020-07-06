<template>
    <div class="w-100 p-4">
        <b-card
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            class="mb-4 overflow-hidden"
        >
            <template slot="header">
                <b-row align-v="center">
                    <b-col>
                        <h5>{{ pipeline.repo.name }}</h5>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <small>{{ pipeline.repo.owner.login }}</small>
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
                        {{ pipeline.repo.description }}
                        <br />
                        <br />
                        <b>Image:</b>
                        {{ pipeline.config.image }}
                        <br />
                        <b>Parameters:</b>
                        {{ pipeline.config.params.length }}
                        <br />
                        <b>Input:</b>
                        {{ pipeline.config.input ? 'Yes' : 'No' }}
                        <br />
                        <b>Output:</b>
                        {{ pipeline.config.output ? 'Yes' : 'No' }}
                        <br />
                        <b>Command:</b>
                        <code>{{ ' ' + pipeline.config.commands }}</code>
                    </b-card-body>
                </b-col>
            </b-row>
        </b-card>
        <b-card
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
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
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            class="mb-4"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Target
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
            <template v-slot:footer style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>Selected: {{ target.name }}</h5>
                    </b-col>
                </b-row>
            </template>
        </b-card>
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
import SelectTarget from '../components/SelectTarget';
import Pipelines from '@/services/apiV1/PipelineManager';

export default {
    name: 'StartPipeline',
    components: {
        EditParameters,
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
            pipeline: null,
            params: [],
            target: {
                name: 'None'
            }
        };
    },
    mounted: function() {
        Pipelines.get(this.owner, this.name).then(pipeline => {
            this.pipeline = pipeline;
            this.params = pipeline.config.params.map(function(param) {
                return {
                    key: param,
                    value: ''
                };
            });
        });
    },
    methods: {
        onTargetSelected(target) {
            this.target = target;
        }
        // onStart(values) {
        //     Pipelines.start(this.name, this.collection_pk, values).then(
        //         result => {}
        //     );
        // },
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

.pipeline-text
    background-color: $dark
    padding: 10px
</style>
