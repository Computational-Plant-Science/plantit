<template>
    <div class="m-0 p-0">
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
                            ><h5 class="text-white">researchers</h5>
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
                            ><h1
                                v-if="institutionCount >= 0"
                                class="text-success"
                            >
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
        <b-card
            class="rounded-0"
            bg-variant="dark"
            border-variant="dark"
            text-variant="white"
            header-bg-variant="dark"
            header-border-variant="dark"
            footer-border-variant="white"
        >
            <br />
            <b-container>
                <b-row class="text-center">
                    <b-col>
                        <h5 class="text-light">About</h5>
                    </b-col></b-row
                >
                <br />
                <b-row class="text-light lightlinks text-center"
                    ><b-col>
                        <p>
                            <b-img
                                style="
                                    max-width: 1.5rem;
                                    position: relative;
                                    top: -3px;
                                "
                                :src="require('../../assets/logo.png')"
                                class="m-0 p-0"
                            ></b-img>
                            free service for parallelizable image-based plant phenotyping &mdash; deploy to a cluster with a click
                            </p>
                            <p>
                            <b-img
                                style="
                                    max-width: 1.5rem;
                                    position: relative;
                                    top: -3px;
                                "
                                :src="require('../../assets/logo.png')"
                                class="m-0 p-0"
                            ></b-img>
                            bind CyVerse datasets to reproducible container workflows, no programming experience required
                        </p>
                        <p>
                            <b-img
                                style="
                                    max-width: 1.5rem;
                                    position: relative;
                                    top: -3px;
                                "
                                :src="require('../../assets/logo.png')"
                                class="m-0 p-0"
                            ></b-img>
                            add a <code>plantit.yaml</code> file to a public
                            repository to integrate a workflow, then configure
                            and run in the browser
                        </p>
                        <p>
                            <b-img
                                style="
                                    max-width: 1.5rem;
                                    position: relative;
                                    top: -3px;
                                "
                                :src="require('../../assets/logo.png')"
                                class="m-0 p-0"
                            ></b-img>
                            supersedes
                            <b-link href="http://dirt.cyverse.org/?q=welcome"
                                ><b>D</b>igital <b>I</b>maging of <b>R</b>oot
                            <b>T</b>raits</b-link
                            > &mdash; supports original <b-link
                                href="https://github.com/Computational-Plant-Science/DIRT"
                                >DIRT2D</b-link
                            >, <b-link
                                href="https://github.com/Computational-Plant-Science/3D_model_reconstruction_demo"
                                >DIRT3D</b-link
                            > <b-link
                                href="https://academic.oup.com/plphys/article/187/2/739/6317839"
                                >(Liu et al 2021)</b-link
                            > and more
                        </p>
                        <p>
                            <b-img
                                style="
                                    max-width: 1.5rem;
                                    position: relative;
                                    top: -3px;
                                "
                                :src="require('../../assets/logo.png')"
                                class="m-0 p-0"
                            ></b-img>
                            flexible, but built for phenomics &mdash; a different tool (e.g.,
                            <b-link href="https://genomevolution.org/CoGe/"
                                >CoGe</b-link
                            >
                            or
                            <b-link href="https://easygwas.ethz.ch/"
                                >easyGWAS</b-link
                            >) may be a better fit for genomics workflows
                            </p>
                            <p>
                            <b-img
                                style="
                                    max-width: 1.5rem;
                                    position: relative;
                                    top: -3px;
                                "
                                :src="require('../../assets/logo.png')"
                                class="m-0 p-0"
                            ></b-img> contributions, bug
                            reports, suggestions, and feature requests are welcome
                            <b-link
                                href="https://github.com/Computational-Plant-Science/plantit"
                                >on GitHub</b-link
                            > &mdash;
                            <b-link
                                href="https://github.com/Computational-Plant-Science/plantit/discussions"
                                >get in touch</b-link
                            >
                            regarding a use case
                        </p>
                    </b-col>
                </b-row>
                <br />
                <br />
                <br />
                <b-row class="text-center">
                    <b-col>
                        <h5 class="text-light">Development Team</h5>
                    </b-col></b-row
                >
                <br />
                <b-row class="justify-content-md-center mb-4">
                    <b-col class="justify-content-md-center">
                        <b-card-group deck columns>
                            <b-card
                                v-for="contrib in currentContributors"
                                v-bind:key="contrib.name"
                                class="text-center mb-4"
                                style="min-width: 10rem"
                                bg-variant="dark"
                                border-variant="transparent"
                                footer-bg-variant="dark"
                                footer-border-variant="default"
                            >
                                <template #default>
                                    <h5 class="text-white">
                                        {{ contrib.name }}
                                    </h5>
                                    <!--<b class="text-white">{{ contrib.role }}</b>-->
                                </template>
                                <template
                                    v-slot:footer
                                    style="background-color: white"
                                >
                                    <b-button
                                        size="sm"
                                        variant="outline-dark"
                                        :href="`https://github.com/${contrib.github_username}`"
                                        class="mr-2 p-2"
                                    >
                                        <i
                                            class="fab fa-github fa-2x text-warning"
                                        ></i>
                                    </b-button>
                                    <b-button
                                        size="sm"
                                        variant="outline-dark"
                                        :href="`https://www.researchgate.net/profile/${contrib.researchgate_username}`"
                                        class="mr-2 p-2"
                                    >
                                        <i
                                            class="fab fa-researchgate fa-2x text-warning"
                                        ></i>
                                    </b-button>
                                    <b-button
                                        size="sm"
                                        v-if="contrib.linkedin_username"
                                        variant="outline-dark"
                                        :href="`https://www.linkedin.com/in/${contrib.linkedin_username}/`"
                                        class="mr-2 p-2"
                                    >
                                        <i
                                            class="fab fa-linkedin fa-2x text-warning"
                                        ></i>
                                    </b-button>
                                </template>
                            </b-card>
                        </b-card-group>
                        <br />
                        <br />
                    </b-col>
                </b-row>
                <b-row class="text-center">
                    <b-col>
                        <h6
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Former Contributors
                        </h6>
                    </b-col></b-row
                >
                <br />
                <b-row class="justify-content-md-center mb-4">
                    <b-col class="justify-content-md-center">
                        <b-card-group deck columns>
                            <b-card
                                v-for="contrib in formerContributors"
                                v-bind:key="contrib.name"
                                class="text-center mb-4"
                                style="min-width: 10rem"
                                bg-variant="dark"
                                border-variant="transparent"
                            >
                                <template #default>
                                    <h5 class="text-white">
                                        {{ contrib.name }}
                                    </h5>
                                    <b class="text-white">{{ contrib.role }}</b>
                                </template>
                            </b-card>
                        </b-card-group>
                        <br />
                        <br />
                    </b-col>
                </b-row>
                <br />
                <b-row class="text-center">
                    <b-col>
                <p>
                            <i
                                ><small><small><b>note:</b> platform developers make no guarantees
                                regarding workflow results' quality &mdash; <br/> questions should be directed to workflow authors via GitHub or some other channel</small></small></i
                            >
                        </p>
</b-col>
</b-row>
                <br />
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col
                        ><b-img
                            center
                            style="
                                max-width: 12rem;
                                transform: translate(0px, 20px);
                            "
                            href="https://www.computational-plant-science.org/joomla30/"
                            :src="require('../../assets/cps2.png')"
                            class="m-0 p-0"
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
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'home-about',
    async mounted() {
        await Promise.all([
            this.loadCounts(true),
            this.loadTimeseries(),
            this.loadContributors(),
        ]);
    },
    data: function () {
        return {
            userCount: -1,
            workflowCount: -1,
            developerCount: -1,
            taskCount: -1,
            institutionCount: -1,
            timeseriesTasksRunning: null,
            contributors: [],
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
        async loadContributors() {
            await axios
                .get('/apis/v1/misc/contributors/')
                .then((response) => {
                    this.contributors = response.data.contributors;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
    },
    computed: {
        ...mapGetters('user', ['profile']),
        currentContributors() {
            return this.contributors.filter((c) => !c.former);
        },
        formerContributors() {
            return this.contributors.filter((c) => c.former);
        },
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
