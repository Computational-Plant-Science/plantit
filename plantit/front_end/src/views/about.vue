<template>
    <div>
        <br />
        <br />
        <b-container>
            <b-row>
                <b-col class="text-center"
                    ><h4
                        :class="profile.darkMode ? 'text-white' : 'text-theme'"
                        style="text-decoration: underline; z-index: 100"
                    >
                        <small>about</small>plant<small
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
            <b-row
                ><b-col>
                    <p>
                        plantIT is a science gateway for image-based plant
                        phenotyping. It was preceded by &mdash; grew out of, as
                        it were &mdash;
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
                    <p>
                        plantIT is free software-as-a-service for HPC/HTC
                        phenotyping in the browser. Registered users can access
                        and annotate data stored in the CyVerse cloud and submit
                        (possibly highly parallel) simulations and analyses to
                        clusters and supercomputers, no programming experience
                        required.
                    </p>
                    <p>
                        plantIT is also a platform-as-a-service for programmers
                        and developers, tightly integrated with GitHub and
                        Docker. Add a <code>plantit.yaml</code> file to any
                        public repository to integrate a container workflow,
                        allowing researchers to deploy your code to a cluster or
                        supercomputer with a few clicks.
                    </p>
                    <p>
                        plantIT makes a number of algorithms available by
                        default, including
                        <b-link
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            href="https://academic.oup.com/plphys/article/187/2/739/6317839"
                            >DIRT3D</b-link
                        >, a 3D root system reconstruction and analysis pipeline
                        (Liu et al 2021) and other trait analysis workflows.
                    </p>
                    <p>
                        plantIT is flexible enough to run most
                        container-friendly workflows, but if you want to do
                        genomics, a different tool (e.g.,
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
                        >) might be a better fit. Feel free to file bug reports,
                        make suggestions, request features
                        <b-link
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            href="https://github.com/Computational-Plant-Science/plantit"
                            >on GitHub</b-link
                        >, or
                        <b-link
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            href="https://github.com/Computational-Plant-Science/plantit/discussions"
                            >get in touch</b-link
                        >
                        regarding a use case.
                    </p>
                    <p>
                        plantIT is like glue: it sits between things and binds
                        them together. It is not any of the following
                        technologies (although it employs several internally):
                    </p>
                    <ul>
                        <li>
                            a pipeline framework (e.g.,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://snakemake.readthedocs.io/en/stable/"
                                >Snakemake</b-link
                            >,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://www.nextflow.io/"
                                >NextFlow</b-link
                            >,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://github.com/spotify/luigi"
                                >Luigi</b-link
                            >,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://airflow.apache.org/"
                                >AirFlow</b-link
                            >)
                        </li>
                        <li>
                            a machine learning automation platform (e.g.,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://metaflow.org/"
                                >MetaFlow</b-link
                            >)
                        </li>
                        <li>
                            a distributed queue or task scheduler (e.g.,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://docs.celeryproject.org/en/stable/index.html"
                                >Celery</b-link
                            >,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://dask.org/"
                                >Dask</b-link
                            >)
                        </li>
                        <li>
                            a batch-processing, streaming, or analytics platform
                            (e.g.,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://spark.apache.org/"
                                >Spark</b-link
                            >)
                        </li>
                        <li>
                            a container orchestrator or infrastructure-as-code
                            system (e.g.,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://kubernetes.io/"
                                >Kubernetes</b-link
                            >)
                        </li>
                        <li>
                            a cluster scheduler (e.g.,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://adaptivecomputing.com/cherry-services/torque-resource-manager/"
                                >Torque/Moab</b-link
                            >,
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-success'
                                        : 'text-dark'
                                "
                                href="https://slurm.schedmd.com/overview.html"
                                >SLURM</b-link
                            >)
                        </li>
                    </ul>
                </b-col>
            </b-row>
            <br />
            <br />
            <hr :style="profile.darkMode ? 'border-top: 1px solid #d6df5D' : 'border-top: 1px solid #212529'" />
            <br />
            <br />
            <b-row class="text-center">
                <b-col>
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Project Team
                    </h5>
                </b-col></b-row
            >
            <br />
            <b-row class="justify-content-md-center mb-4">
                <b-col class="justify-content-md-center">
                    <b-card-group deck columns>
                        <b-card
                            class="text-center"
                            style="min-width: 20rem"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            border-variant="transparent"
                            :footer-bg-variant="
                                profile.darkMode ? 'success' : 'white'
                            "
                            footer-border-variant="white"
                        >
                            <template #default>
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Alexander Bucksch
                                </h5>
                                <b
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Principal Investigator</b
                                >
                            </template>
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
                            class="text-center"
                            style="min-width: 20rem"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            border-variant="transparent"
                            :footer-bg-variant="
                                profile.darkMode ? 'success' : 'white'
                            "
                            footer-border-variant="white"
                            ><template #default>
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Suxing Liu
                                </h5>
                                <b
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Algorithm Developer</b
                                >
                            </template>
                            <template
                                v-slot:footer
                                style="background-color: white"
                            >
                                <b-button
                                    class="mr-2 p-2"
                                    variant="outline-dark"
                                    href="https://github.com/lsx1980"
                                >
                                    <i class="fab fa-github fa-2x success"></i>
                                </b-button>
                                <b-button
                                    variant="outline-dark"
                                    class="mr-2 p-2"
                                    href="https://www.researchgate.net/profile/Suxing-Liu-2"
                                >
                                    <i
                                        class="fab fa-researchgate fa-2x success"
                                    ></i>
                                </b-button>
                            </template>
                        </b-card>
                        <b-card
                            class="text-center"
                            style="min-width: 20rem"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            border-variant="transparent"
                            :footer-bg-variant="
                                profile.darkMode ? 'success' : 'white'
                            "
                            footer-border-variant="white"
                        >
                            <template #default>
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Wes Bonelli
                                </h5>
                                <b
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Platform Developer</b
                                >
                            </template>
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
                            class="text-center"
                            style="min-width: 10rem"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            border-variant="transparent"
                            :footer-bg-variant="
                                profile.darkMode ? 'success' : 'white'
                            "
                            footer-border-variant="white"
                        >
                          <template #default>
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Chris Cotter
                                </h5>
                                <b
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Platform Developer</b
                                >
                            </template>
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
                            class="text-center"
                            style="min-width: 10rem"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            border-variant="transparent"
                            :footer-bg-variant="
                                profile.darkMode ? 'success' : 'white'
                            "
                            footer-border-variant="white"
                        >
                          <template #default>
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Abhiram Das
                                </h5>
                                <b
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Platform Developer (DIRT)</b
                                >
                            </template>
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
                            class="text-center"
                            style="min-width: 10rem"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            border-variant="transparent"
                            :footer-bg-variant="
                                profile.darkMode ? 'success' : 'white'
                            "
                            footer-border-variant="white"
                        >
                          <template #default>
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Megan Flory
                                </h5>
                                <b
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Graphic Design</b
                                >
                            </template>
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
                            class="text-center"
                            style="min-width: 10rem"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            border-variant="transparent"
                            :footer-bg-variant="
                                profile.darkMode ? 'success' : 'white'
                            "
                            footer-border-variant="white"
                        >
                          <template #default>
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Maria Luck
                                </h5>
                                <b
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Graphic Design</b
                                >
                            </template>
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

export default {
    name: 'about',
    computed: {
        ...mapGetters('user', ['profile']),
    },
};
</script>

<style scoped></style>
