<template>
    <div>
        <b-img
            class="card-img-left"
            style="max-width: 14rem;opacity: 0.2;position: relative;right: -75px"
            right
            :src="require('../assets/logo.png')"
        ></b-img>
        <b-row class="card-img-overlay">
            <b-col>
                <b-row>
                    <b-col>
                        <small>
                            <b-link
                                class="text-secondary"
                                :href="
                                    'https://github.com/' +
                                        flow.repository.owner.login +
                                        '/' +
                                        flow.repository.name
                                "
                            >
                                {{ flow.repository.owner.login }}/{{
                                    flow.repository.name
                                }}
                            </b-link>
                        </small>
                        <br />
                        <br />

                        <b-row>
                            <b-col>
                                {{ flow.repository.description }}
                            </b-col>
                        </b-row>
                    </b-col>
                </b-row>
            </b-col>
        </b-row>
        <b-row class="card-img-overlay" align-v="bottom">
            <b-col align-self="end">
                <b-button
                    :href="flow.repository.html_url"
                    variant="outline-dark"
                    block
                    :title="flow.repository.html_url"
                    class="text-center"
                >
                    <i class="fab fa-github fa-1x fa-fw"></i>
                    View
                </b-button>
            </b-col>
            <b-col align-self="end">
                <b-button
                    v-if="selectable"
                    block
                    class="text-center"
                    variant="outline-dark"
                    v-b-tooltip.hover
                    @click="flowSelected(flow)"
                >
                    <i class="fas fa-terminal fa-1x fa-fw"></i>
                    Try it out
                    <!--{{ flow.repository.name }}-->
                </b-button>
                <h3 v-else>{{ flow.repository.name }}</h3>
            </b-col>
            <!--<b-col md="auto" v-if="showPublic">
                        <h5>
                            <b-badge
                                :variant="
                                    flow.config.public
                                        ? 'success'
                                        : 'warning'
                                "
                                >{{
                                flow.config.public
                                    ? 'Public'
                                    : 'Private'
                              }}
                            </b-badge>
                        </h5>
                    </b-col>-->
        </b-row>
    </div>
</template>

<script>
export default {
    name: 'flow-blurb',
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
    methods: {
        flowSelected: function(workflow) {
            this.$emit('flowSelected', workflow);
        }
    }
};
</script>

<style scoped></style>
