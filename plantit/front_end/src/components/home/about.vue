<template>
    <div>
        <b-card
            class="rounded-0 text-center"
            bg-variant="dark"
            border-variant="dark"
            text-variant="white"
            header-bg-variant="dark"
            header-border-variant="dark"
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
                        <h1 class="text-success">
                            PlantIT
                        </h1>
                        <h5 class="text-white mt-4">
                            Plant science workflow automation in the browser.
                        </h5>
                    </b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col align-self="end" class="text-right"
                        ><h3 class="text-success">
                            {{ users.length }}
                        </h3></b-col
                    >
                    <b-col align-self="middle" class="text-left">users</b-col>
                </b-row>
                <b-row>
                    <b-col align-self="end" class="text-right"
                        ><h3 class="text-success">{{ runs }}</h3></b-col
                    >
                    <b-col align-self="middle" class="text-left">jobs</b-col>
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
                            :img-src="
                                require('../../assets/frontpage/icons/algorithm.png')
                            "
                            img-width="100px"
                            img-height="90px"
                            img-left
                            style="border: none;"
                        >
                            <b-card-text class="ml-4">
                                <h4 class="text-white">
                                    Access or upload data.
                                </h4>
                                Upload, store, and publish datasets with
                                <b-link
                                    class="text-white"
                                    href="https://www.cyverse.org/"
                                    >CyVerse</b-link
                                >.<!--, or plug in cloud stores like
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
                            :img-src="
                                require('../../assets/frontpage/icons/code.png')
                            "
                            img-width="100px"
                            img-height="90px"
                            img-left
                            style="border: none;"
                        >
                            <b-card-text class="ml-4">
                                <h4 class="text-white">
                                    Find or share software.
                                </h4>
                                Run code from
                                <b-link
                                    class="text-white"
                                    href="https://www.github.com/"
                                    >Github</b-link
                                >
                                or publish your own to the community &mdash; if
                                it can run in
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
                                <b-link class="text-white">plantit</b-link>.
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
                            bg-variant="dark"
                            text-variant="success"
                            :img-src="
                                require('../../assets/frontpage/icons/UI.png')
                            "
                            img-width="100px"
                            img-height="90px"
                            img-left
                            style="border: none;"
                        >
                            <b-card-text class="ml-4">
                                <h4 class="text-white">
                                    Workflows on the web.
                                </h4>
                                Configure parameters, deploy to a cluster, and
                                get notified when results are ready &mdash; all
                                from the browser, no programming required.
                            </b-card-text>
                        </b-card>
                    </b-col>
                </b-row>
                <br />
                <br />
            </b-container>
        </b-card>
        <b-card
            class="rounded-0 text-center"
            bg-variant="white"
            border-variant="white"
            text-variant="dark"
            header-bg-variant="dark"
            header-border-variant="dark"
        >
            <br />
            <br />
            <br />
            <div class="p-0 m-0 background-white text-white">
                <b-img
                    style="max-width: 5rem;transform: translate(0px, 20px);"
                    :src="require('../../assets/logo.png')"
                    center
                    class="m-0 p-0"
                ></b-img>
            </div>
            <div class="p-1 pt-2 background-dark">
                <h1 class="text-center text-white">
                    <b class="text-dark">About</b>
                </h1>
            </div>
            <br />
            <br />
            <b-container>
                <b-row align-content="center">
                    <b-col class="text-left">
                        <VueMarkdown :source="source"> </VueMarkdown>
                    </b-col>
                </b-row>
            </b-container>
            <br />
            <br />
            <br />
            <b-container class="text-center">
                <div class="p-0 m-0 background-white text-white">
                    <b-img
                        style="max-width: 5rem;transform: translate(0px, 20px);"
                        :src="require('../../assets/logo.png')"
                        center
                        class="m-0 p-0"
                    ></b-img>
                </div>
                <h1 class="text-center">
                    <b>People</b>
                </h1>
                <br />
                <br />

                <b-row class="justify-content-md-center mb-4">
                    <b-col>
                        <b-tabs
                            justified
                            active-nav-item-class="text-dark"
                            nav-class=""
                        >
                            <br />
                            <b-tab title="Active" active>
                                <template v-slot:title class="m-0 p-0">
                                    <b class="text-secondary">Active</b>
                                </template>
                                <b-card-group deck columns>
                                    <b-card
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        sub-title-text-variant="secondary"
                                        text-variant="dark"
                                        title="Alexander Bucksch"
                                        sub-title="Principal Investigator"
                                        style="min-width: 20rem"
                                    >
                                        <template
                                            v-slot:footer
                                            style="background-color: white"
                                        >
                                            <b-button
                                                variant="outline-dark"
                                                href="https://github.com/koalaspirit"
                                                class="mr-2 p-2"
                                            >
                                                <i
                                                    class="fab fa-github fa-2x success"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                variant="outline-dark"
                                                href="https://www.researchgate.net/profile/Alexander_Bucksch"
                                                class="mr-2 p-2"
                                            >
                                                <i
                                                    class="fab fa-researchgate fa-2x success"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                variant="outline-dark"
                                                href="https://www.linkedin.com/in/abucksch/"
                                                class="mr-2 p-2"
                                            >
                                                <i
                                                    class="fab fa-linkedin fa-2x success"
                                                ></i>
                                            </b-button>
                                        </template>
                                    </b-card>
                                    <b-card
                                        sub-title-text-variant="secondary"
                                        text-variant="dark"
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        title="Wes Bonelli"
                                        sub-title="Developer"
                                        style="min-width: 20rem"
                                    >
                                        <template
                                            v-slot:footer
                                            style="background-color: white"
                                        >
                                            <b-button
                                                class="mr-2 p-2"
                                                variant="outline-dark"
                                                href="https://github.com/w-bonelli"
                                            >
                                                <i
                                                    class="fab fa-github fa-2x success"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                variant="outline-dark"
                                                class="mr-2 p-2"
                                                href="https://www.researchgate.net/profile/Wes_Bonelli"
                                            >
                                                <i
                                                    class="fab fa-researchgate fa-2x success"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                class="mr-2 p-2"
                                                variant="outline-dark"
                                                href="https://www.linkedin.com/in/wesley-bonelli/"
                                            >
                                                <i
                                                    class="fab fa-linkedin fa-2x success"
                                                ></i>
                                            </b-button>
                                        </template>
                                    </b-card>
                                </b-card-group>
                            </b-tab>
                            <b-tab title="Former">
                                <template v-slot:title class="m-0 p-0">
                                    <b class="text-secondary">Former</b>
                                </template>
                                <b-card-group columns>
                                    <b-card
                                        bg-variant="white"
                                        sub-title-text-variant="secondary"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        text-variant="dark"
                                        border-variant="white"
                                        title="Chris Cotter"
                                        sub-title="Developer"
                                        style="min-width: 20rem;"
                                    >
                                        <template
                                            v-slot:footer
                                            style="background-color: white"
                                        >
                                            <b-button
                                                class="mr-2 p-2"
                                                variant="outline-dark"
                                                href="https://github.com/cottersci"
                                            >
                                                <i
                                                    class="fab fa-github fa-2x success"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                variant="outline-dark"
                                                href="https://www.linkedin.com/in/crcotter/"
                                                class="mr-2 p-2"
                                            >
                                                <i
                                                    class="fab fa-linkedin fa-2x success"
                                                ></i>
                                            </b-button>
                                        </template>
                                    </b-card>
                                    <b-card
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        text-variant="dark"
                                        sub-title-text-variant="secondary"
                                        title="Abhiram Das"
                                        sub-title="Developer (DIRT)"
                                        style="min-width: 20rem"
                                    >
                                        <template
                                            v-slot:footer
                                            style="background-color: white"
                                        >
                                            <b-button
                                                variant="outline-dark"
                                                href="https://www.linkedin.com/in/abhiram-das-7a8b382/"
                                                class="card-link"
                                            >
                                                <i
                                                    class="fab fa-linkedin fa-2x success"
                                                ></i>
                                            </b-button>
                                        </template>
                                    </b-card>
                                    <b-card
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        text-variant="dark"
                                        sub-title-text-variant="secondary"
                                        title="Megan Flory"
                                        sub-title="Designer"
                                        style="min-width: 20rem"
                                    >
                                        <template
                                            v-slot:footer
                                            style="background-color: white"
                                        >
                                            <b-button
                                                variant="outline-dark"
                                                href="https://github.com/meganflory"
                                                class="mr-2 p-2"
                                            >
                                                <i
                                                    class="fab fa-github fa-2x success"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                variant="outline-dark"
                                                href="https://www.linkedin.com/in/meganflory13/"
                                                class="mr-2 p-2"
                                            >
                                                <i
                                                    class="fab fa-linkedin fa-2x success"
                                                ></i>
                                            </b-button>
                                        </template>
                                    </b-card>
                                    <b-card
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        text-variant="dark"
                                        sub-title-text-variant="secondary"
                                        title="Maria Luck"
                                        sub-title="Developer"
                                        style="min-width: 20rem"
                                    >
                                        <template
                                            v-slot:footer
                                            style="background-color: white"
                                        >
                                            <b-button
                                                variant="outline-dark"
                                                href="https://www.linkedin.com/in/mariacpedrosa/"
                                                class="mr-2 p-2"
                                            >
                                                <i
                                                    class="fab fa-linkedin fa-2x success"
                                                ></i>
                                            </b-button>
                                        </template>
                                    </b-card>
                                </b-card-group>
                            </b-tab>
                        </b-tabs>
                    </b-col>
                </b-row>
            </b-container>
        </b-card>
    </div>
</template>

<script>
import VueMarkdown from 'vue-markdown';
import about from '@/assets/markdown/about.md';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'home-about',
    components: {
        VueMarkdown
    },
    async mounted() {
        this.loadAllUsers();
        await this.loadRuns();
    },
    data: function() {
        return {
            source: about,
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

<style scoped lang="sass">
@import '../../scss/_colors.sass'

h1
    color: $color-highlight
</style>
