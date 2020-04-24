<template>
    <b-card
        class="rounded-0"
        bg-variant="light"
        sub-title-text-variant="secondary"
        title="Developers"
        sub-title="Share pipelines with a broad audience and advance reproducible science."
    >
        <b-container class="p-0 m-0" fluid="true">
            <b-row align-v="center" align-content="center" class="mt-4">
                <b-col md="auto">
                    <b-card
                        title="Batteries included (but not required)"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="light"
                        text-variant="dark"
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
                            <b-link href="https://www.cyverse.org/"
                                >CyVerse</b-link
                            >
                            or plug in alternative data stores. Then deploy on
                            your own HPC/HTC infrastructure or request time on
                            XSEDE resources (like the University of Georgia's
                            <b-link href="https://gacrc.uga.edu/systems/"
                                >Sapelo2</b-link
                            >
                            or TACC's
                            <b-link
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
                        title="Workflow orchestration on the web"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="light"
                        text-variant="dark"
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
                        title="Full control over your environment"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="light"
                        text-variant="dark"
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
                            <b-link href="https://sylabs.io/docs/"
                                >Singularity</b-link
                            >, it will run on PlantIT.
                        </b-card-text>
                    </b-card>
                </b-col>
            </b-row>
            <b-row class="mt-4">
                <b-col>
                    <b-card
                        title="Phenotyping-as-a-Service"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="light"
                        text-variant="dark"
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
