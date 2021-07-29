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
                        ><small class="ml-1">usage</small>
                    </h1>
                </b-col>
            </b-row>
            <br />
            <b-row>
                <b-col align-self="end" class="text-right mr-0"
                    ><h1 v-if="userCount >= 0" class="text-success">
                        {{ userCount }}
                    </h1>
                    <b-spinner
                        v-else
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner
                ></b-col>
                <b-col align-self="end" class="text-left ml-0 pl-0"
                    ><h5 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                        <i class="fas fa-user fa-fw"></i> Users
                    </h5>
                </b-col>
                <b-col align-self="end" class="text-right mr-0"
                    ><h1 v-if="onlineCount >= 0" class="text-success">
                        {{ onlineCount }}
                    </h1>
                    <b-spinner
                        v-else
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner
                ></b-col>
                <b-col align-self="end" class="text-left ml-0 pl-0"
                    ><h5 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                        <i class="fas fa-signal fa-fw"></i> Online
                    </h5>
                </b-col>
                <b-col align-self="end" class="text-right mr-0"
                    ><h1 v-if="workflowCount >= 0" class="text-success">
                        {{ workflowCount }}
                    </h1>
                    <b-spinner
                        v-else
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner
                ></b-col>
                <b-col align-self="end" class="text-left ml-0 pl-0"
                    ><h4 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                        <i class="fas fa-stream fa-fw"></i> Workflows
                    </h4>
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
                    ><h4 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                        <i class="fas fa-tasks fa-fw"></i> Tasks
                    </h4>
                </b-col>
            </b-row>
            <br />
            <div id="map" style="height: 40rem"></div>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import mapboxgl from 'mapbox-gl';

export default {
    name: 'usage',
    data: function() {
        return {
            map: {},
            mapCenter: [0, 0],
            mapMarkers: [],
            mapPopup: null,
            userCount: -1,
            onlineCount: -1,
            workflowCount: -1,
            taskCount: -1,
            institutions: []
        };
    },
    async mounted() {
        await this.loadCounts();
        await this.loadInstitutions();

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
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
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
    methods: {
        loadCounts() {
            axios
                .get('/apis/v1/stats/counts/')
                .then(response => {
                    this.userCount = response.data.users;
                    this.onlineCount = response.data.online;
                    this.workflowCount = response.data.workflows;
                    this.taskCount = response.data.tasks;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        loadInstitutions() {
            axios
                .get('/apis/v1/stats/institutions/')
                .then(response => {
                    this.institutions = response.data.institutions;
                    this.paintInstitutions();
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
        }
    }
};
</script>

<style scoped></style>
