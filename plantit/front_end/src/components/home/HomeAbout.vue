<template>
    <div id="background" class="vertical-center">
        <b-container id="main">
            <b-card align="center" fluid>
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col>
                        <b-img
                            :src="require('@/assets/logo.png')"
                            width="100px"
                            alt="Plant IT"
                        ></b-img>
                        <h1>Plant IT</h1>
                    </b-col>
                </b-row>
                <b-row align-v="center" class="mb-2">
                    <b-col align="center">
                        <b-navbar toggleable="lg">
                            <b-collapse class="justify-content-center" is-nav>
                                <b-navbar-nav align="center">
                                    <b-nav-item to="/About">About</b-nav-item>
                                    <b-nav-item to="/Guide"
                                        >User Guide</b-nav-item
                                    >
                                    <b-nav-item
                                        to="https://github.com/Computational-Plant-Science/DIRT2_Webplatform/issues/new"
                                    >
                                        Report an Issue
                                    </b-nav-item>
                                </b-navbar-nav>
                            </b-collapse>
                        </b-navbar>
                    </b-col>
                </b-row>
                <b-row align-v="center" class="mb-4">
                    <b-col align="right">
                        <b-button
                            href="/user/dashboard"
                            class="plantit-btn-alternate"
                            >Sign Up
                        </b-button>
                    </b-col>
                    or
                    <b-col align="left">
                        <b-button
                            href="/user/dashboard"
                            class="bold plantit-btn"
                            >Log In
                        </b-button>
                    </b-col>
                </b-row>
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
    background-color: hsla(0, 0%, 100%, 0.80)
    background-repeat: no-repeat
    background-position: bottom
    background-size: 100%
    min-height: 100vh
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
