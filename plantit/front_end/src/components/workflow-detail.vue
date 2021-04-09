<template>
    <div
        v-if="workflow && workflow.config"
        :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
    >
        <b-img
            v-if="workflow.config.logo"
            rounded
            class="card-img-right"
            style="max-width: 12rem;position: absolute;right: 20px;top: 20px;z-index:1"
            right
            :src="
                `https://raw.githubusercontent.com/${workflow.repo.owner.login}/${workflow.repo.name}/master/${workflow.config.logo}`
            "
        ></b-img>
        <b-img
            v-else
            class="card-img-left"
            style="max-width: 7rem"
            right
            :src="require('../assets/logo.png')"
        ></b-img>
        <b-row no-gutters>
            <b-col>
                <b-row>
                    <b-col md="auto" class="mr-0">
                        <h2
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                        >
                            {{ workflow.config.name }}
                        </h2>
                        <b-badge
                            class="mr-1"
                            :variant="
                                workflow.config.public ? 'success' : 'warning'
                            "
                            >{{
                                workflow.config.public ? 'Public' : 'Private'
                            }}</b-badge
                        ><b-badge
                            v-for="topic in workflow.repo.topics"
                            v-bind:key="topic"
                            class="mr-1"
                            variant="secondary"
                            >{{ topic }}</b-badge
                        >
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <small>
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                :href="
                                    'https://github.com/' +
                                        workflow.repo.owner.login +
                                        '/' +
                                        workflow.repo.name
                                "
                            >
                                <i class="fab fa-github fa-fw"></i>
                                {{ workflow.repo.owner.login }}/{{
                                    workflow.repo.name
                                }}
                            </b-link>
                        </small>
                    </b-col>
                </b-row>
                <br />
                <b-row>
                    <b-col>
                        <b-row>
                            <b-col>
                                {{ workflow.repo.description }}
                            </b-col>
                        </b-row>
                        <br />
                        <div
                            v-if="
                                workflow.config.author !== undefined &&
                                    workflow.config.author !== null
                            "
                        >
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Authors
                            </h5>
                            <b-row>
                                <b-col>
                                    <b-row
                                        v-if="
                                            workflow.config.author !== undefined
                                        "
                                    >
                                        <b-col>
                                            <span
                                                v-if="
                                                    typeof workflow.config
                                                        .author === 'string' ||
                                                        (Array.isArray(
                                                            workflow.config
                                                                .author
                                                        ) &&
                                                            workflow.config
                                                                .author
                                                                .length === 1)
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                >{{
                                                    workflow.config.author
                                                }}</span
                                            >
                                            <b-list-group v-else>
                                                <b-list-group-item
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'dark'
                                                            : 'light'
                                                    "
                                                    v-for="author in workflow
                                                        .config.author"
                                                    v-bind:key="author"
                                                    >{{
                                                        author
                                                    }}</b-list-group-item
                                                >
                                            </b-list-group>
                                        </b-col>
                                    </b-row>
                                </b-col>
                            </b-row>
                        </div>
                        <div
                            v-if="
                                workflow.config.doi !== undefined &&
                                    workflow.config.doi !== null
                            "
                        >
                            <br />
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Publications/DOIs
                            </h5>
                            <b-row>
                                <b-col>
                                    <b-row
                                        v-if="workflow.config.doi !== undefined"
                                    >
                                        <b-col>
                                            <b-link
                                                v-if="
                                                    typeof workflow.config
                                                        .doi === 'string' ||
                                                        (Array.isArray(
                                                            workflow.config.doi
                                                        ) &&
                                                            workflow.config.doi
                                                                .length === 1)
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :href="
                                                    `https://doi.org/${workflow.config.doi}`
                                                "
                                                >{{
                                                    workflow.config.doi
                                                }}</b-link
                                            >
                                            <b-list-group v-else>
                                                <b-list-group-item
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'dark'
                                                            : 'light'
                                                    "
                                                    v-for="doi in workflow
                                                        .config.doi"
                                                    v-bind:key="doi"
                                                    ><b-link
                                                        class="
                                                        text-dark
                                                    "
                                                        :href="
                                                            `https://doi.org/${doi}`
                                                        "
                                                        >{{ doi }}</b-link
                                                    ></b-list-group-item
                                                >
                                            </b-list-group>
                                        </b-col>
                                    </b-row>
                                </b-col>
                            </b-row>
                        </div>
                        <br />
                        <b-tabs
                            content-class="mt-3"
                            nav-class="bg-transparent"
                            active-nav-item-class="bg-secondary text-dark"
                        >
                            <b-tab
                                active
                                title="Configuration"
                                :title-link-class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                            >
                                <b-row>
                                    <b-col>
                                        <b-row>
                                            <b-col>
                                                <small>Image</small>
                                            </b-col>
                                            <b-col cols="10">
                                                <b>{{
                                                    workflow.config.image
                                                }}</b>
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col>
                                                <small>GPU</small>
                                            </b-col>
                                            <b-col cols="10">
                                                {{
                                                    workflow.config.gpu
                                                        ? 'Yes'
                                                        : 'No'
                                                }}
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col>
                                                <small>Mount</small>
                                            </b-col>
                                            <b-col cols="10">
                                                {{
                                                    workflow.config.mount
                                                        ? workflow.config.mount
                                                        : 'None'
                                                }}
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col>
                                                <small>Parameters</small>
                                            </b-col>
                                            <b-col cols="10">
                                                <b>{{
                                                    workflow.config.params
                                                        ? workflow.config.params
                                                              .length
                                                        : 'None'
                                                }}</b>
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col>
                                                <small>Command</small>
                                            </b-col>
                                            <b-col cols="10">
                                                <b
                                                    ><code>{{
                                                        ' ' +
                                                            workflow.config
                                                                .commands
                                                    }}</code></b
                                                >
                                            </b-col>
                                        </b-row>
                                        <b-row
                                            v-if="
                                                workflow.config.input !==
                                                    undefined
                                            "
                                        >
                                            <b-col>
                                                <small>Input</small>
                                            </b-col>
                                            <b-col cols="10">
                                                <b
                                                    ><code
                                                        >[working
                                                        directory]/input/{{
                                                            workflow.config
                                                                .input.filetypes
                                                                ? '[' +
                                                                  (workflow
                                                                      .config
                                                                      .input
                                                                      .filetypes
                                                                      ? '*.' +
                                                                        workflow.config.input.filetypes.join(
                                                                            ', *.'
                                                                        )
                                                                      : []) +
                                                                  ']'
                                                                : ''
                                                        }}</code
                                                    ></b
                                                >
                                            </b-col>
                                        </b-row>
                                        <b-row
                                            v-if="
                                                workflow.config.output !==
                                                    undefined
                                            "
                                        >
                                            <b-col>
                                                <small>Output</small>
                                            </b-col>
                                            <b-col cols="10">
                                                <b
                                                    ><code
                                                        >[working directory]/{{
                                                            workflow.config
                                                                .output.path
                                                                ? workflow
                                                                      .config
                                                                      .output
                                                                      .path +
                                                                  '/'
                                                                : ''
                                                        }}{{
                                                            workflow.config
                                                                .output.include
                                                                ? '[' +
                                                                  (workflow
                                                                      .config
                                                                      .output
                                                                      .exclude
                                                                      ? '+ '
                                                                      : '') +
                                                                  (workflow
                                                                      .config
                                                                      .output
                                                                      .include
                                                                      .patterns
                                                                      ? '*.' +
                                                                        workflow.config.output.include.patterns.join(
                                                                            ', *.'
                                                                        )
                                                                      : []) +
                                                                  (workflow
                                                                      .config
                                                                      .output
                                                                      .include
                                                                      .names
                                                                      ? ', ' +
                                                                        workflow.config.output.include.names.join(
                                                                            ', '
                                                                        )
                                                                      : [])
                                                                : ''
                                                        }}{{
                                                            workflow.config
                                                                .output.exclude
                                                                ? ' - ' +
                                                                  (workflow
                                                                      .config
                                                                      .output
                                                                      .exclude
                                                                      .patterns
                                                                      ? '*.' +
                                                                        workflow.config.output.exclude.patterns.join(
                                                                            ', *.'
                                                                        )
                                                                      : []) +
                                                                  (workflow
                                                                      .config
                                                                      .output
                                                                      .exclude
                                                                      .names
                                                                      ? ', ' +
                                                                        workflow.config.output.exclude.names.join(
                                                                            ', '
                                                                        )
                                                                      : [])
                                                                : '' + ']'
                                                        }}
                                                    </code></b
                                                >
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                                <hr />
                                <b-row>
                                    <b-col
                                        align-self="end"
                                        md="auto"
                                        class="text-right"
                                        v-if="!workflow.config.resources"
                                    >
                                        <b-alert show variant="warning"
                                            >This workflow does not specify
                                            cluster resources and can only be
                                            run in the <b>Sandbox</b>.</b-alert
                                        >
                                    </b-col>
                                    <b-col
                                        align-self="end"
                                        class="text-left"
                                        v-else
                                    >
                                        <b-row>
                                            <b-col>
                                                <b
                                                    ><code>{{
                                                        ' ' +
                                                            workflow.config
                                                                .resources.time
                                                    }}</code></b
                                                >
                                                <small> time</small>
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col>
                                                <b
                                                    ><code>{{
                                                        ' ' +
                                                            workflow.config
                                                                .resources.mem
                                                    }}</code></b
                                                >
                                                <small> memory</small>
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col>
                                                <b
                                                    ><code>{{
                                                        ' ' +
                                                            workflow.config
                                                                .resources
                                                                .processes
                                                    }}</code></b
                                                >
                                                <small> process(es)</small>
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col>
                                                <b
                                                    ><code>{{
                                                        ' ' +
                                                            workflow.config
                                                                .resources.cores
                                                    }}</code></b
                                                >
                                                <small> core(s)</small>
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                            </b-tab>
                            <b-tab
                                v-if="
                                        workflow.readme !== undefined &&
                                            workflow.readme !== null
                                    "
                                title="README"
                                :title-link-class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                            >
                                <div
                                    v-if="
                                        workflow.readme !== undefined &&
                                            workflow.readme !== null
                                    "
                                >
                                    <div
                                        :class="
                                            profile.darkMode
                                                ? 'theme-container-readme m-0 p-3'
                                                : 'theme-container-light m-0 p-3'
                                        "
                                    >
                                        <br />
                                        <b-row>
                                            <b-col
                                                ><vue-markdown>{{
                                                    workflow.readme
                                                }}</vue-markdown></b-col
                                            >
                                        </b-row>
                                    </div>
                                </div>
                            </b-tab>
                        </b-tabs>
                    </b-col>
                </b-row>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import VueMarkdown from 'vue-markdown';

export default {
    name: 'workflow-detail',
    components: {
        VueMarkdown
    },
    props: {
        showPublic: {
            type: Boolean,
            required: true
        },
        workflow: {
            type: Object,
            required: true
        }
    },
    computed: {
        ...mapGetters('user', ['profile'])
    },
    methods: {
        workflowSelected: function(workflow) {
            this.$emit('workflowSelected', workflow);
        }
    }
};
</script>
<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.flow-icon
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
