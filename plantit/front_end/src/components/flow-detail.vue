<template>
    <div
        v-if="flow && flow.config"
        :class="darkMode ? 'theme-dark' : 'theme-light'"
    >
        <b-img
            v-if="flow.config.logo"
            rounded="circle"
            class="card-img-right"
            style="max-width: 18rem;position: absolute;right: 20px;top: 20px;z-index:1"
            right
            :src="
                `https://raw.githubusercontent.com/${flow.repo.owner.login}/${flow.repo.name}/master/${flow.config.logo}`
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
                        <b-badge
                            class="mr-1"
                            :variant="
                                flow.config.public ? 'success' : 'warning'
                            "
                            >{{
                                flow.config.public ? 'Public' : 'Private'
                            }}</b-badge
                        >
                        <h1 :class="darkMode ? 'text-white' : 'text-dark'">
                            {{ flow.config.name }}
                        </h1>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <small>
                            <b-link
                                :class="darkMode ? 'text-warning' : 'text-dark'"
                                :href="
                                    'https://github.com/' +
                                        flow.repo.owner.login +
                                        '/' +
                                        flow.repo.name
                                "
                            >
                                <i class="fab fa-github fa-fw"></i>
                                {{ flow.repo.owner.login }}/{{ flow.repo.name }}
                            </b-link>
                        </small>
                    </b-col>
                </b-row>
                <hr :class="darkMode ? 'theme-dark' : 'theme-light'" />
                <b-row>
                    <b-col>
                        <b-row>
                            <b-col>
                                {{ flow.repo.description }}
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
                                        <b>{{ flow.config.author }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Clone</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            flow.config.clone ? 'Yes' : 'No'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Image</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{ flow.config.image }}</b>
                                    </b-col>
                                </b-row>
                                <b-row v-if="flow.config.mount !== undefined">
                                    <b-col>
                                        <small>Mount</small>
                                    </b-col>
                                    <b-col cols="10">
                                        {{
                                            flow.config.mount
                                                ? flow.config.mount
                                                : 'None'
                                        }}
                                    </b-col>
                                </b-row>
                                <!--<b-row>
                                    <b-col>
                                        <small>From</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            flow.config.from
                                                ? flow.config.from.capitalize()
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
                                            flow.config.to
                                                ? flow.config.to.capitalize()
                                                : 'None'
                                        }}</b>
                                    </b-col>
                                </b-row>-->
                                <b-row>
                                    <b-col>
                                        <small>Parameters</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b>{{
                                            flow.config.params
                                                ? flow.config.params.length
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
                                                ' ' + flow.config.commands
                                            }}</code></b
                                        >
                                    </b-col>
                                </b-row>
                              <b-row v-if="flow.config.input !== undefined">
                                    <b-col>
                                        <small>Input</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b
                                            >{{
                                                flow.config.input.kind[0].toUpperCase() + flow.config.input.kind.substr(1)
                                          }} <code>{{ flow.config.input.patterns ? '[' + (flow.config.input.patterns ? '*.' + flow.config.input.patterns.join(', *.') : []) + ']' : '' }}</code></b
                                        >
                                    </b-col>
                                </b-row>
                              <b-row v-if="flow.config.output !== undefined">
                                    <b-col>
                                        <small>Output</small>
                                    </b-col>
                                    <b-col cols="10">
                                        <b
                                            ><code>[working directory]/{{
                                                flow.config.output.path ? flow.config.output.path + '/' : ''
                                            }}{{ flow.config.output.include ? '[+ ' + (flow.config.output.include.patterns ? '*.' + flow.config.output.include.patterns.join(', *.') : []) + (flow.config.output.include.names ? flow.config.output.include.names.join(', ') : []) + ']' : '' }}{{ flow.config.output.exclude ? '[- ' + (flow.config.output.exclude.patterns ? '*.' + flow.config.output.include.patterns.join(', *.') : []) + (flow.config.output.include.names ? flow.config.output.exclude.names.join(', ') : []) + ']' : '' }}
                                        </code></b
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
                                            @click="flowSelected(flow)"
                                        >
                                            <i class="fas fa-terminal"></i>
                                            Run
                                        </b-button>
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-col>
                    <b-col
                        align-self="end"
                        md="auto"
                        class="text-right"
                        v-if="!flow.config.resources"
                    >
                        <b-alert show variant="warning"
                            >This flow does not specify cluster resources and
                            can only be run in the <b>Sandbox</b>.</b-alert
                        >
                    </b-col>
                    <b-col align-self="end" class="text-left" v-else>
                        <b>Cluster Resources</b>
                        <br />
                        <br />
                        <b-row align-v="right" align-h="right">
                            <b-col>
                                <b
                                    ><code>{{
                                        ' ' + flow.config.resources.time
                                    }}</code></b
                                >
                                <small> time</small>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                <b
                                    ><code>{{
                                        ' ' + flow.config.resources.mem
                                    }}</code></b
                                >
                                <small> memory</small>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                <b
                                    ><code>{{
                                        ' ' + flow.config.resources.tasks
                                    }}</code></b
                                >
                                <small> task(s)</small>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                <b
                                    ><code>{{
                                        ' ' + flow.config.resources.cores
                                    }}</code></b
                                >
                                <small> core(s)</small>
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
        flow: {
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
        flowSelected: function(flow) {
            this.$emit('flowSelected', flow);
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
