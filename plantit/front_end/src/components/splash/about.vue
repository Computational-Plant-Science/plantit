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
                <b-container v-if="userCount >= 0">
                    <b-row>
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1 v-if="workflowCount >= 0" class="text-success">
                                {{ workflowCount }}
                            </h1>
                            <b-spinner
                                v-else
                                type="spinner"
                                label="Loading..."
                                variant="success"
                            ></b-spinner
                        ></b-col>
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 class="text-white">workflows</h5>
                        </b-col>
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1 v-if="userCount >= 0" class="text-success">
                                {{ userCount }}
                            </h1>
                            <b-spinner
                                v-else
                                type="spinner"
                                label="Loading..."
                                variant="success"
                            ></b-spinner
                        ></b-col>
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 class="text-white">
                                researchers
                            </h5>
                        </b-col>
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1
                                v-if="developerCount >= 0"
                                class="text-success"
                            >
                                {{ developerCount }}
                            </h1>
                            <b-spinner
                                v-else
                                type="spinner"
                                label="Loading..."
                                variant="success"
                            ></b-spinner
                        ></b-col>
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 class="text-white">developers</h5>
                        </b-col>
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1 v-if="taskCount >= 0" class="text-success">
                                {{ taskCount }}
                            </h1>
                            <b-spinner
                                v-else
                                type="spinner"
                                label="Loading..."
                                variant="success"
                            ></b-spinner>
                        </b-col>
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 class="text-white">submissions</h5>
                        </b-col>
                        <b-col align-self="end" class="text-right mr-0"
                            ><h1 v-if="institutionCount >= 0" class="text-success">
                                {{ institutionCount }}
                            </h1>
                            <b-spinner
                                v-else
                                type="spinner"
                                label="Loading..."
                                variant="success"
                            ></b-spinner>
                        </b-col>
                        <b-col align-self="end" class="text-left ml-0 pl-0"
                            ><h5 class="text-white">institutions</h5>
                        </b-col>
                    </b-row>
                    <!--<br/>
                    <b-row v-if="profile.loggedIn">
                        <b-col
                            ><Plotly
                                v-if="timeseriesTasksRunning !== null"
                                :data="tasksRunningPlotData"
                                :layout="tasksRunningPlotLayout"
                            ></Plotly
                        ></b-col>
                    </b-row>-->
                </b-container>
            </template>
            <b-container>
                <br />
                <b-row align-content="center" align-h="center">
                    <b-col align-h="center">
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left rounded-0 overflow-hidden"
                            bg-variant="dark"
                            no-body
                            text-variant="white"
                            img-width="50px"
                            img-height="50px"
                            :img-src="
                                require('../../assets/frontpage/icons/UI.png')
                            "
                            img-left
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text class="ml-4 mr-4">
                                <h4 class="text-success">
                                    plant phenomics rooted in the cloud
                                </h4>
                                built on
                                <b-link
                                    class="text-white"
                                    href="https://www.cyverse.org/"
                                    >CyVerse</b-link
                                >
                                for data storage and
                                <b-link
                                    class="text-white"
                                    href="https://www.github.com/"
                                    >Github</b-link
                                >
                                for source control,
                                <br />
                                <small
                                    ><b-img
                                        style="
                                            max-width: 1.5rem;
                                            position: relative;
                                            top: 1px;
                                        "
                                        :src="require('../../assets/logo.png')"
                                        left
                                        class="m-0 p-0"
                                    ></b-img
                                    >plant<small
                                        class="mb-3 text-success"
                                        style="
                                            text-decoration: underline;
                                            text-shadow: 1px 1px 2px black;
                                            z-index: 100;
                                        "
                                        ><small>IT</small></small
                                    ></small
                                >
                                is both science gateway and continuous delivery
                                platform
                            </b-card-text>
                        </b-card>
                    </b-col>
                    <b-col md="auto" align-self="center"
                        ><b-img
                            rounded
                            style="max-height: 2rem"
                            center
                            class="mb-1"
                            :src="
                                require('../../assets/logos/cyverse_bright.png')
                            "
                        ></b-img
                        ><b-img
                            rounded
                            class="mt-2"
                            style="max-height: 2rem"
                            left
                            :src="
                                require('../../assets/logos/github_mark_white.png')
                            "
                        ></b-img
                        ><b-img
                            rounded
                            style="max-height: 3rem"
                            center
                            :src="
                                require('../../assets/logos/github_white.png')
                            "
                        ></b-img
                    ></b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col md="auto" align-self="center"
                        ><b-img
                            rounded
                            style="max-height: 4rem"
                            center
                            :src="require('../../assets/logos/docker.png')"
                        ></b-img></b-col
                    ><b-col md="auto" align-self="center"
                        ><b-img
                            rounded
                            style="max-height: 4rem"
                            center
                            :src="require('../../assets/logos/singularity.png')"
                        ></b-img
                    ></b-col>
                    <b-col>
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left text-white rounded-0 overflow-hidden"
                            no-body
                            img-width="50px"
                            img-height="50px"
                            bg-variant="dark"
                            text-variant="white"
                            :img-src="
                                require('../../assets/frontpage/icons/algorithm.png')
                            "
                            img-right
                            style="border: none; box-shadow: none"
                        >
                            <b-card-text
                                class="ml-4 mr-4 text-white text-right"
                            >
                                <h4 class="text-success">
                                    portable pipelines for open science
                                </h4>
                                deploy
                                <b-link
                                    class="text-white"
                                    href="https://www.docker.com/"
                                    >Docker</b-link
                                >
                                image definitions to clusters with
                                <b-link
                                    class="text-white"
                                    href="https://sylabs.io/docs/"
                                    >Singularity</b-link
                                >
                                <br />
                                for portable, versionable, reproducible
                                phenotyping workflows
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
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'home-about',
    async mounted() {
        await Promise.all([this.loadCounts(true), this.loadTimeseries()]);
    },
    data: function () {
        return {
            userCount: -1,
            workflowCount: -1,
            developerCount: -1,
            taskCount: -1,
            institutionCount: -1,
            timeseriesTasksRunning: null,
        };
    },
    methods: {
        async loadCounts(invalidate) {
            await axios
                .get(`/apis/v1/stats/counts/?invalidate=${invalidate}`)
                .then((response) => {
                    this.userCount = response.data.users;
                    this.workflowCount = response.data.workflows;
                    this.developerCount = response.data.developers;
                    this.taskCount = response.data.tasks;
                    this.institutionCount = response.data.institutions;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadTimeseries() {
            await axios
                .get('/apis/v1/stats/timeseries/')
                .then((response) => {
                    this.timeseriesUsers = [response.data.users];
                    this.timeseriesTasks = [response.data.tasks];
                    this.timeseriesTasksRunning = [response.data.tasks_running];
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
    },
    computed: {
        ...mapGetters('user', ['profile']),
        tasksRunningPlotData() {
            if (this.timeseriesTasksRunning === null)
                return { x: [], y: [], type: 'scatter' };
            return [
                {
                    x: this.timeseriesTasksRunning[0].x.map((t) =>
                        moment(t).format('YYYY-MM-DD HH:mm:ss')
                    ),
                    y: this.timeseriesTasksRunning[0].y,
                    text: this.timeseriesTasksRunning[0].y.map(
                        () => `running tasks`
                    ),
                    type: 'scatter',
                    line: { color: '#d6df5D' },
                },
            ];
        },
        tasksRunningPlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                images: [
                    {
                        x: 0.415,
                        y: 0.2,
                        sizex: 1.2,
                        sizey: 1.2,
                        source: require('../../assets/logo.png'),
                        xanchor: 'middle',
                        yanchor: 'bottom',
                        opacity: 0.15,
                    },
                ],
                title: {
                    // text: 'Tasks Running',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)',
                        },
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)',
                        },
                    },
                },
                yaxis: {
                    dtick: 1,
                    showticklabels: false,
                },
                paper_bgcolor: '#1c1e23',
                plot_bgcolor: '#1c1e23',
            };
        },
    },
};
</script>

<style lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
h1
    color: $success
</style>
