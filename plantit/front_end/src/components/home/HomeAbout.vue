<template>
    <div id="background" class="vertical-center m-0 p-0">
        <b-container id="main">
            <b-card
                align="center"
                bg-variant="default"
                footer-bg-variant="white"
                footer-border-variant="white"
                border-variant="success"
                style="max-width: 550px;padding: 0;margin: 0 auto;float: none;margin-bottom: 10px; opacity: 0.98"
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
                <b-card-body class="text-center">
                    <p>
                        Welcome to PlantIT, a <b>Phenomics</b>-as-a-Service
                        science gateway!
                        <br>
                        <br>
                        PlantIT allows computational researchers to make their
                        algorithms available to a broad community, and offers
                        biological researchers an easy-to-use interface to apply
                        algorithms in their own work.
                    </p>
                </b-card-body>
                <b-navbar toggleable="sm" class="m-0 p-0">
                    <b-collapse class="justify-content-center m-0 p-0" is-nav>
                        <b-navbar-nav class="m-0 p-0">
                            <b-nav-item to="/About" class="m-0 p-0">
                                <b-button variant="outline-dark">
                                    <i class="fas fa-question fa-2x"></i>
                                    <br />
                                    About PlantIT
                                </b-button>
                            </b-nav-item>
                            <b-nav-item to="/Guide" class="m-0 p-0">
                                <b-button variant="outline-dark">
                                    <i class="fas fa-map-signs fa-2x"></i>
                                    <br />
                                    User Guide
                                </b-button>
                            </b-nav-item>
                            <b-nav-item to="/Documentation" class="m-0 p-0">
                                <b-button variant="outline-dark">
                                    <i class="fas fa-book fa-2x"></i>
                                    <br />
                                    Developer Docs
                                </b-button>
                            </b-nav-item>
                        </b-navbar-nav>
                    </b-collapse>
                </b-navbar>
                <template v-slot:footer style="background-color: white">
                    <b-row class="mb-2">
                        <b-col>
                            <b-button
                                block
                                href="/user/dashboard"
                                variant="success"
                                >Sign Up
                            </b-button>
                        </b-col>
                        <b-col>
                            <b-button
                                block
                                href="/user/dashboard"
                                variant="outline-dark"
                                >Log In
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
    background-color: hsla(0, 0%, 100%, 0.10)
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
