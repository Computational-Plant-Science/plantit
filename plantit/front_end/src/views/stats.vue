<template>
    <div>
        <br />
        <br />
        <b-container>
            <b-row>
                <b-col class="text-center"
                    ><b-img
                        style="max-width: 5rem;transform: translate(0px, 20px);"
                        :src="require('../assets/logo.png')"
                        center
                        class="m-0 p-0 mb-1"
                    ></b-img>
                    <h1
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        style="text-decoration: underline;"
                    >
                        plant<small
                            class="mb-3 text-success"
                            style="text-decoration: underline;text-shadow: 1px 0 0 #000, 0 -1px 0 #000, 0 1px 0 #000, -1px 0 0 #000;"
                            >IT</small
                        >
                    </h1>
                    Stats
                </b-col>
            </b-row>
            <br />
            <b-row
                ><b-col
                    ><Plotly
                        v-if="institutions.length > 0"
                        :data="institutionPlotData"
                        :layout="institutionPlotLayout"
                    ></Plotly></b-col
            ></b-row>
            <div id="map"></div>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { Plotly } from 'vue-plotly';
import mapboxgl from 'mapbox-gl';
import mapboxSdk from '@mapbox/mapbox-sdk';
// import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';

export default {
    name: 'stats',
    components: {
        Plotly
    },
    data: function() {
        return {
            map: {},
            mapCenter: [0, 0],
            mapboxToken: 'pk.eyJ1Ijoidy1ib25lbGxpIiwiYSI6ImNrcTcxNWk3MDAxbnAyb252eHBrazl4M2YifQ.MX_60RJeRuTGu4hQxPsWWw', // process.env.VUE_APP_MAPBOX_TOKEN,
            userCount: -1,
            workflowCount: -1,
            taskCount: -1,
            institutions: []
        };
    },
    async mounted() {
        await this.loadCounts();
        await this.loadInstitutions();

        mapboxgl.accessToken = this.mapboxToken;
        var mapboxClient = mapboxSdk({ accessToken: mapboxgl.accessToken });

        this.map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v11',
            center: this.mapCenter,
            zoom: 10
        });

        // let geocoder = new MapboxGeocoder({
        //     accessToken: this.access_token,
        //     mapboxgl: mapboxgl,
        //     marker: false
        // });

        mapboxClient.geocoding
            .forwardGeocode({
                query: 'Wellington, New Zealand',
                autocomplete: false,
                limit: 1
            })
            .send()
            .then(function(response) {
                if (
                    response &&
                    response.body &&
                    response.body.features &&
                    response.body.features.length
                ) {
                    var feature = response.body.features[0];
                    new mapboxgl.Marker()
                        .setLngLat(feature.center)
                        .addTo(this.map);
                }
            });
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
        },
        loadInstitutions() {
            axios
                .get('/apis/v1/stats/institutions/')
                .then(response => {
                    this.institutions = response.data.institutions;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        }
    },
    computed: {
        ...mapGetters('user', ['profile']),
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
                    text: 'Represented Institutions',
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
