<template>
    <div
        v-if="workflow.config"
        :class="darkMode ? 'theme-dark' : 'theme-light'"
    >
        <b-img
            v-if="workflow.config.logo"
            rounded="circle"
            class="card-img-right"
            style="max-width: 10rem;position: absolute;right: 20px;top: 20px;z-index:1"
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
                        <h2 :class="darkMode ? 'text-white' : 'text-dark'">
                            {{ workflow.config.name }}
                        </h2>
                    </b-col>
                    <b-col class="ml-0 pl-0" v-if="showPublic">
                        <h5 :class="darkMode ? 'text-white' : 'text-dark'">
                            <b-badge variant="white" class="mr-2"
                                ><i class="fas fa-stream fa-1x fa-fw"></i>
                                Flow</b-badge
                            >
                            <b-badge
                                class="mr-2"
                                :variant="
                                    workflow.config.public
                                        ? 'success'
                                        : 'warning'
                                "
                                >{{
                                    workflow.config.public
                                        ? 'Public'
                                        : 'Private'
                                }}</b-badge
                            >
                        </h5>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <small>
                            <b-link
                                :class="darkMode ? 'text-warning' : 'text-dark'"
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
                <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                <b-row>
                    <b-col>
                        <b-row>
                            <b-col>
                                {{ workflow.repo.description }}
                            </b-col>
                        </b-row>
                        <br />
                        <b-row>
                            <b-col>
                                <b-row>
                                    <b-col>
                                        <small>Author</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{ workflow.config.author }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Clone</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            workflow.config.clone ? 'Yes' : 'No'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Image</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{ workflow.config.image }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>From</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            workflow.config.from
                                                ? workflow.config.from.capitalize()
                                                : 'None'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>To</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            workflow.config.to
                                                ? workflow.config.to.capitalize()
                                                : 'None'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Parameters</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            workflow.config.params
                                                ? workflow.config.params.length
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
                                                ' ' + workflow.config.commands
                                            }}</code></b
                                        >
                                    </b-col>
                                </b-row>
                                <b-row v-if="selectable">
                                    <b-col>
                                        <br />
                                        <br />
                                        <b-button
                                            block
                                            class="text-left"
                                            variant="success"
                                            v-b-tooltip.hover
                                            @click="workflowSelected(workflow)"
                                        >
                                            <i class="fas fa-terminal"></i>
                                            Run
                                        </b-button>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-col>
                </b-row>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'flow-detail',
    props: {
        showPublic: {
            type: Boolean,
            required: true
        },
        workflow: {
            type: Object,
            required: true
        },
        selectable: {
            type: Boolean,
            required: true
        }
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
            'loggedIn',
            'darkMode'
        ])
    },
    methods: {
        workflowSelected: function(workflow) {
            this.$emit('flowSelected', workflow);
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
