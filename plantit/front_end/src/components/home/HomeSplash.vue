<template>
    <div id="background" class="vertical-center m-0 p-0">
        <b-container id="main">
            <b-card
                align="center"
                class="p-2 text-white"
                footer-bg-variant="transparent"
                footer-border-variant="white"
                border-variant="white"
                text-variant="white"
                bg-variant="transparent"
                style="max-width: 400px;padding: 0;margin: 0 auto;float: none;margin-bottom: 10px; opacity: 1.0"
            >
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col>
                        <b-img
                            :src="require('@/assets/logo.png')"
                            width="100px"
                            alt="Plant IT"
                        ></b-img>
                        <h1>PlantIT</h1>
                    </b-col>
                </b-row>
                <br />
                <b-navbar toggleable="sm" class="m-0 p-0">
                    <b-collapse class="justify-content-center m-0 p-0" is-nav>
                        <b-navbar-nav class="m-0 p-0">
                            <b-nav-item to="/About" class="m-0 p-0">
                                <b-button variant="outline-dark">
                                    <i class="fas fa-seedling fa-3x"></i>
                                    <br />
                                    About
                                </b-button>
                            </b-nav-item>
                            <b-nav-item to="/Guide" class="m-0 p-0">
                                <b-button variant="outline-dark">
                                    <i class="fas fa-map-signs fa-3x"></i>
                                    <br />
                                    Guide
                                </b-button>
                            </b-nav-item>
                            <b-nav-item to="/Docs" class="m-0 p-0">
                                <b-button variant="outline-dark">
                                    <i class="fas fa-book fa-3x"></i>
                                    <br />
                                    Docs
                                </b-button>
                            </b-nav-item>
                        </b-navbar-nav>
                    </b-collapse>
                </b-navbar>
                <template v-slot:footer class="m-0 p-0">
                    <b-row class="m-0 p-0">
                        <b-col class="m-0 p-0">
                            <b-button
                                variant="outline-white"
                                block
                                class="text-center"
                                href="/login/?next=/pipelines/"
                            >
                                <b-img
                                    :src="
                                        require('@/assets/sponsors/cyversebw-notext.png')
                                    "
                                    height="18px"
                                    alt="Cyverse"
                                ></b-img>
                                Log In with CyVerse
                            </b-button>
                        </b-col>
                    </b-row>
                </template>
            </b-card>
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
@import '../../scss/_colors.sass'
@import '../../scss/main.sass'


.vertical-center
    min-height: 100%
    /* Fallback for browsers do NOT support vh unit */
    min-height: 100vh
    /* These two lines are counted as one :-)       */

    display: flex
    align-items: center

#background
    background-image: url('../../assets/frontpage/index_bg.png')
    background-blend-mode: overlay
    background-color: hsla(0, 0%, 100%, 0.1)
    background-repeat: no-repeat
    background-position: center
    background-size: cover
    min-height: 100vh
    width: 100%
    white-space: nowrap
    position: relative
    text-align: center

#background:after
    opacity: 0.5

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
    left: 50%
    margin-left: -40px
    animation-name: down-arrow-highlight
    animation-duration: 2s
    animation-iteration-count: infinite
    animation-direction: alternate
</style>
