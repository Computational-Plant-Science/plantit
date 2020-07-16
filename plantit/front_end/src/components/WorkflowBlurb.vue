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
            style="max-width: 11rem;opacity: 0.15"
            right
            :src="require('../assets/logo.png')"
        ></b-img>
        <b-row class="card-img-overlay">
            <b-col>
                <b-row>
                    <b-col>
                        <b-button
                            v-if="selectable"
                            block
                            class="text-left"
                            variant="success"
                            v-b-tooltip.hover
                            @click="workflowSelected(workflow)"
                        >
                            <i class="fas fa-terminal"></i>
                            {{ workflow.config.name }}
                        </b-button>
                        <h3 v-else>{{ workflow.config.name }}</h3>
                    </b-col>
                    <b-col md="auto" v-if="showPublic">
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
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <small>
                            <b-link
                                class="text-secondary"
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
