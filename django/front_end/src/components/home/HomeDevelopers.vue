<template>
    <b-container fluid class="m-0 p-4 center-container">
        <h1>DEVELOPERS</h1>
        <h4>We have made it so easy for you.</h4>

        <b-row class="m-5">
            <b-col lg="6">
                <b-row class="mb-5">
                    <b-col md="3" class="text-center">
                        <b-img
                            :src="
                                require('../../assets/frontpage/icons/algorithm.png')
                            "
                            width="100px"
                            alt="Algorithms"
                        ></b-img>
                    </b-col>
                    <b-col>
                        <h3>Focus on your algorithm</h3>
                        Plant IT automatically parallelizes the analysis across all
                        samples, allowing you to focus on your algorithms,
                        not logistics.
                    </b-col>
                </b-row>

                <b-row class="mb-5">
                    <b-col md="3" class="text-center">
                        <b-img
                            :src="
                                require('../../assets/frontpage/icons/UI.png')
                            "
                            width="100px"
                            alt="Algorithms"
                        ></b-img>
                    </b-col>
                    <b-col>
                        <h3>UI Included</h3>
                        Plant IT provides a UI to help users run the algorithms and set algorithm parameters.
                        Parameters are automatically validated and passed to your algorithm.
                    </b-col>
                </b-row>

                <b-row>
                    <b-col md="3" class="text-center">
                        <b-img
                            :src="
                                require('../../assets/frontpage/icons/code.png')
                            "
                            width="100px"
                            alt="Algorithms"
                        ></b-img>
                    </b-col>
                    <b-col>
                        <h3>No Need to Rewrite Your Existing Code</h3>
                        You can import libraries and run the analysis as python
                        code inside the PlantIT framework, or call
                        an external program.
                    </b-col>
                </b-row>
            </b-col>

            <b-col class="mt-5">
                <b-row class="mb-5">
                    <b-col md="3" class="text-center">
                        <b-img
                            :src="
                                require('../../assets/frontpage/icons/format.png')
                            "
                            width="100%"
                            alt="Algorithms"
                        ></b-img>
                    </b-col>
                    <b-col>
                        <h3>Autoformatted results</h3>
                        You choose what data to return to the user, then
                        Plant IT automatically collates the results across all samples.
                        Key-value pairs are return as a CSV, output files are organized by sample.
                    </b-col>
                </b-row>

                <b-row>
                    <b-col md="3" class="text-center">
                        <b-img
                            :src="
                                require('../../assets/frontpage/icons/documentation.png')
                            "
                            width="100%"
                            alt="Algorithms"
                        ></b-img>
                    </b-col>
                    <b-col>
                        <h3>You control the enviroment</h3>
                        You do not have to worry about
                        if the system your code is running on has all the
                        right libraries. All your algorithm code is run inside a
                        Singularity container you provide.
                    </b-col>
                </b-row>
            </b-col>
        </b-row>
    </b-container>
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
