<template>
    <b-container fluid class="m-0 p-4 center-container">
        <h1>Sponsors</h1>

        <b-row id="sponsors">
          <b-col>
            <b-link href="http://www.cyverse.org/">
              <b-img
                  :src="require('@/assets/sponsors/PoweredbyCyverse_LogoSquare.webp')"
                  height="100px"
                  alt="Cyverse"
              ></b-img>
            </b-link>
          </b-col>
          <b-col>
            <b-link href="http://arpa-e.energy.gov/">
              <b-img
                  :src="require('@/assets/sponsors/arpa_e.png')"
                  height="100px"
                  alt="ARPA-E"
              ></b-img>
            </b-link>
          </b-col>
          <b-col>
            <b-link href="http://www.computational-plant-science.org">
              <b-img
                  :src="require('@/assets/sponsors/cps-black.png')"
                  height="100px"
                  alt="Computational Plant Science Lab"
              ></b-img>
            </b-link>
          </b-col>
          <b-col>
            <b-link href="http://www.uga.edu/">
              <b-img
                  :src="require('@/assets/sponsors/uga.png')"
                  height="100px"
                  alt="University Of Georgia"
              ></b-img>
            </b-link>
          </b-col>
          <b-col>
            <b-link href="http://gacra.uga.edu/">
              <b-img
                  :src="require('@/assets/sponsors/gacrc.png')"
                  height="100px"
                  alt="Georgia Advanced Computing Resource Center"
              ></b-img>
            </b-link>
          </b-col>
        </b-row>
    </b-container>
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

  #sponsors
    text-align: center

  #sponsors > .col
    padding-top: 30px
</style>
