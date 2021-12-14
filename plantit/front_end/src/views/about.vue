<template>
    <div>
        <br />
        <br />
        <b-container>
            <b-row>
                <b-col class="text-center"
                    ><b-img
                        style="max-width: 5rem; transform: translate(0px, 20px)"
                        :src="require('../assets/logo.png')"
                        center
                        class="m-0 p-0 mb-1"
                    ></b-img>
                    <h1 class="text-dark" style="text-decoration: underline">
                        plant<small
                            class="mb-3 text-success"
                            style="
                                text-decoration: underline;
                                text-shadow: 1px 1px 2px black;
                            "
                            >it</small
                        >
                    </h1>
                </b-col>
            </b-row>
            <br />
            <b-row
                ><b-col>
                    <b-img
                        :src="require('../assets/about/summary.png')"
                        center
                        style="max-width: 69rem"
                    ></b-img>
                    <br />
                    <p>
                        <b
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            style="text-decoration: underline"
                        >
                            plant<small
                                class="mb-3 text-success"
                                style="
                                    text-decoration: underline;
                                    text-shadow: 1px 0 0 #000, 0 -1px 0 #000,
                                        0 1px 0 #000, -1px 0 0 #000;
                                "
                                >IT</small
                            >
                        </b>
                        is a science gateway for plant phenotyping. It was
                        preceded by &mdash; grew out of, as it were &mdash;
                        <b-link
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            href="http://dirt.cyverse.org/?q=welcome"
                            >DIRT</b-link
                        >
                        (<b>D</b>igital <b>I</b>maging of <b>R</b>oot
                        <b>T</b>raits), which measures traits of monocot and
                        dicot roots from user-uploaded images, making
                        high-throughput grid computing available via a web
                        portal.
                    </p>
                    <br />
                    <b-img
                        :src="require('../assets/about/features.png')"
                        center
                        style="max-width: 69rem"
                    ></b-img>
                    <br />
                    <p>
                        <b
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            style="text-decoration: underline"
                        >
                            plant<small
                                class="mb-3 text-success"
                                style="
                                    text-decoration: underline;
                                    text-shadow: 1px 0 0 #000, 0 -1px 0 #000,
                                        0 1px 0 #000, -1px 0 0 #000;
                                "
                                >IT</small
                            >
                        </b>
                        is software-as-a-service for farmers, biologists,
                        breeders, and anyone else aiming to automate the
                        collection and analysis of phenotype data. Store,
                        publish, and access data with CyVerse, and run
                        simulations and analyses on clusters from a browser, no
                        programming experience required.
                    </p>
                    <br />
                    <b-img
                        :src="require('../assets/about/examples.png')"
                        center
                        style="max-width: 69rem"
                    ></b-img>
                    <br />
                    <p>
                        <b
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            style="text-decoration: underline"
                        >
                            plant<small
                                class="mb-3 text-success"
                                style="
                                    text-decoration: underline;
                                    text-shadow: 1px 0 0 #000, 0 -1px 0 #000,
                                        0 1px 0 #000, -1px 0 0 #000;
                                "
                                >IT</small
                            >
                        </b>
                        is also a platform-as-a-service for programmers and
                        software developers, tightly integrated with GitHub and
                        Docker. Just add a <code>plantit.yaml</code> file to
                        your repository, then anyone can deploy a container with
                        your code to a cluster or supercomputer with a few
                        clicks.
                    </p>
                    <br />
                    <b-img
                        :src="require('../assets/about/configuring.png')"
                        center
                        style="max-width: 69rem"
                    ></b-img>
                    <br />
                    <p>
                        <b
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            style="text-decoration: underline"
                        >
                            plant<small
                                class="mb-3 text-success"
                                style="
                                    text-decoration: underline;
                                    text-shadow: 1px 0 0 #000, 0 -1px 0 #000,
                                        0 1px 0 #000, -1px 0 0 #000;
                                "
                                >IT</small
                            >
                        </b>
                        is like glue. It sits between things and binds them
                        together. It is <i class="text-danger">not</i> itself
                        any of these things, however:
                    </p>

                    <b-list-group
                        ><b-list-group-item
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            >a pipeline framework (e.g.,
                            <b-link
                                class="text-dark"
                                href="https://snakemake.readthedocs.io/en/stable/"
                                >Snakemake</b-link
                            >,
                            <b-link
                                class="text-dark"
                                href="https://www.nextflow.io/"
                                >NextFlow</b-link
                            >,
                            <b-link
                                class="text-dark"
                                href="https://github.com/spotify/luigi"
                                >Luigi</b-link
                            >,
                            <b-link
                                class="text-dark"
                                href="https://airflow.apache.org/"
                                >AirFlow</b-link
                            >)</b-list-group-item
                        ><b-list-group-item
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            >a machine learning automation platform (e.g.,
                            <b-link
                                class="text-dark"
                                href="https://metaflow.org/"
                                >MetaFlow</b-link
                            >)</b-list-group-item
                        >
                        <b-list-group-item
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            >a distributed queue or task scheduler (e.g.,
                            <b-link
                                class="text-dark"
                                href="https://docs.celeryproject.org/en/stable/index.html"
                                >Celery</b-link
                            >,
                            <b-link class="text-dark" href="https://dask.org/"
                                >Dask</b-link
                            >)</b-list-group-item
                        ><b-list-group-item
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            >a batch-processing, streaming, or analytics
                            platform (e.g.,
                            <b-link
                                class="text-dark"
                                href="https://spark.apache.org/"
                                >Spark</b-link
                            >)</b-list-group-item
                        ><b-list-group-item
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            >a container orchestrator or infrastructure-as-code
                            system (e.g.,
                            <b-link
                                class="text-dark"
                                href="https://kubernetes.io/"
                                >Kubernetes</b-link
                            >)</b-list-group-item
                        ><b-list-group-item
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            >a cluster scheduler (e.g.,
                            <b-link
                                class="text-dark"
                                href="https://adaptivecomputing.com/cherry-services/torque-resource-manager/"
                                >Torque/Moab</b-link
                            >,
                            <b-link
                                class="text-dark"
                                href="https://slurm.schedmd.com/overview.html"
                                >SLURM</b-link
                            >)</b-list-group-item
                        ></b-list-group
                    >
                    <br />
                    <p>
                        <b
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            style="text-decoration: underline"
                        >
                            plant<small
                                class="mb-3 text-success"
                                style="
                                    text-decoration: underline;
                                    text-shadow: 1px 0 0 #000, 0 -1px 0 #000,
                                        0 1px 0 #000, -1px 0 0 #000;
                                "
                                >IT</small
                            >
                        </b>
                        is flexible enough to run most container-friendly
                        workflows, but if you want to do genomics, a tool like
                        <b-link
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            href="https://genomevolution.org/CoGe/"
                            >CoGe</b-link
                        >
                        or
                        <b-link
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            href="https://easygwas.ethz.ch/"
                            >easyGWAS</b-link
                        >
                        might be a better fit. Feel free to
                        <b-link
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            href="https://github.com/Computational-Plant-Science/plantit/discussions"
                            >get in touch</b-link
                        >
                        with questions about your use case, file a bug report,
                        make a suggestion, or request a feature.
                    </p>
                </b-col>
            </b-row>
            <br />
            <b-row align-v="center" class="justify-content-md-center">
                <b-col
                    ><b-img
                        center
                        style="
                            max-width: 15rem;
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
            <b-row class="text-center">
                <b-col>
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Development Team
                    </h5>
                </b-col></b-row
            >
            <br />
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    <b-card-group deck columns>
                        <b-card
                            bg-variant="white"
                            footer-bg-variant="white"
                            footer-border-variant="white"
                            border-variant="white"
                            sub-title-text-variant="dark"
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
                                    <i class="fab fa-github fa-2x success"></i>
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
                            sub-title-text-variant="dark"
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
                                    <i class="fab fa-github fa-2x success"></i>
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
                <b-col>
                    <b-card-group deck columns>
                        <b-card
                            bg-variant="white"
                            sub-title-text-variant="dark"
                            footer-bg-variant="white"
                            footer-border-variant="white"
                            text-variant="dark"
                            border-variant="white"
                            title="Chris Cotter"
                            sub-title="Developer"
                            style="min-width: 10rem"
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
                                    <i class="fab fa-github fa-2x success"></i>
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
                            sub-title-text-variant="dark"
                            title="Abhiram Das"
                            sub-title="Developer (DIRT)"
                            style="min-width: 10rem"
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
                            sub-title-text-variant="dark"
                            title="Megan Flory"
                            sub-title="Designer"
                            style="min-width: 10rem"
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
                                    <i class="fab fa-github fa-2x success"></i>
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
                            sub-title-text-variant="dark"
                            title="Maria Luck"
                            sub-title="Developer"
                            style="min-width: 10rem"
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
                </b-col>
            </b-row>
            <br />
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'about',
    computed: {
        ...mapGetters('user', ['profile']),
    },
};
</script>

<style scoped></style>
