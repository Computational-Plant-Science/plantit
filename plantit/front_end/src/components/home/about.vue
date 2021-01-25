<template>
    <div>
        <b-card
            class="rounded-0 text-center"
            bg-variant="dark"
            border-variant="dark"
            text-variant="white"
            header-bg-variant="dark"
            header-border-variant="dark"
            footer-border-variant="white"
        >
            <template slot="header" style="border: none">
                <br />
                <br />
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col>
                        <b-img
                            style="max-width: 5rem;transform: translate(0px, 20px);"
                            :src="require('../../assets/logo.png')"
                            center
                            class="m-0 p-0"
                        ></b-img>
                        <h2 class="text-white">
                            plant<small class="mb-3 text-success">IT</small>
                        </h2>
                        <h5 class="text-white mt-4">
                            plant phenomics in the browser
                        </h5>
                    </b-col>
                </b-row>
                <br />
                <b-row>
                    <b-col align-self="end" class="text-right mr-0"
                        ><h2 class="text-success">{{ runs }}</h2></b-col
                    >
                    <b-col align-self="middle" class="text-left ml-0 pl-0"
                        >jobs (and counting!)</b-col
                    >
                </b-row>
            </template>
            <b-container>
                <br />
                <br />
                <b-row align-content="center" align-h="center">
                    <b-col align-h="center">
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left rounded-0 overflow-hidden"
                            bg-variant="dark"
                            no-body
                            text-variant="success"
                            img-width="120px"
                            :img-src="
                                require('../../assets/frontpage/icons/algorithm.png')
                            "
                            img-left
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text class="ml-4 mr-4">
                                <h4 class="text-white">
                                    plug in your data
                                </h4>
                                attach metadata and collaborate with team
                                members
                                <br />
                                upload, analyze, and publish datasets with
                                <b-link
                                    class="text-white"
                                    href="https://www.cyverse.org/"
                                    >CyVerse</b-link
                                ><!--, or plug in cloud stores like
                            <b-link
                                class="text-white"
                                href="https://aws.amazon.com/s3/"
                                >Amazon S3</b-link
                            >-->
                            </b-card-text>
                        </b-card>
                    </b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col>
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left rounded-0 overflow-hidden"
                            bg-variant="dark"
                            text-variant="success"
                            no-body
                              img-width="120px"
                            :img-src="
                                require('../../assets/frontpage/icons/code.png')
                            "
                            img-right
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text class="ml-4 mr-4 text-success text-right">
                                <h4 class="text-white">
                                    host your software
                                </h4>
                                discover projects or publish your own code with
                                <b-link
                                    class="text-white"
                                    href="https://www.github.com/"
                                    >Github</b-link
                                >
                                <br />
                                if it can run in
                                <b-link
                                    class="text-white"
                                    href="https://www.docker.com/"
                                    >Docker</b-link
                                >
                                or
                                <b-link
                                    class="text-white"
                                    href="https://sylabs.io/docs/"
                                    >Singularity</b-link
                                >, it will run on
                                <b-link class="text-white">PlantIT</b-link>
                            </b-card-text>
                        </b-card>
                    </b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col md="auto">
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left text-white rounded-0 overflow-hidden"
                            no-body
                            img-width="120px"
                            bg-variant="dark"
                            text-variant="success"
                            :img-src="
                                require('../../assets/frontpage/icons/UI.png')
                            "
                            img-left
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text class="ml-4 mr-4">
                                <h4 class="text-white">
                                    workflows on the web
                                </h4>
                                configure parameters and deploy to a cluster
                                <br />
                                all from the browser, no programming required
                            </b-card-text>
                        </b-card>
                    </b-col>
                </b-row>
                <br />
                <br />
            </b-container>
        </b-card>
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'home-about',
    async mounted() {
        this.loadAllUsers();
        await this.loadRuns();
    },
    data: function() {
        return {
            users: [],
            runs: 0
        };
    },
    methods: {
        loadAllUsers() {
            axios
                .get('/apis/v1/users/get_all/')
                .then(response => {
                    this.users = response.data.users;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadRuns() {
            return axios
                .get('/apis/v1/runs/get_total_count/')
                .then(response => {
                    this.runs = response.data.count;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    }
};
</script>

<style lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
h1
    color: $success
</style>
