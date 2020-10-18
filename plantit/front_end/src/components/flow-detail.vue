<template>
    <div v-if="workflow.config">
        <b-img
            v-if="workflow.config.logo"
            rounded="circle"
            class="card-img-right"
            style="max-width: 10rem;opacity: 0.8;position: absolute;right: 20px;top: 20px;z-index:1"
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
                        <h2>
                            {{ workflow.config.name }}
                        </h2>
                    </b-col>
                    <b-col class="ml-0 pl-0" v-if="showPublic">
                        <h5>
                            <b-badge
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
                                class="text-dark"
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
                <hr />
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
                                    <b-col cols="11">
                                        <b>{{ workflow.config.author }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Clone</small>
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{
                                            workflow.config.clone ? 'Yes' : 'No'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>Image</small>
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{ workflow.config.image }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <small>From</small>
                                    </b-col>
                                    <b-col cols="11">
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
                                    <b-col cols="11">
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
                                    <b-col cols="11">
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
                                    <b-col cols="11">
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
    methods: {
        workflowSelected: function(workflow) {
            this.$emit('flowSelected', workflow);
        }
    }
};
</script>

<style scoped></style>
