<template>
    <div>
        <b-card title="Develop...">
            <b-card-text>
                ...against a powerful PaaS (<i>Phenotyping</i>-as-a-Service) data science platform. Plug in your storage and
                compute resources or share time on the Computational Plant Science lab's own infrastructure free of charge.
                <b-container fluid class="m-0 p-4">
                    <b-row class="mb-5">
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
                            <b-card title="Workflow orchestration">
                                <b-card-text>
                                    Bootstrap your analyses with the following batteries-included frameworks:
                                    <br>
                                    <br>
                                    <b-list-group>
                                        <b-list-group-item>CookieCutter</b-list-group-item>
                                        <b-list-group-item>Dagster</b-list-group-item>
                                    </b-list-group>
                                    <br>
                                    Or build bespoke workflows: pipelines run in Singularity containers over
                                    which you have full control. If your code runs on Linux, it will run on
                                    PlantIT!
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
                            <b-card title="Execution and monitoring">
                                <b-card-text>
                                    Schedule pipelines or run them in real time from the web portal or RESTful
                                    API.
                                </b-card-text>
                            </b-card>
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
