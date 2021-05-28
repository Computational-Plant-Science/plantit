<template>
    <div>
        <b-row style="z-index: 10">
            <b-col cols="10">
                <h2>
                    <b-link
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        variant="outline-dark"
                        v-b-tooltip.hover
                        :to="{
                            name: 'workflow',
                            params: {
                                owner: workflow['repo']['owner']['login'],
                                name: workflow['repo']['name']
                            }
                        }"
                    >
                        {{ workflow.config.name }}
                    </b-link>
                </h2>
                <b-badge v-if="!workflow.config.public" variant="warning"
                    >Private</b-badge
                >
                <b-badge
                    v-for="topic in workflow.repo.topics"
                    v-bind:key="topic"
                    class="mr-1 mb-0"
                    variant="secondary"
                    >{{ topic }}</b-badge
                >
                <br />
                <small>
                    <b-link
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        @click="
                            openRepo(
                                'https://github.com/' +
                                    workflow.repo.owner.login +
                                    '/' +
                                    workflow.repo.name
                            )
                        "
                    >
                        <i class="fab fa-github fa-fw"></i>
                        {{ workflow.repo.owner.login }}/{{ workflow.repo.name }}
                    </b-link>
                </small>
                <br />
                <small>{{ workflow.repo.description }}</small>
                <br />
            </b-col>
            <b-col cols="1"></b-col>
        </b-row>
        <b-img
            rounded
            class="card-img-right"
            style="max-width: 6rem;opacity: 0.8;position: absolute;right: -25px;top: -15px;z-index:1;"
            right
            :src="
                `https://raw.githubusercontent.com/${workflow.repo.owner.login}/${workflow.repo.name}/master/${workflow.config.logo}`
            "
        ></b-img>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'workflow-blurb',
    props: {
        workflow: {
            type: Object,
            required: true
        }
    },
    methods: {
        openRepo(url) {
            window.open(url);
        }
    },
    computed: mapGetters('user', ['profile'])
};
</script>
<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
