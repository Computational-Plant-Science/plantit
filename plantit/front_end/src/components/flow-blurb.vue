<template>
    <div>
        <b-row style="z-index: 10">
            <b-col>
                <h4>
                    <b-link
                        :disabled="selectable"
                        class="text-left"
                        variant="outline-dark"
                        v-b-tooltip.hover
                        @click="flowSelected"
                    >
                        {{ flow.config.name }}
                    </b-link>
                </h4>
                <small>
                    <b-link
                        variant="outline-dark"
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
                <br />
                <br />
                {{ flow.repo.description }}
                <br />
                <br />
                <b-button v-if="selectable" @click="flowSelected" variant="warning">
                    {{ selectable }}
                </b-button>
            </b-col>
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
                    username: this.flow['repo']['owner']['login'],
                    name: this.flow['repo']['name']
                }
            });
        }
    }
};
</script>

<style scoped></style>
