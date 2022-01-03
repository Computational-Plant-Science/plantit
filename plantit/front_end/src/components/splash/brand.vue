<template>
    <div id="background" class="vertical-center m-0 p-0">
        <b-container id="main">
            <b-card
                align="center"
                class="p-1 text-white"
                footer-bg-variant="transparent"
                footer-border-variant="white"
                border-variant="default"
                text-variant="white"
                :bg-variant="profile.darkMode ? 'dark' : 'white'"
                style="
                    width: 90%;
                    height: 90%;
                    padding: 0;
                    margin: 0 auto;
                    float: none;
                    margin-bottom: 10px;
                    opacity: 0.95;
                "
            >
                <template #header>
                    <b-row class="p-1"
                        ><b-col md="auto" align-self="center">
                            <h4
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-theme'
                                "
                                style="text-decoration: underline; z-index: 100"
                            >
                                plant<small
                                    class="mb-3 text-success"
                                    style="
                                        text-decoration: underline;
                                        text-shadow: 1px 1px 2px black;
                                        z-index: 100;
                                    "
                                    ><small>IT</small></small
                                >
                                <small
                                    ><small
                                        ><small
                                            ><b-badge variant="success"
                                                ><span v-if="version !== 0">{{
                                                    version
                                                }}</span
                                                ><i
                                                    class="fas fa-spinner"
                                                    v-else
                                                ></i></b-badge></small></small
                                ></small>
                            </h4>
                        </b-col>
                        <b-col md="auto" align-self="center"
                            ><b-link
                                to="/about"
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i
                                    class="fas fa-question-circle fa-1x fa-fw"
                                ></i
                                >About</b-link
                            ></b-col
                        >
                        <!--<b-nav-item
                            to="/beta"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="Beta Test"
                            ><span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fas fa-vial fa-1x fa-fw"></i>Beta
                                Testing</span
                            ></b-nav-item
                        >-->
                        <b-col md="auto" align-self="center"
                            ><b-link
                                to="/stats"
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fas fa-chart-bar fa-1x fa-fw"></i
                                >Stats</b-link
                            ></b-col
                        >
                        <b-col md="auto" align-self="center">
                            <b-link
                                href="https://plantit.readthedocs.io/en/latest"
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fas fa-book fa-1x fa-fw"></i
                                >Docs</b-link
                            >
                        </b-col>
                        <b-col md="auto" align-self="center">
                            <b-link
                                href="https://github.com/Computational-Plant-Science/plantit"
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fab fa-github fa-1x fa-fw"></i
                                >Github</b-link
                            >
                        </b-col>
                        <b-col></b-col>
                        <b-col align-self="center" md="auto">
                            <b-button
                                v-if="!profile.loggedIn"
                                variant="white"
                                class="text-center"
                                href="/apis/v1/idp/cyverse_login/"
                            >
                                Log in with
                                <b-img
                                    :src="
                                        require('@/assets/sponsors/cyversebw-notext.png')
                                    "
                                    height="18px"
                                    alt="Cyverse"
                                ></b-img>
                                <b>CyVerse</b>
                            </b-button>
                            <b-button
                                v-else
                                variant="white"
                                class="text-right"
                                href="/apis/v1/idp/cyverse_login/"
                            >
                                <span
                                    :class="
                                        profile.darkMode
                                            ? 'text-success'
                                            : 'text-dark'
                                    "
                                >
                                    <i
                                        class="fas fa-arrow-circle-right fa-fw"
                                    ></i>
                                    Log In</span
                                >
                            </b-button>
                        </b-col>
                        <!--<b-nav-item
                            href="#"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="Slack"
                        >
                            <span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fab fa-slack fa-1x fa-fw"></i>
                                Slack</span
                            >
                        </b-nav-item>-->
                    </b-row>
                    <b-row>
                        <b-col md="auto">
                            <i class="text-theme mt-4 ml-1 text-left">
                                <span>a browser gateway for </span
                                ><span
                                    class="text-theme"
                                    style="
                                        text-decoration: underline;
                                        text-decoration-color: #d6df5d;
                                    "
                                    >HPC plant phenotyping
                                </span>
                            </i></b-col
                        >
                        <b-col></b-col>
                    </b-row>
                </template>
                <b-row class="m-0 mt-2 mb-2"
                    ><b-col class="text-left">
                        <h5
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                        >
                            New to plantIT?
                        </h5>
                        <p
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                        >
                            plantIT is a web portal for
                            high-performance/-throughput phenomics. It automates
                            data transfers and workflow deployments, making it
                            easy to submit phenotyping pipelines to XSEDE and
                            other supercomputing resources.
                        </p>
                        <hr />
                        <p
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                        >
                            For <b>Researchers:</b> Deploy highly parallel
                            simulations or analyses to a cluster or
                            supercomputer, all from the browser.
                        </p>
                        <p
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                        >
                            For <b>Developers:</b> Publish versionable container
                            workflows from any GitHub repository to the
                            worldwide research community.
                        </p></b-col
                    ><b-col class="text-left">
                        <h5
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                        >
                            Recent news
                        </h5>
                        <span v-if="loadingUpdates">
                            <b-spinner
                                type="spinner"
                                label="Loading..."
                                variant="secondary"
                            ></b-spinner>
                            Loading updates...
                        </span>
                        <span
                            v-else-if="updates.length === 0"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >No updates to show.</span
                        >
                        <b-row
                            v-for="update in updates"
                            v-bind:key="update.created"
                            ><b-col
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                                ><small>{{ prettify(update.created) }}</small>
                                <p>{{ update.content }}</p></b-col
                            ></b-row
                        >
                    </b-col></b-row
                >
            </b-card>
        </b-container>
        <div style="position: absolute; bottom: 0; left: 49%">
            <i
                class="fas fa-chevron-down fa-5x fa-fw"
                id="about-down-arrow"
            ></i>
        </div>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from 'moment';

export default {
    name: 'home-brand',
    data: function () {
        return {
            version: 0,
            updates: [],
            timeseriesTasksRunning: null,
        };
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
                        x: 0.385,
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
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
            };
        },
    },
    created: async function () {
        this.crumbs = this.$route.meta.crumb;
        await Promise.all([
            this.getVersion(),
            this.getUpdates(),
            this.loadTimeseries(),
        ]);
    },
    methods: {
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        async getVersion() {
            await axios({
                method: 'get',
                url: `https://api.github.com/repos/Computational-Plant-Science/plantit/tags`,
                headers: { 'Content-Type': 'application/json' },
            })
                .then((response) => {
                    this.version = response.data[0].name;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        async getUpdates() {
            await axios
                .get('/apis/v1/news/updates/')
                .then((response) => {
                    this.updates = response.data.updates;
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
};
</script>

<style scoped lang="sass">
@import '../../scss/_colors.sass'
@import '../../scss/main.sass'


.vertical-center
    min-height: 100%
    /* Fallback for browsers do NOT support vh unit */
    min-height: 100vh
    /* These two lines are counted as one :-)       */

    display: flex
    align-items: center

#background
    background-image: url('../../assets/frontpage/index_bg.png')
    background-blend-mode: normal
    background-color: hsla(0%, 0%, 100%, 1)
    background-repeat: no-repeat
    background-position: center
    background-size: cover
    min-height: 100vh
    width: 100%
    white-space: nowrap
    position: relative
    text-align: center

#background:after
    opacity: 0.5

#main
    text-align: center
    padding-bottom: 50px
    white-space: normal

#message
    width: 60%
    background-color: $color-box-background
    margin: 0 auto
    color: white

#main-nav
    width: 60%
    background-color: $color-box-background
    margin-top: 10px
    margin-bottom: 75px
    border-radius: 10px

    a
        color: $color-highlight
        margin: 0 auto

    a:hover
        text-decoration: underline

@keyframes down-arrow-highlight
    0%
        color: $color-box-background
    100%
        color: $color-highlight

#about-down-arrow
    position: absolute
    bottom: 0
    left: 50%
    margin-left: -40px
    animation-name: down-arrow-highlight
    animation-duration: 2s
    animation-iteration-count: infinite
    animation-direction: alternate

.avatar
    height: 35px
</style>
