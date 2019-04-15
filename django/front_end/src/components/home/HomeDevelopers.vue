<template>
    <b-container fluid class="m-0 p-4 center-container">
        <h1>DEVELOPERS</h1>
        We've made it so easy for you.

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
                        <h3>Focus on your algorithm.</h3>
                        Plant IT automatically paraleizes the analysi across all
                        samples, allowing devlopers to fous on thier alogrithms,
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
                        <h3>Focus on your algorithm.</h3>
                        Plant IT automatically paraleizes the analysi across all
                        samples, allowing devlopers to fous on thier alogrithms,
                        not logistics.
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
                        <h3>Focus on your algorithm.</h3>
                        Plant IT automatically paraleizes the analysi across all
                        samples, allowing devlopers to fous on thier alogrithms,
                        not logistics.
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
                        <h3>Focus on your algorithm.</h3>
                        Plant IT automatically paraleizes the analysi across all
                        samples, allowing devlopers to fous on thier alogrithms,
                        not logistics.
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
                        <h3>Focus on your algorithm.</h3>
                        Plant IT automatically paraleizes the analysi across all
                        samples, allowing devlopers to fous on thier alogrithms,
                        not logistics.
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
