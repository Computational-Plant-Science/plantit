<template>
    <div class="vertical-center m-0 p-0">
        <b-container fluid>
            <b-card
                align="center"
                class="rounded-0 text-center m-0 p-3"
                bg-variant="white"
                border-variant="white"
                header-bg-variant="white"
                header-border-variant="white"
            >
                <b-row>
                    <b-col>
                        <b-link href="http://gacra.uga.edu/">
                            <b-img
                                :src="require('@/assets/sponsors/gacrc.png')"
                                height="35px"
                                alt="Georgia Advanced Computing Resource Center"
                            ></b-img>
                        </b-link>
                    </b-col>
                    <b-col>
                        <b-link href="https://www.nsf.gov/">
                            <b-img
                                :src="require('@/assets/sponsors/nsf.png')"
                                height="35px"
                                alt="National Science Foundation"
                            ></b-img>
                        </b-link>
                    </b-col>
                    <b-col>
                        <b-link href="http://arpa-e.energy.gov/">
                            <b-img
                                :src="require('@/assets/sponsors/arpa_e.png')"
                                height="35px"
                                alt="ARPA-E"
                            ></b-img>
                        </b-link>
                    </b-col>
                    <b-col>
                        <b-link href="http://www.xsede.org/">
                            <b-img
                                :src="require('@/assets/sponsors/xsede.png')"
                                height="35px"
                                alt="XSEDE"
                            ></b-img>
                        </b-link>
                    </b-col>
                </b-row>
            </b-card>
        </b-container>
    </div>
</template>

<script>
export default {
    name: 'home-sponsors',
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

.shadowed
  box-shadow: inset 0px 0px 5px 5px $dark
</style>
