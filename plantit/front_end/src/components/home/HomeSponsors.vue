<template>
    <div>
        <b-card
            class="rounded-0"
            bg-variant="light"
            style="border:none"
            title="Sponsors"
        >
            <b-card-group columns>
                <b-card align="center" class="mr-4 mb-4">
                    <b-link href="http://www.computational-plant-science.org">
                        <b-img
                            :src="require('@/assets/sponsors/cps-black.png')"
                            height="75px"
                            alt="Computational Plant Science Lab"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card align="center" class="mr-4 mb-4">
                    <b-link href="http://www.cyverse.org/">
                        <b-img
                            :src="require('@/assets/sponsors/cyversebw.png')"
                            height="75px"
                            alt="Cyverse"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card align="center" class="mr-4 mb-4">
                    <b-link href="http://www.xsede.org/">
                        <b-img
                            :src="require('@/assets/sponsors/xsede.png')"
                            height="75px"
                            alt="XSEDE"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card align="center" class="mr-4 mb-4">
                    <b-link href="http://arpa-e.energy.gov/">
                        <b-img
                            :src="require('@/assets/sponsors/arpa_e.png')"
                            height="75px"
                            alt="ARPA-E"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card align="center" class="mr-4 mb-4">
                    <b-link href="http://www.uga.edu/">
                        <b-img
                            :src="require('@/assets/sponsors/uga.png')"
                            height="75px"
                            alt="University Of Georgia"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card align="center" class="mr-4 mb-4">
                    <b-link href="http://gacra.uga.edu/">
                        <b-img
                            :src="require('@/assets/sponsors/gacrc.png')"
                            height="75px"
                            alt="Georgia Advanced Computing Resource Center"
                        ></b-img>
                    </b-link>
                </b-card>
            </b-card-group>
        </b-card>
    </div>
</template>

<script>
export default {
    name: 'HomeSponsors'
};
</script>

<style lang="sass" scoped>
@import '../../scss/_colors.sass'

h1
    color: $color-highlight

.sponsors
    text-align: center

.sponsors > .col
    padding-top: 30px
</style>
