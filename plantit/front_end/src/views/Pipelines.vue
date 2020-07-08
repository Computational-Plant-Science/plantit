<template>
    <div class="w-100 p-4">
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="dark"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h2>
                            Community Pipelines
                        </h2>
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
                <b-row align-h="center" v-if="community_pipelines_loading">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="dark"
                    ></b-spinner>
                </b-row>
                <div
                    v-if="
                        !community_pipelines_loading &&
                            filtered_community_pipelines.length === 0
                    "
                >
                    None to show.
                </div>
                <b-card-group deck columns>
                    <b-card
                        no-body
                        v-for="pipeline in filtered_community_pipelines"
                        :key="pipeline.repo.name"
                        class="overflow-hidden p-0 m-4"
                        style="min-width: 35rem"
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="white"
                        footer-border-variant="white"
                        header-border-variant="dark"
                    >
                        <template slot="header">
                            <b-row align-v="center">
                                <b-col>
                                    <h3>{{ pipeline.config.name }}</h3>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>
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
                                    </small>
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
                                            <small>
                                                <b>Author:</b>
                                                {{ pipeline.config.author }}
                                                <br />
                                                <b>Image:</b>
                                                {{ pipeline.config.image }}
                                                <br />
                                                <b>Clone:</b>
                                                {{
                                                    pipeline.config.clone
                                                        ? 'Yes'
                                                        : 'No'
                                                }}
                                                <br />
                                                <b>Parameters:</b>
                                                {{
                                                    pipeline.config.params
                                                        ? pipeline.config.params
                                                              .length
                                                        : 'None'
                                                }}
                                                <br />
                                                <b>Input:</b>
                                                {{
                                                    pipeline.config.input
                                                        ? pipeline.config.input.capitalize()
                                                        : 'None'
                                                }}
                                                <br />
                                                <b>Output:</b>
                                                {{
                                                    pipeline.config.output
                                                        ? pipeline.config.output.capitalize()
                                                        : 'None'
                                                }}
                                            </small>
                                            <br />
                                            <br />
                                            <b-button
                                                block
                                                class="text-left"
                                                variant="success"
                                                v-b-tooltip.hover
                                                @click="
                                                    pipelineSelected(pipeline)
                                                "
                                            >
                                                <i class="fas fa-terminal"></i>
                                                Run
                                            </b-button>
                                        </b-card-body>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-card-group>
            </b-row>
        </b-card>
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="dark"
            class="mt-3"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h3>
                            Your Pipelines
                        </h3>
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
                <b-row align-h="center" v-if="user_pipelines_loading">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="dark"
                    ></b-spinner>
                </b-row>
                <div
                    v-if="
                        !user_pipelines_loading &&
                            filtered_user_pipelines.length === 0
                    "
                >
                    None to show.
                </div>
                <b-card-group deck columns>
                    <b-card
                        v-for="pipeline in filtered_user_pipelines"
                        :key="pipeline.repo.name"
                        class="overflow-hidden p-0 m-4"
                        style="min-width: 35rem"
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="white"
                        footer-border-variant="white"
                        header-border-variant="dark"
                    >
                        <template slot="header">
                            <b-row align-v="center">
                                <b-col>
                                    <h3>{{ pipeline.config.name }}</h3>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>
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
                                    </small>
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
                                            <small>
                                                <b>Author:</b>
                                                {{ pipeline.config.author }}
                                                <br />
                                                <b>Image:</b>
                                                {{ pipeline.config.image }}
                                                <br />
                                                <b>Clone:</b>
                                                {{
                                                    pipeline.config.clone
                                                        ? 'Yes'
                                                        : 'No'
                                                }}
                                                <br />
                                                <b>Parameters:</b>
                                                {{
                                                    pipeline.config.params
                                                        ? pipeline.config.params
                                                              .length
                                                        : 'None'
                                                }}
                                                <br />
                                                <b>Input:</b>
                                                {{
                                                    pipeline.config.input
                                                        ? pipeline.config.input.capitalize()
                                                        : 'None'
                                                }}
                                                <br />
                                                <b>Output:</b>
                                                {{
                                                    pipeline.config.output
                                                        ? pipeline.config.output.capitalize()
                                                        : 'None'
                                                }}
                                            </small>
                                            <br />
                                            <br />
                                            <b-button
                                                block
                                                class="text-left"
                                                variant="success"
                                                v-b-tooltip.hover
                                                @click="
                                                    pipelineSelected(pipeline)
                                                "
                                            >
                                                <i class="fas fa-terminal"></i>
                                                Run
                                            </b-button>
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

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'Pipelines',
    components: {},
    data: function() {
        return {
            community_pipelines_loading: false,
            user_pipelines_loading: false,
            filter_community_pipelines_query: '',
            filter_user_pipelines_query: '',
            community_pipelines: [],
            user_pipelines: []
        };
    },
    mounted: function() {
        this.loadCommunityPipelines();
        this.loadUserPipelines();
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
        loadCommunityPipelines() {
            this.community_pipelines_loading = true;
            Pipelines.list().then(data => {
                this.community_pipelines = data.pipelines || [];
                this.community_pipelines_loading = false;
            });
        },
        loadUserPipelines() {
            this.user_pipelines_loading = true;
            Users.getCurrentUserGithubRepos().then(pipelines => {
                if (pipelines == null) {
                    this.user_pipelines = [];
                } else {
                    this.user_pipelines = pipelines;
                }
                this.user_pipelines_loading = false;
            });
        },
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
