<template>
    <div>
        <br />
        <br />
        <b-container>
            <b-row>
                <b-col class="text-center"
                    ><h4
                        class="text-white"
                        style="text-decoration: underline; z-index: 100"
                    >
                        <b-img
                            style="
                                max-width: 2.5rem;
                                position: relative;
                                left: 5px;
                            "
                            :src="require('../assets/logo.png')"
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
                        >
                    </h4>
                </b-col>
            </b-row>
            <br />
            <b-row class="text-light lightlinks"
                ><b-col>
                    <p>
                        <b-img
                            style="
                                max-width: 1.5rem;
                                position: relative;
                                top: -3px;
                            "
                            :src="require('../assets/logo.png')"
                            class="m-0 p-0"
                        ></b-img>
                        free service for image-based plant phenotyping
                        automation. Registered users can access and annotate
                        data stored in the CyVerse cloud and submit (possibly
                        highly parallel) trait extraction pipelines,
                        simulations, or other tasks to clusters and
                        supercomputers, no programming experience required. It's
                        also a platform-as-a-service for developers, closely
                        integrated with GitHub and Docker. Add a
                        <code>plantit.yaml</code> file to any public repository
                        to integrate a container workflow, allowing researchers
                        to deploy it to a cluster or supercomputer with a few
                        clicks.
                    </p>
                    <p>
                        <b-img
                            style="
                                max-width: 1.5rem;
                                position: relative;
                                top: -3px;
                            "
                            :src="require('../assets/logo.png')"
                            class="m-0 p-0"
                        ></b-img>
                        preceded by &mdash; grew out of, as it were &mdash;
                        <b-link href="http://dirt.cyverse.org/?q=welcome"
                            >DIRT</b-link
                        >
                        (<b>D</b>igital <b>I</b>maging of <b>R</b>oot
                        <b>T</b>raits), which measures traits of monocot and
                        dicot roots from user-uploaded images, making
                        high-throughput grid computing available via a web
                        portal. A number of algorithms are freely available by
                        default, including the original <b>DIRT</b> as well as
                        <b-link
                            href="https://github.com/Computational-Plant-Science/3D_model_reconstruction_demo"
                            >DIRT3D</b-link
                        >, a 3D root system reconstruction and analysis pipeline
                        <b-link
                            href="https://academic.oup.com/plphys/article/187/2/739/6317839"
                            >(Liu et al 2021)</b-link
                        >.
                    </p>
                    <p>
                        <b-img
                            style="
                                max-width: 1.5rem;
                                position: relative;
                                top: -3px;
                            "
                            :src="require('../assets/logo.png')"
                            class="m-0 p-0"
                        ></b-img>
                        like glue: sitting between things, binding them
                        together. It is not any of the following technologies
                        (although it employs several internally):
                    </p>
                    <ul>
                        <li>
                            a workflow management framework or distributed task
                            queue (e.g.,
                            <b-link
                                href="https://snakemake.readthedocs.io/en/stable/"
                                >Snakemake</b-link
                            >,
                            <b-link href="https://www.nextflow.io/"
                                >NextFlow</b-link
                            >,
                            <b-link href="https://github.com/spotify/luigi"
                                >Luigi</b-link
                            >,
                            <b-link href="https://airflow.apache.org/"
                                >AirFlow</b-link
                            >,
                            <b-link
                                href="https://docs.celeryproject.org/en/stable/index.html"
                                >Celery</b-link
                            >, <b-link href="https://dask.org/">Dask</b-link>)
                        </li>
                        <li>
                            a machine learning automation platform (e.g.,
                            <b-link href="https://metaflow.org/"
                                >MetaFlow</b-link
                            >)
                        </li>
                        <li>
                            a batch-processing, streaming, or analytics platform
                            (e.g.,
                            <b-link href="https://spark.apache.org/"
                                >Spark</b-link
                            >)
                        </li>
                        <li>
                            a container orchestrator (e.g.,
                            <b-link href="https://kubernetes.io/"
                                >Kubernetes</b-link
                            >)
                        </li>
                        <li>
                            a cluster scheduler (e.g.,
                            <b-link
                                href="https://adaptivecomputing.com/cherry-services/torque-resource-manager/"
                                >Torque/Moab</b-link
                            >,
                            <b-link
                                href="https://slurm.schedmd.com/overview.html"
                                >SLURM</b-link
                            >)
                        </li>
                    </ul>
                    <p>
                        <b-img
                            style="
                                max-width: 1.5rem;
                                position: relative;
                                top: -3px;
                            "
                            :src="require('../assets/logo.png')"
                            class="m-0 p-0"
                        ></b-img>
                        flexible enough to run most bioinformatics workflows,
                        but if you want to do genomics, a different tool (e.g.,
                        <b-link href="https://genomevolution.org/CoGe/"
                            >CoGe</b-link
                        >
                        or
                        <b-link href="https://easygwas.ethz.ch/"
                            >easyGWAS</b-link
                        >) might be a better fit. Feel free to file bug reports,
                        make suggestions, request features
                        <b-link
                            href="https://github.com/Computational-Plant-Science/plantit"
                            >on GitHub</b-link
                        >, or
                        <b-link
                            href="https://github.com/Computational-Plant-Science/plantit/discussions"
                            >get in touch</b-link
                        >
                        regarding a use case.
                    </p>
                    <p>
                        <i
                            ><b>note:</b> developers make no guarantees
                            regarding the products of analyses performed on the
                            platform. Researchers must ensure the validity of
                            their own results.</i
                        >
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
                                <h5 class="text-white">{{ contrib.name }}</h5>
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
                                    <i class="fab fa-github fa-2x text-warning"></i>
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
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Former Contributors
                    </h5>
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
                                <h5 class="text-white">{{ contrib.name }}</h5>
                                <b class="text-white">{{ contrib.role }}</b>
                            </template>
                        </b-card>
                    </b-card-group>
                    <br />
                    <br />
                </b-col>
            </b-row>
            <br />
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
                        :src="
                            profile.darkMode
                                ? require('../assets/cps2.png')
                                : require('../assets/cps_black.png')
                        "
                        class="m-0 p-0"
                    ></b-img
                ></b-col>
            </b-row>
            <br />
            <br />
            <br />
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'about',
    data: function () {
        return {
            contributors: [],
        };
    },
    created: async function () {
        await this.loadContributors();
    },
    computed: {
        ...mapGetters('user', ['profile']),
        currentContributors() {
            return this.contributors.filter((c) => !c.former);
        },
        formerContributors() {
            return this.contributors.filter((c) => c.former);
        },
    },
    methods: {
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
};
</script>
<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'

.vertical-center
    min-height: 100%
    /* Fallback for browsers do NOT support vh unit */
    min-height: 100vh
    /* These two lines are counted as one :-)       */

    display: flex
    align-items: center
</style>
