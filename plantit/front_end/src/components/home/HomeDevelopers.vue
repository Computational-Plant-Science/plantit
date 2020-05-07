<template>
    <b-card
        class="rounded-0 text-center"
        bg-variant="dark"
        border-variant="success"
        text-variant="white"
        header-bg-variant="dark"
        header-border-variant="dark"
    >
        <template slot="header" style="border: none">
            <h2 class="text-success">Developers</h2>
            <p class="text-white">
                Share pipelines with a broad audience and advance reproducible
                science.
            </p>
        </template>
        <b-container>
            <b-row align-content="center" align-h="center">
                <b-col align-h="center">
                    <b-card
                        sub-title="Batteries included (but not required)"
                        sub-title-text-variant="success"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="dark"
                        text-variant="white"
                        :img-src="
                            require('../../assets/frontpage/icons/algorithm.png')
                        "
                        img-width="100px"
                        img-height="90px"
                        img-left
                        style="border: none;"
                    >
                        <b-card-text>
                            Store and publish data with
                            <b-link
                                class="text-white"
                                href="https://www.cyverse.org/"
                                >CyVerse</b-link
                            >
                            or plug in alternate data stores. Then deploy on
                            your own HPC/HTC cluster or request XSEDE resources
                            (like the University of Georgia's
                            <b-link
                                class="text-white"
                                href="https://gacrc.uga.edu/systems/"
                                >Sapelo2</b-link
                            >
                            or TACC's
                            <b-link
                                class="text-white"
                                href="https://www.tacc.utexas.edu/systems/stampede2"
                                >Stampede</b-link
                            >).
                        </b-card-text>
                    </b-card>
                </b-col>
            </b-row>
            <b-row class="mt-4">
                <b-col md="auto">
                    <b-card
                        sub-title="Workflow orchestration on the web"
                        sub-title-text-variant="success"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="dark"
                        text-variant="white"
                        :img-src="
                            require('../../assets/frontpage/icons/UI.png')
                        "
                        img-width="100px"
                        img-height="90px"
                        img-left
                        style="border: none;"
                    >
                        <b-card-text class="m-0 p-0">
                            Publish your algorithms to the community and empower
                            researchers everywhere. Run and monitor workflows
                            from the browser (or develop against the RESTful
                            API).
                        </b-card-text>
                    </b-card>
                </b-col>
            </b-row>
            <b-row class="mt-4">
                <b-col>
                    <b-card
                        sub-title="Full control over your environment"
                        sub-title-text-variant="success"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="dark"
                        text-variant="white"
                        :img-src="
                            require('../../assets/frontpage/icons/code.png')
                        "
                        img-width="100px"
                        img-height="90px"
                        img-left
                        style="border: none;"
                    >
                        <b-card-text>
                            Containerize existing code or develop custom
                            pipelines with your tools of choice. If it can run
                            in
                            <b-link
                                class="text-white"
                                href="https://sylabs.io/docs/"
                                >Singularity</b-link
                            >, it will run on PlantIT.
                        </b-card-text>
                    </b-card>
                </b-col>
            </b-row>
            <b-row class="mt-4">
                <b-col>
                    <b-card
                        sub-title="Phenotyping-as-a-Service"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="dark"
                        text-variant="white"
                        sub-title-text-variant="success"
                        :img-src="
                            require('../../assets/frontpage/icons/documentation.png')
                        "
                        img-width="100px"
                        img-height="90px"
                        img-left
                        style="border: none;"
                    >
                        <b-card-text>
                            Submit and validate workflow parameters from code or
                            browser, then get notified when results are
                            available.
                        </b-card-text>
                    </b-card>
                </b-col>
            </b-row>
        </b-container>
    </b-card>
</template>

<script>
export default {
    name: 'HomeDevelopers'
};
</script>

<style scoped lang="sass">
@import '../../scss/_colors.sass'

h1
    color: $color-highlight
</style>
