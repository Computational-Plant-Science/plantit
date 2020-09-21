<template>
    <div>
        <b-row style="z-index: 10">
            <b-col>
                <small>
                    <b-link
                        variant="outline-dark"
                        :href="
                            'https://github.com/' +
                                flow.repository.owner.login +
                                '/' +
                                flow.repository.name
                        "
                    >
                        <i class="fab fa-github fa-fw"></i>
                        {{ flow.repository.owner.login }}/{{
                            flow.repository.name
                        }}
                    </b-link>
                </small>
                <br />
                <br />
                {{ flow.repository.description }}
            </b-col>
        </b-row>
        <br />
        <b-row align-v="end">
            <b-col>
                <b-button
                    v-if="selectable"
                    class="text-left"
                    variant="outline-dark"
                    v-b-tooltip.hover
                    @click="flowSelected"
                >
                    {{ selectable }}
                    <!--{{ flow.repository.name }}-->
                </b-button>
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
        <b-img
            class="card-img-right"
            style="max-width: 14rem;opacity: 0.1;position: absolute;right: -25px;top: -25px;z-index:1"
            right
            :src="require('../assets/logo.png')"
        ></b-img>
    </div>
</template>

<script>
import router from '@/router';

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
            type: String,
            required: true
        }
    },
    methods: {
        flowSelected() {
            router.push({
                name: 'flow',
                params: {
                    username: this.flow['repository']['owner']['login'],
                    name: this.flow['repository']['name']
                }
            });
        }
    }
};
</script>

<style scoped></style>
