<template>
    <div>
        <br />
        <br />
        <b-container fluid>
            <b-row>
                <b-col class="text-center">
                    <h4
                        :class="profile.darkMode ? 'text-white' : 'text-theme'"
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
                        ><small>stats</small>
                    </h4>
                </b-col>
            </b-row>
            <b-row>
                <b-col align-self="end" class="text-right mr-0">
                    <b-tabs
                        v-model="activeTab"
                        nav-class="bg-transparent"
                        active-nav-item-class="bg-transparent text-dark"
                        pills
                        align="center"
                    >
                        <b-tab
                            title="Workflows"
                            :title-link-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            :class="
                                profile.darkMode
                                    ? 'theme-dark m-0 p-3'
                                    : 'theme-light m-0 p-3'
                            "
                            ><template #title
                                ><h1 class="text-success text-center">
                                    <span v-if="workflowCount >= 0">{{
                                        workflowCount
                                    }}</span
                                    ><b-spinner
                                        v-else
                                        label="Loading..."
                                        variant="secondary"
                                    ></b-spinner>
                                </h1>
                                <b-button
                                    :variant="
                                        activeTab === 0
                                            ? profile.darkMode
                                                ? 'outline-success'
                                                : 'success'
                                            : profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    ><i class="fas fa-stream fa-fw"></i>
                                    <br />
                                    Phenomics
                                    <br />
                                    Workflows</b-button
                                ></template
                            >
                            <!--<b-row>
                                <b-col
                                    ><Plotly
                                        v-if="showWorkflowsUsagePlot"
                                        :data="workflowsUsagePlotTraces"
                                        :layout="workflowsUsagePlotLayout"
                                    ></Plotly
                                ></b-col>
                            </b-row>-->
                            <br />
                            <b-card-group deck columns
                                ><b-card
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    class="overflow-hidden text-left p-2"
                                    v-for="workflow in workflows"
                                    v-bind:key="
                                        workflow.config.name +
                                        '/' +
                                        workflow.branch.name
                                    "
                                    no-body
                                    style="min-width: 50rem"
                                    ><blurb
                                        :workflow="workflow"
                                        :linkable="false"
                                    ></blurb></b-card
                            ></b-card-group>
                        </b-tab>
                        <b-tab
                            :title-link-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            :class="
                                profile.darkMode
                                    ? 'theme-dark m-0 p-3'
                                    : 'theme-light m-0 p-3'
                            "
                        >
                            <template #title>
                                <h1 class="text-success text-center">
                                    <span v-if="userCount >= 0">{{
                                        userCount
                                    }}</span>
                                    <b-spinner
                                        v-else
                                        label="Loading..."
                                        variant="secondary"
                                    ></b-spinner>
                                </h1>
                                <b-button
                                    :variant="
                                        activeTab === 1
                                            ? profile.darkMode
                                                ? 'outline-success'
                                                : 'success'
                                            : profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                >
                                    <i class="fas fa-user fa-fw"></i>
                                    <br />
                                    Scientists &<br />Researchers</b-button
                                ></template
                            ><Plotly
                                v-if="showUsersPlot"
                                :data="usersPlotTraces"
                                :layout="usersPlotLayout"
                            ></Plotly>
                            <br />
                            <span text-center>
                                <h1 class="text-success">
                                    <span v-if="onlineCount >= 0">{{
                                        onlineCount
                                    }}</span>
                                    <b-spinner
                                        v-else
                                        label="Loading..."
                                        variant="secondary"
                                    ></b-spinner>
                                </h1>
                                <b-badge
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    ><i class="fas fa-signal fa-fw"></i>
                                    Online</b-badge
                                ></span
                            >
                        </b-tab
                        >
                        <b-tab
                            title="Developers"
                            :title-link-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            :class="
                                profile.darkMode
                                    ? 'theme-dark m-0 p-3'
                                    : 'theme-light m-0 p-3'
                            "
                            ><template #title
                                ><h1 class="text-success text-center">
                                    <span v-if="developerCount >= 0">{{
                                        developerCount
                                    }}</span>
                                    <b-spinner
                                        v-else
                                        label="Loading..."
                                        variant="secondary"
                                    ></b-spinner>
                                </h1>
                                <b-button
                                    :variant="
                                        activeTab === 2
                                            ? profile.darkMode
                                                ? 'outline-success'
                                                : 'success'
                                            : profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    ><i class="fas fa-code fa-fw"></i>
                                    <br />
                                    Workflow
                                    <br />
                                    Developers</b-button
                                ></template
                            >
                          <b-card-group
                                ><b-card
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    class="overflow-hidden text-left p-2"
                                    v-for="user in developers"
                                    v-bind:key="user"
                                    ><b-row
                                        ><b-col
                                            ><b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :href="`https://github.com/${user}`"
                                                ><i
                                                    class="fab fa-github fa-fw"
                                                ></i>
                                                {{ user }}</b-link
                                            ></b-col
                                        ><b-col md="auto">{{
                                            workflows.filter(
                                                (wf) =>
                                                    wf.repo.owner.login === user
                                            ).length
                                        }}</b-col></b-row
                                    ></b-card
                                ></b-card-group
                            ></b-tab
                        >

                      <b-tab
                            title="Tasks"
                            :title-link-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            :class="
                                profile.darkMode
                                    ? 'theme-dark m-0 p-3'
                                    : 'theme-light m-0 p-3'
                            ">
                        <template #title
                                ><h1 class="text-success text-center">
                                    <span v-if="taskCount >= 0">{{
                                        taskCount
                                    }}</span>
                                    <b-spinner
                                        v-else
                                        label="Loading..."
                                        variant="secondary"
                                    >
                                    </b-spinner>
                                </h1>
                                <b-button
                                    :variant="
                                        activeTab === 3
                                            ? profile.darkMode
                                                ? 'outline-success'
                                                : 'success'
                                            : profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    v-b-tooltip.hover
                                    :title="`Tasks`"
                                    ><i class="fas fa-terminal fa-fw"></i>
                                    <br />
                                    Workflow
                                    <br />
                                    Submissions
                                </b-button></template
                            >
                          <b-row align-h="center">
                            <b-col>
                              <h1 v-if="runningCount >= 0" class="text-success">
                                {{ runningCount }}
                            </h1>
                            <b-spinner
                                v-else
                                type="grow"
                                label="Loading..."
                                variant="secondary"
                            ></b-spinner
                            ><b-badge
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                ><i class="fas fa-terminal fa-fw"></i>
                                Running</b-badge
                            >
                          </b-col>
                          </b-row>
                          <br/><Plotly
                                v-if="showTasksTotalPlot"
                                :data="tasksTotalPlotTraces"
                                :layout="tasksTotalPlotLayout"
                            ></Plotly>
                            </b-tab>
                      <b-tab
                            title="Institutions"
                            :title-link-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            :class="
                                profile.darkMode
                                    ? 'theme-dark m-0 p-3'
                                    : 'theme-light m-0 p-3'
                            "
                            ><template #title
                                ><h1 class="text-success text-center">
                                    <span v-if="institutionCount >= 0">{{
                                        institutionCount
                                    }}</span>
                                    <b-spinner
                                        v-else
                                        label="Loading..."
                                        variant="secondary"
                                    >
                                    </b-spinner>
                                </h1>
                                <b-button
                                    :variant="
                                        activeTab === 4
                                            ? profile.darkMode
                                                ? 'outline-success'
                                                : 'success'
                                            : profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    v-b-tooltip.hover
                                    title="Institutions"
                                    ><i class="fas fa-university fa-fw"></i>
                                    <br />
                                    Represented
                                    <br />
                                    Institutions
                                </b-button></template>
                        <!--<b-row><b-col><b-list-group><b-list-group-item class="text-left" v-for="inst in getInstitutions" v-bind:key="inst.institution">{{ inst.institution }} ({{ inst.count }})</b-list-group-item></b-list-group></b-col></b-row>-->
                        <!--<div id="map" style="height: 40rem; width: 100%"></div>-->
                    </b-tab>
                    </b-tabs>
                </b-col>
            </b-row>
          <div id="map" style="height: 40rem; width: 100%"></div>
        </b-container>
    </div>
</template>

<script>
import blurb from '@/components/workflows/workflow-blurb.vue';
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import mapboxgl from 'mapbox-gl';
import { Plotly } from 'vue-plotly';
import moment from 'moment';

export default {
    name: 'stats',
    components: {
        blurb,
        Plotly,
    },
    data: function () {
        return {
            map: {},
            mapCenter: [0, 0],
            mapMarkers: [],
            mapPopup: null,
            userCount: -1,
            timeseriesUsersTotal: null,
            timeseriesTasksTotal: null,
            timeseriesTasksUsage: null,
            timeseriesWorkflowsUsage: null,
            onlineCount: -1,
            workflowCount: -1,
            developerCount: -1,
            taskCount: -1,
            runningCount: -1,
            institutionCount: -1,
            institutions: [],
            activeTab: 0,
        };
    },
    async mounted() {
        // set up map
        this.configureMap();

        // load stats
        await this.loadCounts();
        await this.loadInstitutions();
        await this.loadTimeseries();

        // load public workflows
        await this.$store.dispatch('workflows/loadPublic');
    },
    methods: {
        configureMap() {
            mapboxgl.accessToken = process.env.VUE_APP_MAPBOX_TOKEN;
            this.map = new mapboxgl.Map({
                container: 'map',
                style: `mapbox://styles/mapbox/${
                    this.profile.darkMode ? 'dark-v10' : 'light-v10'
                }`,
                center: this.mapCenter,
                zoom: 1,
            });

            this.mapPopup = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false,
            });

            var map = this.map;
            var popup = this.mapPopup;

            this.map.on('mouseenter', 'institutions', function (e) {
                // Change the cursor style as a UI indicator.
                map.getCanvas().style.cursor = 'pointer';

                var feature = e.features[0];
                var coordinates = feature.geometry.coordinates.slice();
                var html = `<span class="text-dark">${feature.properties.name}, ${feature.properties.count} user(s)</span>`;

                // Ensure that if the map is zoomed out such that multiple
                // copies of the feature are visible, the popup appears
                // over the copy being pointed to.
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] +=
                        e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Populate the popup and set its coordinates
                // based on the feature found.
                popup.setLngLat(coordinates).setHTML(html).addTo(map);
            });

            this.map.on('mouseleave', 'institutions', function () {
                map.getCanvas().style.cursor = '';
                popup.remove();
            });
        },
        async loadCounts() {
            await axios
                .get('/apis/v1/stats/counts/')
                .then((response) => {
                    this.userCount = response.data.users;
                    this.onlineCount = response.data.online;
                    this.workflowCount = response.data.workflows;
                    this.developerCount = response.data.developers;
                    this.agentCount = response.data.agents;
                    this.taskCount = response.data.tasks;
                    this.runningCount = response.data.running;
                    this.institutionCount = response.data.institutions;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadInstitutions() {
            await axios
                .get('/apis/v1/stats/institutions/')
                .then((response) => {
                    this.institutions = response.data;
                    if (this.map) this.paintInstitutions();
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
                    this.timeseriesUsersTotal = {
                        x: response.data.users_total.map((tuple) =>
                            moment(tuple[0]).format('YYYY-MM-DD HH:mm:ss')
                        ),
                        y: response.data.users_total.map((tuple) => tuple[1]),
                        type: 'line',
                        mode: 'lines',
                        line: { color: '#d6df5D', shape: 'spline' },
                    };
                    this.timeseriesTasksTotal = {
                        x: response.data.tasks_total.map((tuple) =>
                            moment(tuple[0]).format('YYYY-MM-DD HH:mm:ss')
                        ),
                        y: response.data.tasks_total.map((tuple) => tuple[1]),
                        name: 'Total',
                        type: 'line',
                        mode: 'lines',
                        line: { color: '#d6df5D', shape: 'spline' },
                    };
                    this.timeseriesTasksUsage = {
                        x: Object.keys(response.data.tasks_usage).map((key) =>
                            moment(key).format('YYYY-MM-DD HH:mm:ss')
                        ),
                        y: Object.keys(response.data.tasks_usage).map(
                            (key) => response.data.tasks_usage[key]
                        ),
                        name: 'Usage',
                        yaxis: 'y2',
                        type: 'line',
                        mode: 'lines',
                        line: { color: '#f0e68c', shape: 'spline' },
                    };
                    this.timeseriesWorkflowsUsage = Object.fromEntries(
                        Object.entries(response.data.workflows_usage).map(
                            ([k, v]) => [
                                k,
                                {
                                    x: Object.keys(v).map((key) =>
                                        moment(key).format(
                                            'YYYY-MM-DD HH:mm:ss'
                                        )
                                    ),
                                    y: Object.values(v),
                                    name: k,
                                    type: 'line',
                                    mode: 'lines',
                                    line: { shape: 'spline' },
                                },
                            ]
                        )
                    );
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        unpaintInstitutions() {
            this.map.removeLayer('institutions');
            this.map.removeSource('institutions');
        },
        paintInstitutions() {
            this.map.addSource('institutions', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: Object.values(this.institutions).map(
                        (institution) => institution.geocode
                    ),
                },
            });
            this.map.addLayer({
                id: 'institutions',
                type: 'circle',
                source: 'institutions',
                paint: {
                    'circle-color': '#4264fb',
                    'circle-radius': 6,
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#ffffff',
                },
            });
        },
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', [
            'publicWorkflows',
            'publicWorkflowsLoading',
        ]),
        getInstitutions() {
          return Object.values(this.institutions);
        },
        workflows() {
            return this.publicWorkflows.filter((wf) => !wf.example);
        },
        developers() {
            return Array.from(
                new Set(this.workflows.map((wf) => wf.repo.owner.login))
            );
        },
        darkMode() {
            return this.profile.darkMode;
        },
        showUsersPlot() {
            return (
                this.timeseriesUsersTotal !== null &&
                this.timeseriesUsersTotal.x.length > 1
            );
        },
        usersPlotTraces() {
            return [this.timeseriesUsersTotal];
        },
        usersPlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                height: 350,
                // title: {
                //     text: 'Total',
                //     font: {
                //         color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                //     },
                // },
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
                    showticklabels: false,
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
            };
        },
        showTasksTotalPlot() {
            return (
                this.timeseriesTasksTotal !== null &&
                this.timeseriesTasksTotal.x.length > 1
            );
        },
        tasksTotalPlotTraces() {
            return [this.timeseriesTasksTotal, this.timeseriesTasksUsage];
        },
        tasksTotalPlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                hovermode: false,
                // title: {
                //     text: 'Total',
                //     font: {
                //         color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                //     },
                // },
                legend: {
                    // orientation: 'h',
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
                    showticklabels: false,
                },
                yaxis2: {
                  showticklabels: false,
                    overlaying: 'y',
                    side: 'right'
                  },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
            };
        },
        showTasksUsagePlot() {
            return (
                this.timeseriesTasksUsage !== null &&
                this.timeseriesTasksUsage.x.length > 1
            );
        },
        tasksUsagePlotTraces() {
            return [this.timeseriesTasksUsage];
        },
        tasksUsagePlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                hovermode: false,
                title: {
                    text: 'Usage',
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
        showWorkflowsUsagePlot() {
            return (
                this.timeseriesWorkflowsUsage !== null &&
                Object.keys(this.timeseriesWorkflowsUsage).length > 0
            );
        },
        workflowsUsagePlotTraces() {
            return [this.timeseriesWorkflowsUsage];
        },
        workflowsUsagePlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                title: {
                    text: 'Usage',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    // orientation: 'h',
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
};
</script>

<style scoped></style>
