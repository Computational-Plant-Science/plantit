<template>
    <div v-if="workflow.config">
        <b-img
            class="card-img-left"
            v-if="workflow.icon_url"
            style="max-width: 8rem;opacity: 0.15"
            right
            :src="workflow.icon_url"
        >
        </b-img>
        <b-img
            v-else
            class="card-img-left"
            style="max-width: 15rem;opacity: 0.15"
            right
            :src="require('../assets/logo.png')"
        ></b-img>
        <b-row class="card-img-overlay">
            <b-col>
                <b-card-body>
                    <b-row>
                        <b-col md="auto" class="mr-0">
                            <b-button
                                class="text-left mr-0"
                                variant="success"
                                v-b-tooltip.hover
                                @click="workflowSelected(workflow)"
                            >
                                <i class="fas fa-terminal"></i>
                                Run
                            </b-button>
                        </b-col>
                        <b-col md="auto" class="ml-0 pl-0 mr-0 pr-0">
                            <h2 class="ml-0 pl-0 mr-0 pr-0">
                                {{ workflow.config.name }}
                            </h2>
                        </b-col>
                        <b-col md="auto">
                            <h5 v-if="showPublic">
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
                                    }}
                                </b-badge>
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
                            <br />
                            <br />

                            <b-row>
                                <b-col>
                                    {{ workflow.repo.description }}
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
    name: 'WorkflowBlurb',
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
