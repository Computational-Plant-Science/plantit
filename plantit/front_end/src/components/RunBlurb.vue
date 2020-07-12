<template>
    <div v-if="workflow.config">
        <b-row>
            <b-col>
                <h2>
                    Run
                    <b-badge :variant="run.state === 2 ? 'danger' : 'success'"
                        >{{ statusToString(run.state) }}
                    </b-badge>
                    on
                    <b-badge variant="dark">{{ run.cluster }}</b-badge>
                </h2>
            </b-col>
        </b-row>
        <b-row>
            <b-col align-self="start">
                <b-row>
                    <b-col>
                        <b-card-body>
                            <h2>{{ workflow.config.name }}</h2>
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
                            <b-row v-if="selectable">
                                <b-col>
                                    <b-button
                                        class="text-left"
                                        variant="success"
                                        v-b-tooltip.hover
                                        @click="workflowSelected(workflow)"
                                    >
                                        <i class="fas fa-terminal"></i>
                                        Run <b>{{ workflow.config.name }}</b>
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
                style="max-width: 15rem; max-height: 12rem"
            >
                <b-img
                    v-if="run.state === 1 || run.state === 2"
                    style="max-width: 8rem"
                    :src="require('../assets/logo.png')"
                    right
                >
                </b-img>
                <b-img
                    v-else
                    style="max-width: 15rem;"
                    :src="require('../assets/PlantITLoading.gif')"
                    right
                ></b-img>
            </b-col>
        </b-row>
    </div>
</template>

<script>
export default {
    name: 'RunBlurb',
    props: {
        workflow: {
            type: Object,
            required: true
        },
        run: {
            type: Object,
            required: true
        },
        selectable: {
            type: Boolean,
            required: true
        }
    },
    methods: {
        statusToString(status) {
            switch (status) {
                case 1:
                    return 'Completed';
                case 2:
                    return 'Failed';
                case 3:
                    return 'Running';
                case 4:
                    return 'Created';
            }
        }
    }
};
</script>

<style scoped></style>
