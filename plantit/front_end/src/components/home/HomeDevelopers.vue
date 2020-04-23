<template>
    <div>
        <b-card
            class="text-center rounded-0"
            bg-variant="dark"
            text-variant="white"
        >
            <b-card-text>
                <b-container fluid class="p-2">
                    <b-row class="mt-2">
                        <b-col>
                            <b-card
                                title="Deploy existing code at scale"
                                class="text-left rounded-0 overflow-hidden"
                                bg-variant="dark"
                                text-variant="light"
                                :img-src="
                                    require('../../assets/frontpage/icons/code.png')
                                "
                                img-width="100px"
                                img-height="90px"
                                img-left
                                style="border: none"
                            >
                                <b-card-text>
                                    Develop custom pipelines with your tools of
                                    choice, then upload them as Singularity
                                    containers.
                                </b-card-text>
                            </b-card>
                        </b-col>
                        <b-col>
                            <b-card
                                title="Orchestrate workflows from the browser"
                                class="text-left rounded-0 overflow-hidden"
                                bg-variant="dark"
                                text-variant="light"
                                :img-src="
                                    require('../../assets/frontpage/icons/UI.png')
                                "
                                img-width="100px"
                                img-height="90px"
                                img-left
                                style="border: none"
                            >
                                <b-card-text>
                                    Run pipelines and inspect results from the
                                    PlantIT portal (or develop against the
                                    RESTful API).
                                </b-card-text>
                            </b-card>
                        </b-col>
                    </b-row>
                    <b-row class="mt-4">
                        <b-col>
                            <b-card
                                title="Batteries included (but not required)"
                                class="text-left rounded-0 overflow-hidden"
                                bg-variant="dark"
                                text-variant="light"
                                :img-src="
                                    require('../../assets/frontpage/icons/algorithm.png')
                                "
                                img-width="100px"
                                img-height="90px"
                                img-left
                                style="border: none"
                            >
                                <b-card-text>
                                    Store and publish data with
                                    <b-link href="https://www.cyverse.org/"
                                        >CyVerse</b-link
                                    >, then plug in your compute resources (or request
                                    time on the University of Georgia's
                                    <b-link
                                        href="https://gacrc.uga.edu/systems/"
                                        >Sapelo2</b-link
                                    > cluster or TACC's Stampede.)
                                </b-card-text>
                            </b-card>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <b-img
                                center
                                fluid
                                :src="
                                    require('@/assets/frontpage/icons/hex1.png')
                                "
                                alt="Plant IT"
                            ></b-img>
                        </b-col>
                    </b-row>
                    <b-row>
                        <!--
                        <b-card align="center" class="mr-4 mb-4">
                            <b-col>
                                <b-link
                                    href="http://www.computational-plant-science.org"
                                >
                                    <b-img
                                        :src="
                                            require('@/assets/sponsors/cps-black.png')
                                        "
                                        height="100px"
                                        alt="Computational Plant Science Lab"
                                    ></b-img>
                                </b-link>
                            </b-col>
                        </b-card>
                        <b-card align="center" class="mr-4 mb-4">
                            <b-col>
                                <b-link href="http://www.cyverse.org/">
                                    <b-img
                                        :src="
                                            require('@/assets/sponsors/cyversebw.png')
                                        "
                                        height="100px"
                                        alt="Cyverse"
                                    ></b-img>
                                </b-link>
                            </b-col>
                        </b-card>
                        <b-card align="center" class="mr-4 mb-4">
                            <b-col>
                                <b-link href="http://www.xsede.org/">
                                    <b-img
                                        :src="
                                            require('@/assets/sponsors/xsede.png')
                                        "
                                        height="100px"
                                        alt="XSEDE"
                                    ></b-img>
                                </b-link>
                            </b-col>
                        </b-card>
                        <b-card align="center" class="mr-4 mb-4">
                            <b-col>
                                <b-link href="http://arpa-e.energy.gov/">
                                    <b-img
                                        :src="
                                            require('@/assets/sponsors/arpa_e.png')
                                        "
                                        height="100px"
                                        alt="ARPA-E"
                                    ></b-img>
                                </b-link>
                            </b-col>
                        </b-card>
                        <b-card align="center" class="mr-4 mb-4">
                            <b-col>
                                <b-link href="http://www.uga.edu/">
                                    <b-img
                                        :src="
                                            require('@/assets/sponsors/uga.png')
                                        "
                                        height="100px"
                                        alt="University Of Georgia"
                                    ></b-img>
                                </b-link>
                            </b-col>
                        </b-card>
                        <b-card align="center" class="mr-4 mb-4">
                            <b-col>
                                <b-link href="http://gacra.uga.edu/">
                                    <b-img
                                        :src="
                                            require('@/assets/sponsors/gacrc.png')
                                        "
                                        height="100px"
                                        alt="Georgia Advanced Computing Resource Center"
                                    ></b-img>
                                </b-link>
                            </b-col>
                        </b-card>
                        -->
                    </b-row>
                </b-container>
            </b-card-text>
        </b-card>
    </div>
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
