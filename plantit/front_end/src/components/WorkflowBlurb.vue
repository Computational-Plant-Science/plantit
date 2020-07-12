<template>
    <div v-if="workflow.config">
        <b-row>
            <b-col align-self="center">
                <b-row>
                    <b-col>
                        <b-card-body>
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
                                    }}
                                </b-badge>
                            </h5>
                            <h3><b>{{ workflow.config.name }}</b></h3>
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
                            <br />
                            <b-row v-if="selectable">
                                <b-col>
                                    <b-button
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
                        </b-card-body>
                    </b-col>
                </b-row>
            </b-col>
            <b-col
                md="auto"
                align-self="end"
                style="max-width: 8rem; max-height: 12rem"
            >
                <b-img
                    v-if="workflow.icon_url"
                    style="max-width: 8rem"
                    :src="workflow.icon_url"
                    top
                >
                </b-img>
                <b-img
                    v-else
                    style="max-width: 8rem;"
                    :src="require('../assets/logo.png')"
                    right
                ></b-img>
            </b-col>
        </b-row>
    </div>
</template>

<script>
export default {
    name: 'WorkflowBlurb',
    props: {
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
