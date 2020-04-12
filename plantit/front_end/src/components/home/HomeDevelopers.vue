<template>
    <div>
        <b-card title="What is PlantIT?">
            <b-card-text>
                PlantIT is a <b>Phenotyping</b>-as-a-Service platform for computational plant biologists.
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
                                title="Access data and run code where *you* want to."
                            >
                                <b-card-text>
                                    Plug in your own storage and compute resources or share time on the Computational Plant Science lab's own infrastructure, free of charge.
                                </b-card-text>
                            </b-card>
                        </b-col>
                    </b-row>
                    <b-row class="mt-4">
                        <b-col md="auto" class="text-center">
                            <b-img
                                :src="
                                    require('../../assets/frontpage/icons/code.png')
                                "
                                width="100px"
                                alt="Algorithms"
                            ></b-img>
                        </b-col>
                        <b-col>
                            <b-card title="Deploy, version, and reproduce existing workflows.">
                                <b-card-text>
                                    PlantIT pipelines run in Singularity containers. There's no need to rewrite existing code: if it can run in a container, it will run on PlantIT!
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
                            <b-card title="Orchestrate analyses from your browser.">
                                <b-card-text>
                                    Run and introspect pipelines from the PlantIT portal (or RESTful API).
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
