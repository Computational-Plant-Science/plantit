<template>
    <div
        class="w-100 h-100 pl-3 pt-3"
        :style="
            darkMode
                ? 'background-color: #d6df5D'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <b-container class="pl-3 pt-3" fluid>
            <b-row v-if="targets.length > 0" align-v="center" align-h="center">
                <b-col>
                    <b-card-group deck columns class="justify-content-center">
                        <b-card
                            v-for="target in targets"
                            v-bind:key="target.name"
                            :bg-variant="darkMode ? 'dark' : 'white'"
                            :header-bg-variant="darkMode ? 'dark' : 'white'"
                            border-variant="default"
                            :header-border-variant="
                                darkMode ? 'secondary' : 'default'
                            "
                            :text-variant="darkMode ? 'white' : 'dark'"
                            style="min-width: 30rem; max-width: 40rem;"
                            class="overflow-hidden mb-4"
                        >
                            <b-row style="z-index: 10">
                                <b-col cols="10">
                                    <h2>
                                        <b-link
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                            variant="outline-dark"
                                            v-b-tooltip.hover
                                            @click="targetSelected(target)"
                                        >
                                            {{ target.name }}
                                        </b-link>
                                    </h2>
                                    <b-badge
                                        v-if="!target.public"
                                        variant="warning"
                                        >Private</b-badge
                                    >
                                    <br />
                                    <small>
                                        {{ target.description }}
                                    </small>
                                    <br />
                                </b-col>
                                <b-col cols="1"></b-col>
                            </b-row>
                            <b-img
                                v-if="target.logo"
                                rounded
                                class="card-img-right overflow-hidden"
                                style="max-height: 5rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                right
                                :src="target.logo"
                            ></b-img>
                            <i
                                v-else
                                style="max-width: 7rem;position: absolute;right: 20px;top: 20px;"
                                right
                                class="card-img-left fas fa-server fa-2x fa-fw"
                            ></i>
                        </b-card>
                    </b-card-group>
                    <!--<b-card-group deck columns class="justify-content-center">
                        <b-card
                            v-for="target in targets"
                            v-bind:key="target.name"
                            :bg-variant="darkMode ? 'dark' : 'white'"
                            :header-bg-variant="darkMode ? 'dark' : 'white'"
                            border-variant="default"
                            :header-border-variant="
                                darkMode ? 'secondary' : 'default'
                            "
                            :text-variant="darkMode ? 'white' : 'dark'"
                            style="min-width: 30rem; max-width: 40rem;"
                            class="overflow-hidden mb-4"
                        >
                        </b-card>
                        <b-row align-v="center">
                            <b-col
                                style="color: white; cursor: pointer"
                                @click="targetSelected(target)"
                            >
                                <h5
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    {{ target.name }}
                                    <small
                                        :class="
                                            darkMode
                                                ? 'text-warning'
                                                : 'text-dark'
                                        "
                                        >({{ target.hostname }})</small
                                    >
                                </h5>
                            </b-col>
                        </b-row>
                    </b-card-group>-->
                </b-col>
            </b-row>
            <b-row align-h="center" class="text-center" v-else>
                <b-col>
                    None to show.
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
import { mapGetters } from 'vuex';

export default {
    name: 'targets.vue',
    data: function() {
        return {
            targets: []
        };
    },
    mounted() {
        this.loadTargets();
    },
    computed: mapGetters(['profile', 'loggedIn', 'allUsers', 'darkMode']),
    methods: {
        loadTargets() {
            this.targetsLoading = true;
            axios
                .get('/apis/v1/targets/get_all/')
                .then(response => {
                    this.targets = response.data.targets;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        targetSelected(target) {
            router.push({
                name: 'target',
                params: {
                    name: target.name
                }
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.hvr:hover
  text-decoration: underline
  text-underline-color: $dark
  cursor: pointer
</style>
