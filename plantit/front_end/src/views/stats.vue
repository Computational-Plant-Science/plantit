<template>
    <div>
        <br />
        <br />
        <b-container fluid>
            <b-row>
                <b-col class="text-center">
                    <b-img
                        style="max-width: 5rem;transform: translate(0px, 20px);"
                        :src="require('../assets/logo.png')"
                        center
                        class="m-0 p-0"
                    ></b-img>
                    <h1
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        style="text-decoration: underline;"
                    >
                        plant<small
                            class="mb-3 text-success"
                            style="text-decoration: underline;text-shadow: 1px 0 0 #000, 0 -1px 0 #000, 0 1px 0 #000, -1px 0 0 #000;"
                            >IT</small
                        ><small class="ml-1">stats</small>
                    </h1>
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
                        ><b-tab
                            title="Users"
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
                                <h1
                                    v-if="userCount >= 0"
                                    class="text-success text-center"
                                >
                                    {{ userCount }}
                                </h1>
                                <b-spinner
                                    v-else
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner>
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
                                    v-b-tooltip.hover
                                    :title="`Users`"
                                >
                                    <i class="fas fa-user fa-fw"></i>
                                    Users</b-button
                                ></template
                            ><Plotly
                                v-if="timeseriesUsers.length > 0"
                                :data="usersPlotData"
                                :layout="usersPlotLayout"
                            ></Plotly>
                            <br />
                            <h1 v-if="onlineCount >= 0" class="text-success">
                                {{ onlineCount }}
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
                                ><i class="fas fa-signal fa-fw"></i>
                                Online</b-badge
                            ></b-tab
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
                                ><h1
                                    v-if="workflowCount >= 0"
                                    class="text-success text-center"
                                >
                                    {{ workflowCount }}
                                </h1>
                                <b-spinner
                                    v-else
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner
                                ><b-button
                                    :variant="
                                        activeTab === 1
                                            ? profile.darkMode
                                                ? 'outline-success'
                                                : 'success'
                                            : profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    v-b-tooltip.hover
                                    :title="`Workflows`"
                                    ><i class="fas fa-stream fa-fw"></i>
                                    Workflows</b-button
                                ></template
                            >
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Public Workflows ({{ publicWorkflows.length }})
                            </h5>
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
                                    v-for="workflow in publicWorkflows"
                                    v-bind:key="workflow.config.name"
                                    no-body
                                    style="min-width: 50rem"
                                    ><blurb
                                        :workflow="workflow"
                                        :linkable="false"
                                    ></blurb></b-card
                            ></b-card-group>
                            <br />
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Public Workflow Developers ({{
                                    publicWorkflowDevelopers.length
                                }})
                            </h5>
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
                                    v-for="user in publicWorkflowDevelopers"
                                    v-bind:key="user"
                                    ><b-row
                                        ><b-col
                                            ><b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :href="
                                                    `https://github.com/${user}`
                                                "
                                                ><i
                                                    class="fab fa-github fa-fw"
                                                ></i>
                                                {{ user }}</b-link
                                            ></b-col
                                        ><b-col md="auto">{{
                                            publicWorkflows.filter(
                                                wf =>
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
                            "
                            ><template #title
                                ><h1
                                    v-if="taskCount >= 0"
                                    class="text-success text-center"
                                >
                                    {{ taskCount }}
                                </h1>
                                <b-spinner
                                    v-else
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner
                                ><b-button
                                    :variant="
                                        activeTab === 2
                                            ? profile.darkMode
                                                ? 'outline-success'
                                                : 'success'
                                            : profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    v-b-tooltip.hover
                                    :title="`Tasks`"
                                    ><i class="fas fa-tasks fa-fw"></i>
                                    Tasks</b-button
                                ></template
                            ><Plotly
                                v-if="timeseriesTasks.length > 0"
                                :data="tasksPlotData"
                                :layout="tasksPlotLayout"
                            ></Plotly>
                            <br />
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
                            ></b-tab
                        >
                    </b-tabs>
                </b-col>
            </b-row>
            <br />
            <div id="map" style="height: 40rem"></div>
            <br />
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

export default {
    name: 'stats',
    components: {
        blurb,
        Plotly
    },
    data: function() {
        return {
            map: {},
            mapCenter: [0, 0],
            mapMarkers: [],
            mapPopup: null,
            userCount: -1,
            timeseriesUsers: [],
            timeseriesTasks: [],
            onlineCount: -1,
            workflowCount: -1,
            taskCount: -1,
            runningCount: -1,
            institutions: [],
            activeTab: 0
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
                zoom: 1
            });

            this.mapPopup = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false
            });

            var map = this.map;
            var popup = this.mapPopup;

            this.map.on('mouseenter', 'institutions', function(e) {
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
                popup
                    .setLngLat(coordinates)
                    .setHTML(html)
                    .addTo(map);
            });

            this.map.on('mouseleave', 'institutions', function() {
                map.getCanvas().style.cursor = '';
                popup.remove();
            });
        },
        async loadCounts() {
            await axios
                .get('/apis/v1/stats/counts/')
                .then(response => {
                    this.userCount = response.data.users;
                    this.onlineCount = response.data.online;
                    this.workflowCount = response.data.workflows;
                    this.taskCount = response.data.tasks;
                    this.runningCount = response.data.running;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadInstitutions() {
            await axios
                .get('/apis/v1/stats/institutions/')
                .then(response => {
                    this.institutions = response.data.institutions;
                    if (this.map) this.paintInstitutions();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadTimeseries() {
            await axios
                .get('/apis/v1/stats/timeseries/')
                .then(response => {
                    this.timeseriesUsers = [response.data.users];
                    this.timeseriesTasks = [response.data.tasks];
                })
                .catch(error => {
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
                    features: this.institutions.map(i => i.geocode)
                }
            });
            this.map.addLayer({
                id: 'institutions',
                type: 'circle',
                source: 'institutions',
                paint: {
                    'circle-color': '#4264fb',
                    'circle-radius': 6,
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#ffffff'
                }
            });
        }
    },
    // watch: {
    //     darkMode() {
    //         this.map.setStyle(
    //             `mapbox://styles/mapbox/${
    //                 this.profile.darkMode ? 'dark-v10' : 'light-v10'
    //             }`
    //         );
    //         this.unpaintInstitutions();
    //         this.paintInstitutions();
    //     }
    // },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', [
            'publicWorkflows',
            'publicWorkflowsLoading'
        ]),
        publicWorkflowDevelopers() {
            return Array.from(
                new Set(this.publicWorkflows.map(wf => wf.repo.owner.login))
            );
        },
        darkMode() {
            return this.profile.darkMode;
        },
        institutionPlotData() {
            return [
                {
                    x: Object.keys(this.institutions),
                    y: Object.values(this.institutions),
                    type: 'markers'
                }
            ];
        },
        institutionPlotLayout() {
            return {
                title: {
                    text: 'User Institutions',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff'
            };
        },
        usersPlotData() {
            return this.timeseriesUsers;
        },
        usersPlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                },
                autosize: true,
                height: 350,
                title: {
                    text: 'Total Users',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)'
                        }
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)'
                        }
                    }
                },
                yaxis: {
                    showticklabels: false
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff'
            };
        },
        tasksPlotData() {
            return this.timeseriesTasks;
        },
        tasksPlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                },
                autosize: true,
                title: {
                    text: 'Total Tasks',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)'
                        }
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)'
                        }
                    }
                },
                yaxis: {
                    showticklabels: false
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff'
            };
        }
    }
};
</script>

<style scoped></style>
