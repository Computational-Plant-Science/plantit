<template>
    <div>
        <b-card title="What is PlantIT?">
            <b-card-text>
                PlantIT is a <b>Phenomics</b>-as-a-Service platform for computational plant biologists.
                <b-container fluid class="p-2">
                    <b-row class="mt-4">
                        <b-col md="auto" class="text-center">
                            <b-img
                                :src="
                                    require('../../assets/frontpage/icons/algorithm.png')
                                "
                                width="100px"
                                alt="Algorithms"
                            ></b-img>
                        </b-col>
                        <b-col>
                            <b-card
                                title="Batteries included, but not required"
                            >
                                <b-card-text>
                                    To get up and running quickly, store and publish data with <b-link to="https://www.cyverse.org/">CyVerse</b-link> and run your workflows on the University of Georgia's <b-link to="https://gacrc.uga.edu/systems/">HPC cluster</b-link> (for free). Alternatively, plug in your own storage and compute resources.
                                </b-card-text>
                            </b-card>
                        </b-col>
                    </b-row>
                    <b-row class="mt-4">
                        <b-col md="auto">
                            <b-img
                                :src="
                                    require('../../assets/frontpage/icons/code.png')
                                "
                                width="100px"
                                alt="Algorithms"
                            ></b-img>
                        </b-col>
                        <b-col>
                            <b-card title="Deploy reproducible code at scale">
                                <b-card-text>
                                    Developers are free to use the tools and environments of their choice. Pipelines run in Singularity containers: if your code can be packaged with Docker, it will run on PlantIT.
                                </b-card-text>
                            </b-card>
                        </b-col>
                        <b-col md="auto" class="text-center">
                            <b-img
                                :src="
                                    require('../../assets/frontpage/icons/UI.png')
                                "
                                width="100px"
                                alt="Algorithms"
                            ></b-img>
                        </b-col>
                        <b-col>
                            <b-card title="Orchestrate workflows from the browser">
                                <b-card-text>
                                    Run and inspect the results of pipelines from the PlantIT portal (or develop against the API).
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
