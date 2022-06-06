<template>
        <b-card
            align="center"
            class="rounded-0 text-center m-0"
            bg-variant="white"
            border-variant="light"
            header-bg-variant="white"
            header-border-variant="white"
            style="border: none; box-shadow: none"
        >
          <b-row>
              <b-col>
                    <b-link href="https://www.computational-plant-science.org/joomla30/">
                      <b-img
                        :src="
                                require('@/assets/cps_black.png')
                        "
                        height="35px"
                        alt="Computational Plant Science Lab"
                    ></b-img
                >

                    </b-link>
              </b-col>
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
                    <b-link href="http://www.uga.edu/">
                        <b-img
                            :src="require('@/assets/sponsors/uga.png')"
                            height="35px"
                            alt="University Of Georgia"
                        ></b-img>
                    </b-link></b-col>
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
                    <b-link href="http://www.cyverse.org/">
                        <b-img
                            :src="require('@/assets/sponsors/cyversebw.png')"
                            height="35px"
                            alt="Cyverse"
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
</style>
