<template>
    <b-container>
        <b-card
            align="center"
            class="rounded-0 text-center"
            bg-variant="white"
            border-variant="default"
            style="border:none"
            header-bg-variant="white"
            header-border-variant="white"
        >
            <template slot="header" style="border: none">
                <br />
                <br />
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col>
                        <b-img
                            style="max-width: 5rem;transform: translate(0px, 20px);"
                            :src="require('../../assets/logo.png')"
                            center
                            class="m-0 p-0"
                        ></b-img>
                        <h1>
                            Sponsors
                        </h1>
                        <br />
                    </b-col>
                </b-row>
            </template>
            <b-card-group columns>
                <b-card
                    align="right"
                    bg-variant="transparent"
                    border-variant="white"
                >
                    <b-link href="http://www.computational-plant-science.org">
                        <b-img
                            :src="require('@/assets/sponsors/cps-black.png')"
                            height="50px"
                            alt="Computational Plant Science Lab"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="right"
                    bg-variant="transparent"
                    border-variant="white"
                >
                    <b-link href="http://www.cyverse.org/">
                        <b-img
                            :src="require('@/assets/sponsors/cyversebw.png')"
                            height="40px"
                            alt="Cyverse"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="center"
                    bg-variant="transparent"
                    border-variant="white"
                >
                    <b-link href="http://arpa-e.energy.gov/">
                        <b-img
                            :src="require('@/assets/sponsors/arpa_e.png')"
                            height="47px"
                            alt="ARPA-E"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="center"
                    bg-variant="transparent"
                    border-variant="white"
                >
                    <b-link href="http://www.xsede.org/">
                        <b-img
                            :src="require('@/assets/sponsors/xsede.png')"
                            height="55px"
                            alt="XSEDE"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="left"
                    bg-variant="transparent"
                    border-variant="white"
                >
                    <b-link href="http://www.uga.edu/">
                        <b-img
                            :src="require('@/assets/sponsors/uga.png')"
                            height="47px"
                            alt="University Of Georgia"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="left"
                    bg-variant="transparent"
                    border-variant="white"
                >
                    <b-link href="http://gacra.uga.edu/">
                        <b-img
                            :src="require('@/assets/sponsors/gacrc.png')"
                            height="47px"
                            alt="Georgia Advanced Computing Resource Center"
                        ></b-img>
                    </b-link>
                </b-card>
            </b-card-group>
        </b-card>
    </b-container>
</template>

<script>
export default {
    name: 'home-sponsors'
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
