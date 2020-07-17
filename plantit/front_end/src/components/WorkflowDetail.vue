<template>
    <div v-if="workflow.config">
        <b-img
            class="card-img-left"
            v-if="workflow.icon_url"
            style="max-width: 20rem;"
            right
            :src="workflow.icon_url"
        >
        </b-img>
        <b-img
            v-else
            class="card-img-left"
            style="max-width: 30rem"
            right
            :src="require('../assets/logo.png')"
        ></b-img>
        <b-row no-gutters>
            <b-col>
                <b-row>
                    <b-col md="auto" class="mr-0">
                        <h1>
                            Workflow <b>{{ workflow.config.name }}</b>
                        </h1>
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
                                {{ workflow.repo.owner.login }}/{{
                                    workflow.repo.name
                                }}
                            </b-link>
                        </small>
                    </b-col>
                </b-row>
                <br />
                <b-card-body>
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
                                            Author:
                                        </b-col>
                                        <b-col cols="10">
                                            <b>{{ workflow.config.author }}</b>
                                        </b-col>
                                    </b-row>
                                    <b-row>
                                        <b-col>
                                            Clone:
                                        </b-col>
                                        <b-col cols="10">
                                            <b>{{
                                                workflow.config.clone
                                                    ? 'Yes'
                                                    : 'No'
                                            }}</b>
                                        </b-col>
                                    </b-row>
                                    <b-row>
                                        <b-col>
                                            Image:
                                        </b-col>
                                        <b-col cols="10">
                                            <b>{{ workflow.config.image }}</b>
                                        </b-col>
                                    </b-row>
                                    <b-row>
                                        <b-col>
                                            From:
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
                                            To:
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
                                            Parameters:
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
                                            Command:
                                        </b-col>
                                        <b-col cols="10">
                                            <b
                                                ><code>{{
                                                    ' ' +
                                                        workflow.config.commands
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
                                                @click="
                                                    workflowSelected(workflow)
                                                "
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
                </b-card-body>
            </b-col>
        </b-row>
    </div>
</template>

<script>
export default {
    name: 'WorkflowDetail',
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
            this.$emit('workflowSelected', workflow);
        }
    }
};
</script>

<style scoped></style>
