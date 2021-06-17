<template>
    <div id="background" class="vertical-center m-0 p-0">
        <b-container id="main">
            <b-card
                align="center"
                class="p-3 text-white"
                footer-bg-variant="transparent"
                footer-border-variant="white"
                border-variant="default"
                text-variant="white"
                bg-variant="white"
                style="max-width: 430px;padding: 0;margin: 0 auto;float: none;margin-bottom: 10px; opacity: 0.95"
            >
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col>
                        <b-img
                            style="max-width: 5rem;transform: translate(0px, 20px);"
                            :src="require('../../assets/logo.png')"
                            center
                            class="m-0 p-0"
                        ></b-img>
                        <h1
                            class="text-dark"
                            style="text-decoration: underline;"
                        >
                            plant<small
                                class="mb-3 text-success"
                                style="text-decoration: underline;text-shadow: 1px 0 0 #000, 0 -1px 0 #000, 0 1px 0 #000, -1px 0 0 #000;"
                                >IT</small
                            >
                        </h1>
                    </b-col>
                </b-row>
                <b-navbar toggleable="sm" class="m-0 p-0">
                    <b-collapse class="justify-content-center m-0 p-0" is-nav>
                        <b-navbar-nav class="m-0 p-0">
                            <b-nav-item
                                to="/about"
                                title="About PlantIT"
                                class="m-0 p-0"
                            >
                                <b-button
                                    variant="outline-dark"
                                >
                                    <i class="fas fa-question-circle fa-2x"></i>
                                    <br />
                                    About
                                </b-button>
                            </b-nav-item>
                            <b-nav-item
                                href="https://plantit.readthedocs.io/en/latest"
                                title="PlantIT Docs"
                                class="m-0 p-0"
                            >
                                <b-button
                                    variant="outline-dark"
                                >
                                    <i class="fas fa-book fa-2x"></i>
                                    <br />
                                    Docs
                                </b-button>
                            </b-nav-item>
                            <b-nav-item
                                class="m-0 p-0"
                                title="PlantIT on GitHub"
                                href="https://github.com/Computational-Plant-Science/plantit/discussions/63"
                            >
                                <b-button
                                    variant="outline-dark"
                                    title="GitHub"
                                >
                                    <i class="fab fa-github fa-2x"></i>
                                    <br />
                                    Github
                                </b-button>
                            </b-nav-item>
                            <!--<b-nav-item href="#" class="m-0 p-0" title="Slack">
                                <b-button
                                    variant="outline-dark"
                                    title="GitHub"
                                >
                                    <i class="fab fa-slack fa-2x"></i>
                                    <br />
                                    Slack
                                </b-button>
                            </b-nav-item>-->
                            <!--<b-nav-item class="m-0 p-0" title="Slack">
                                <b-button
                                    variant="outline-dark"
                                    title="Slack"
                                >
                                    <i class="fab fa-slack fa-2x"></i>
                                    <br />
                                    Slack
                                </b-button>
                            </b-nav-item>-->


                            <!--<b-nav-item
                                v-if="profile.loggedIn"
                                title="Enter PlantIT"
                                class="m-0 p-0"
                                :to="'/dashboard/'"
                            >
                                <b-button
                                    variant="white"
                                >
                                    <b-img
                                        v-if="profile.githubProfile"
                                        class="avatar"
                                        rounded="circle"
                                        center
                                        :src="
                                            profile.githubProfile
                                                ? profile.githubProfile
                                                      .avatar_url
                                                : ''
                                        "
                                    ></b-img>
                                    <i
                                        v-else
                                        class="far fa-user fa-fw fa-2x"
                                    ></i>
                                    Enter
                                </b-button>
                            </b-nav-item> -->
                        </b-navbar-nav>
                    </b-collapse>
                </b-navbar>
                <b-row class="m-0 p-0">
                    <b-col class="m-0 p-0">
                        <b-button
                            variant="white"
                            block
                            class="text-center"
                            href="/apis/v1/idp/cyverse_login/"
                        >
                            Log in with
                            <b-img
                                :src="
                                    require('@/assets/sponsors/cyversebw-notext.png')
                                "
                                height="18px"
                                alt="Cyverse"
                            ></b-img>
                            <b>CyVerse</b>
                        </b-button>
                    </b-col>
                </b-row>
            </b-card>
        </b-container>
        <div style="position: absolute; bottom: 0; left: 49%">
            <i
                class="fas fa-chevron-down fa-5x fa-fw"
                id="about-down-arrow"
            ></i>
        </div>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'home-splash',
    computed: mapGetters('user', ['profile']),
    created: function() {
        this.crumbs = this.$route.meta.crumb;
        // this.$store.dispatch('user/loadProfile');
    }
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
    background-blend-mode: normal
    background-color: hsla(0%, 0%, 100%, 1)
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

.avatar
    height: 35px
</style>
