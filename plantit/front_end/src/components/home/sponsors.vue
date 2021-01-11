<template>
    <div>
        <b-card
            align="center"
            class="rounded-0 text-center"
            bg-variant="white"
            border-variant="default"
            header-bg-variant="white"
            header-border-variant="white"
            style="border: none; box-shadow: none"
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
                    align="center"
                    bg-variant="transparent"
                    border-variant="white"
                    style="border: none; box-shadow: none"
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
                    style="border: none; box-shadow: none"
                >
                    <b-link href="https://www.nsf.gov/">
                        <b-img
                            :src="require('@/assets/sponsors/nsf.png')"
                            height="60px"
                            alt="National Science Foundation"
                            class="mr-5"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="center"
                    bg-variant="transparent"
                    border-variant="white"
                    style="border: none; box-shadow: none"
                >
                    <b-link href="http://www.xsede.org/">
                        <b-img
                            :src="require('@/assets/sponsors/xsede.png')"
                            height="60px"
                            alt="XSEDE"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="center"
                    bg-variant="transparent"
                    border-variant="white"
                    style="border: none; box-shadow: none"
                >
                    <b-link href="http://www.cyverse.org/">
                        <b-img
                            :src="require('@/assets/sponsors/cyversebw.png')"
                            height="42px"
                            alt="Cyverse"
                        ></b-img>
                    </b-link>
                </b-card>
                <b-card
                    align="center"
                    bg-variant="transparent"
                    border-variant="white"
                    style="border: none; box-shadow: none"
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
                    align="center"
                    bg-variant="transparent"
                    border-variant="white"
                    style="border: none; box-shadow: none"
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
    </div>
</template>

<script>
export default {
    name: 'home-sponsors'
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
h1
    color: $dark

.sponsors
    text-align: center

.sponsors > .col
    padding-top: 30px
</style>
