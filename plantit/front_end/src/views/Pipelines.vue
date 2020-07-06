<template>
    <div class="w-100 p-4">
        <p>
            Select a
            <b-badge variant="white"
                ><i class="fas fa-stream text-dark"></i> Pipeline</b-badge
            >
            to start a new
            <b-badge variant="white"
                ><i class="fas fa-terminal text-dark"></i> Run</b-badge
            >.
        </p>
        <b-card header-bg-variant="white" border-variant="white">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Community Pipelines
                        </h5>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="filter_community_pipelines_query"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="
                                        !filter_community_pipelines_query
                                    "
                                    @click="
                                        filter_community_pipelines_query = ''
                                    "
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <div v-if="!filtered_community_pipelines.length">
                    None to show.
                </div>
                <b-card-group deck>
                    <b-card
                        v-for="workflow in filtered_community_pipelines"
                        :key="workflow.repo.name"
                        class="overflow-hidden p-0 m-2"
                        style="min-width: 30rem"
                        bg-variant="white"
                        header-bg-variant="white"
                    >
                        <template slot="header">
                            <b-row>
                                <b-col>
                                    <h3>{{ workflow.repo.name }}</h3>
                                </b-col>
                                <b-col md="auto">
                                    <b-button
                                        block
                                        variant="outline-dark"
                                        title="Start a new job"
                                        v-b-tooltip.hover
                                        @click="pipelineSelected(workflow)"
                                    >
                                        <i class="fas fa-terminal"></i>
                                    </b-button>
                                </b-col>
                            </b-row>
                        </template>
                        <b-row no-gutters>
                            <b-col
                                md="auto"
                                style="min-width: 8em; max-width: 8rem; min-height: 8rem; max-height: 8rem"
                            >
                                <b-img
                                    v-if="workflow.icon_url"
                                    style="max-width: 8rem"
                                    :src="workflow.icon_url"
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
                                <b-row>
                                    <b-col>
                                        <b-card-body>
                                            {{ workflow.repo.description }}
                                        </b-card-body>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-card-group>
            </b-row>
        </b-card>
        <b-card header-bg-variant="white" border-variant="white" class="mt-3">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            Your Pipelines
                        </h5>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="filter_user_pipelines_query"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!filter_user_pipelines_query"
                                    @click="filter_user_pipelines_query = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <b-row align-h="center">
                <div v-if="!filtered_user_pipelines.length">
                    None to show.
                </div>
                <b-card-group deck class="pl-3 pr-3">
                    <b-card
                        v-for="pipeline in filtered_user_pipelines"
                        :key="pipeline.repo.name"
                        class="overflow-hidden p-0 m-2"
                        style="min-width: 30rem"
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                    >
                        <template slot="header">
                            <b-row align-v="center">
                                <b-col>
                                    <h5>{{ pipeline.repo.name }}</h5>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>{{
                                        pipeline.repo.owner.login
                                    }}</small>
                                </b-col>
                            </b-row>
                        </template>
                        <template slot="footer">
                            <b-row>
                                <b-col></b-col>
                                <b-col md="auto">
                                    <b-button
                                        variant="outline-dark"
                                        v-b-tooltip.hover
                                        @click="pipelineSelected(pipeline)"
                                    >
                                        <i class="fas fa-terminal"></i> Run
                                    </b-button>
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
                                <b-row>
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
                                            {{
                                                pipeline.config.input
                                                    ? 'Yes'
                                                    : 'No'
                                            }}
                                            <br />
                                            <b>Output:</b>
                                            {{
                                                pipeline.config.output
                                                    ? 'Yes'
                                                    : 'No'
                                            }}
                                            <br />
                                        </b-card-body>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-card-group>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import router from '../router';
import Pipelines from '@/services/apiV1/PipelineManager';
import Users from '@/services/apiV1/UserManager.js';

export default {
    name: 'Pipelines',
    components: {},
    data: function() {
        return {
            filter_community_pipelines_query: '',
            filter_user_pipelines_query: '',
            community_pipelines: [],
            user_pipelines: []
        };
    },
    mounted: function() {
        Pipelines.list().then(data => {
            this.community_pipelines = data.workflows || [];
        });
        Users.getCurrentUserGithubRepos().then(pipelines => {
            if (pipelines == null) {
                this.user_pipelines = [];
            } else {
                this.user_pipelines = pipelines;
            }
        });
    },
    computed: {
        filter_community_pipelines_text: function() {
            return this.filter_community_pipelines_query.toLowerCase();
        },
        filter_user_pipelines_text: function() {
            return this.filter_user_pipelines_query.toLowerCase();
        },
        filtered_community_pipelines: function() {
            if (this.filter_community_pipelines_text === '') {
                return this.community_pipelines;
            } else {
                return this.community_pipelines.filter(pipeline => {
                    return (
                        pipeline.name
                            .toLowerCase()
                            .includes(this.filter_community_pipelines_text) ||
                        pipeline.description
                            .toLowerCase()
                            .includes(this.filter_community_pipelines_text)
                    );
                });
            }
        },
        filtered_user_pipelines: function() {
            if (this.filter_user_pipelines_text === '') {
                return this.user_pipelines;
            } else {
                return this.user_pipelines.filter(pipeline => {
                    return (
                        pipeline.name
                            .toLowerCase()
                            .includes(this.filter_user_pipelines_text) ||
                        pipeline.description
                            .toLowerCase()
                            .includes(this.filter_user_pipelines_text)
                    );
                });
            }
        }
    },
    methods: {
        pipelineSelected: function(pipeline) {
            router.push({
                name: 'start',
                params: {
                    owner: pipeline['repo']['owner']['login'],
                    name: pipeline['repo']['name']
                }
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button

.pipeline
    width: 300px

.pipeline-text
    background-color: $color-box-background
    padding: 10px
</style>

<style scoped lang="sass">
@import '../scss/_colors.sass'
</style>
