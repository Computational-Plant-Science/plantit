<template>
    <b-card
        class="rounded-0"
        bg-variant="light"
        sub-title-text-variant="secondary"
        title="Developers"
        sub-title="Share pipelines with a broad audience and advance reproducible science."
    >
        <b-container class="p-2 pt-4">
            <b-row class="mt-2">
                <b-col>
                    <b-card
                        title="Deploy existing code at scale"
                        class="text-left rounded-0 overflow-hidden"
                        bg-variant="light"
                        text-variant="dark"
                        :img-src="
                            require('../../assets/frontpage/icons/code.png')
                        "
                        img-width="100px"
                        img-height="90px"
                        img-left
                        style="border: none"
                    >
                        <b-card-text>
                            Develop custom pipelines with your tools of choice,
                            then upload them as Singularity containers.
                        </b-card-text>
                    </b-card>
                </b-col>
                <b-col>
                    <b-card
                        title="Orchestrate workflows from the browser"
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
                        <b-card-text>
                            Run pipelines and inspect results from the PlantIT
                            portal (or develop against the RESTful API).
                        </b-card-text>
                    </b-card>
                </b-col>
            </b-row>
            <b-row class="mt-4">
                <b-col>
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
                            >, then plug in your compute resources (or request
                            time on the University of Georgia's
                            <b-link href="https://gacrc.uga.edu/systems/"
                                >Sapelo2</b-link
                            >
                            cluster or TACC's Stampede.)
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
