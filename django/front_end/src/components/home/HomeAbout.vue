<template>
    <div id="background">
        <b-container id="main">
            <b-row>
                <b-col>
                    <b-img
                        :src="require('@/assets/logo.png')"
                        width="100px"
                        alt="Plant IT"
                    ></b-img>
                    <h1>PLANT IT</h1>
                    <b-jumbotron id="message">
                        Plant IT empowers computational researchers to make
                        their algorithms available to a broad community, and
                        provides biological researchers with an easy-to-use
                        interface to apply the algorithms to their own data.
                    </b-jumbotron>
                </b-col>
            </b-row>
            <b-row>
              <b-col>
                <b-nav class="mx-auto " id="main-nav">
                  <b-navbar toggleable="lg" class="mx-auto">
                      <b-nav-item>Contact</b-nav-item>
                      <b-nav-item>Datasets</b-nav-item>
                      <b-nav-item>FAQ</b-nav-item>
                      <b-nav-item href="/user/dashboard">Login</b-nav-item>
                  </b-navbar>
                </b-nav>
            </b-col>
            </b-row>
        </b-container>
        <i class="fas fa-chevron-down fa-7x" id="about-down-arrow"></i>
    </div>
</template>

<script>
export default {
    name: 'HomeAbout'
};
</script>

<style scoped lang="sass">
@import "@/scss/_colors.sass"

#background
  background-image: url('../../assets/frontpage/index_bg.png')
  background-repeat: no-repeat
  background-position: bottom
  background-size: 100%
  min-height: 100vh
  white-space: nowrap
  position: relative
  text-align: center

#main
  text-align: center
  padding-bottom: 50px
  white-space: normal

#message
  width: 60%
  background-color: $color-box-background
  margin: 0 auto
  color: white

#main-nav
  width: 60%
  background-color: $color-box-background
  margin-top: 10px
  margin-bottom: 75px
  border-radius: 10px

  a
    color: $color-highlight
    margin: 0 auto

  a:hover
    text-decoration: underline

@keyframes down-arrow-highlight
  0%
    color: $color-box-background
  100%
    color: $color-highlight

#about-down-arrow
  position: absolute
  bottom: 0
  margin-left: -40px
  animation-name: down-arrow-highlight
  animation-duration: 2s
  animation-iteration-count: infinite
  animation-direction: alternate

</style>
