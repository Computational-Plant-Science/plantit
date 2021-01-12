<template>
    <div>
        <b-row style="z-index: 10">
            <b-col cols="10">
                <h2>
                    <b-link
                        :class="darkMode ? 'text-white' : 'text-dark'"
                        variant="outline-dark"
                        v-b-tooltip.hover
                        @click="flowSelected"
                    >
                        {{ flow.config.name }}
                    </b-link>
                </h2>
                <b-badge
                    v-for="topic in flow.repo.topics"
                    v-bind:key="topic"
                    class="mr-1 mb-0"
                    variant="secondary"
                    >{{ topic }}</b-badge
                >
                <br/>
                <small>
                    <b-link
                        :class="darkMode ? 'text-light' : 'text-dark'"
                        @click="
                            openRepo(
                                'https://github.com/' +
                                    flow.repo.owner.login +
                                    '/' +
                                    flow.repo.name
                            )
                        "
                    >
                        <i class="fab fa-github fa-fw"></i>
                        {{ flow.repo.owner.login }}/{{ flow.repo.name }}
                    </b-link>
                </small>
                <br />
                {{ flow.repo.description }}
                <br />
            </b-col>
            <b-col cols="1"></b-col>
        </b-row>
        <b-img
            rounded="circle"
            class="card-img-right"
            style="max-width: 6rem;opacity: 0.8;position: absolute;right: -25px;top: -15px;z-index:1;"
            right
            :src="
                `https://raw.githubusercontent.com/${flow.repo.owner.login}/${flow.repo.name}/master/${flow.config.logo}`
            "
        ></b-img>
    </div>
</template>

<script>
import router from '@/router';
import { mapGetters } from 'vuex';

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
        },
        openRepo(url) {
            window.open(url);
        }
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn',
        'darkMode'
    ])
};
</script>
<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
</style>
