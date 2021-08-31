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
                        <div
                        >
                            <h1
                                class="text-white mb-0"
                                style="text-decoration: underline; z-index: 10"
                            >
                                plant<small
                                    class="mb-3 text-success"
                                    style="text-decoration: underline;"
                                    >IT</small
                                >
                            </h1>
                            <b-img
                                class="mt-0 pt-0"
                                :src="require('../../assets/coil.png')"
                                style="max-width: 3rem; overflow: hidden; position: absolute; left: 48.6%; z-index: 1; opacity: 0.2"
                                center
                            ></b-img>
                            <h4 class="text-white mt-4 ml-4">
                                a web portal for cloud
                                <span class="text-success"
                                    ><span class="fa-stack mr-0 fa-2x">
                                        <i
                                            class="fas fa-seedling fa-stack-2x"
                                        ></i>
                                        <i
                                            class="text-dark fas fa-camera-retro fa-stack-1x"
                                            style="opacity: 0.4;"
                                        ></i><i class="fas fa-cloud fa-stack-2x" style="opacity: 0.3;position: relative;top:-10px;left:-3px;color: #d9edfe"></i></span
                                    >phenotyping automation</span
                                >
                            </h4>
                        </div>
                    </b-col>
                </b-row>
                <br />
                <br />
                <b-container>
                    <b-row>
                        <!--
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1 v-if="userCount >= 0" class="text-success">
                                {{ userCount }}
                            </h1></b-col
                        >
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 v-if="workflowCount >= 0" class="text-white">
                                users
                            </h5>
                        </b-col>
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1 class="text-success">
                                {{ workflowCount }}
                            </h1></b-col
                        >
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 class="text-white">workflows</h5>
                        </b-col>
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1 v-if="taskCount >= 0" class="text-success">
                          {{ taskCount }}
                        </h1>
                            <b-spinner
                                v-else
                                type="grow"
                                label="Loading..."
                                variant="secondary"
                            ></b-spinner>
                        </b-col>
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 class="text-white">tasks</h5>
                        </b-col>-->
                    </b-row>
                </b-container>
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
                            text-variant="white"
                            img-width="120px"
                            :img-src="
                                require('../../assets/frontpage/icons/algorithm.png')
                            "
                            img-left
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text class="ml-4 mr-4">
                                <h4 class="text-success">
                                    Data storage & provenance
                                </h4>
                                Built on the
                                <b-link
                                    class="text-white"
                                    href="https://www.cyverse.org/"
                                    >CyVerse</b-link
                                >
                                Data Store
                                <!--, or plug in cloud stores like
                            <b-link
                                class="text-white"
                                href="https://aws.amazon.com/s3/"
                                >Amazon S3</b-link
                            >-->
                                and Terrain API for virtual data science
                                <br />
                                Track experiments & datasets and export
                                <b-link
                                    class="text-white"
                                    href="https://www.miappe.org/"
                                    >MIAPPE</b-link
                                >
                                metadata with a click
                            </b-card-text>
                        </b-card>
                    </b-col>
                    <b-col md="auto"
                        ><b-col md="auto"
                            ><b-img
                                rounded
                                style="max-height: 5rem;"
                                center
                                :src="
                                    require('../../assets/logos/cyverse_bright.png')
                                "
                            ></b-img></b-col
                    ></b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col md="auto"
                        ><b-img
                            rounded
                            style="max-height: 6rem;"
                            center
                            :src="
                                require('../../assets/logos/github_white.png')
                            "
                        ></b-img
                    ></b-col>
                    <b-col>
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left rounded-0 overflow-hidden"
                            bg-variant="dark"
                            text-variant="white"
                            no-body
                            img-width="120px"
                            :img-src="
                                require('../../assets/frontpage/icons/code.png')
                            "
                            img-right
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text
                                class="ml-4 mr-4 text-white text-right"
                            >
                                <h4 class="text-success">
                                    Cultivate open source science
                                </h4>
                                Explore F/OSS phenotyping tools or bind your own
                                <b-link
                                    class="text-white"
                                    href="https://www.github.com/"
                                    >Github</b-link
                                >
                                repository
                                <br/>
                                Develop software with
                                <b-link
                                    class="text-white"
                                    href="https://www.docker.com/"
                                    >Docker</b-link
                                >
                                and deploy anywhere with
                                <b-link
                                    class="text-white"
                                    href="https://sylabs.io/docs/"
                                    >Singularity</b-link
                                >
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
                            class="text-left text-white rounded-0 overflow-hidden"
                            no-body
                            img-width="120px"
                            bg-variant="dark"
                            text-variant="white"
                            :img-src="
                                require('../../assets/frontpage/icons/UI.png')
                            "
                            img-left
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text class="ml-4 mr-4">
                                <h4 class="text-success">
                                    Code optional, always visible
                                </h4>
                                High-throughput phenotyping on the web, no
                                programming necessary
                                <br />
                                Transparently reproducible container workflows on the command line
                            </b-card-text>
                        </b-card>
                    </b-col>
                    <b-col md="auto"
                        ><b-img
                            rounded
                            style="max-height: 6rem;"
                            center
                            :src="require('../../assets/logos/docker.png')"
                        ></b-img></b-col
                    ><b-col md="auto"
                        ><b-img
                            rounded
                            style="max-height: 6rem;"
                            center
                            :src="require('../../assets/logos/singularity.png')"
                        ></b-img
                    ></b-col>
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
        await this.loadCounts();
    },
    data: function() {
        return {
            userCount: -1,
            workflowCount: -1,
            taskCount: -1
        };
    },
    methods: {
        loadCounts() {
            axios
                .get('/apis/v1/stats/counts/')
                .then(response => {
                    this.userCount = response.data.users;
                    this.workflowCount = response.data.workflows;
                    this.taskCount = response.data.tasks;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
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
