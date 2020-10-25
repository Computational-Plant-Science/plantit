<template>
    <div id="background" class="vertical-center m-0 p-0">
        <b-container id="main">
            <b-card
                align="center"
                class="p-2 text-white"
                footer-bg-variant="transparent"
                footer-border-variant="white"
                :border-variant="darkMode ? 'secondary' : 'default'"
                :text-variant="darkMode ? 'dark' : 'white'"
                :bg-variant="darkMode ? 'dark' : 'white'"
                style="max-width: 400px;padding: 0;margin: 0 auto;float: none;margin-bottom: 10px; opacity: 1.0"
            >
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col>
                        <b-img
                            style="max-width: 5rem;transform: translate(0px, 20px);"
                            :src="require('../../assets/logo.png')"
                            center
                            class="m-0 p-0"
                        ></b-img>
                        <h1 :class="darkMode ? 'text-white' : 'text-dark'">
                            PlantIT
                        </h1>
                    </b-col>
                </b-row>
                <b-navbar toggleable="sm" class="m-0 p-0">
                    <b-collapse class="justify-content-center m-0 p-0" is-nav>
                        <b-navbar-nav class="m-0 p-0">
                            <b-nav-item to="/guide" class="m-0 p-0">
                                <b-button
                                    :variant="
                                        darkMode
                                            ? 'outline-light'
                                            : 'outline-dark'
                                    "
                                >
                                    <i class="fas fa-map-signs fa-2x"></i>
                                    <br />
                                    Guide
                                </b-button>
                            </b-nav-item>
                            <b-nav-item to="/docs" class="m-0 p-0">
                                <b-button
                                    :variant="
                                        darkMode
                                            ? 'outline-light'
                                            : 'outline-dark'
                                    "
                                >
                                    <i class="fas fa-book fa-2x"></i>
                                    <br />
                                    Docs
                                </b-button>
                            </b-nav-item>
                            <b-nav-item class="m-0 p-0">
                                <b-button
                                    :variant="
                                        darkMode
                                            ? 'outline-light'
                                            : 'outline-dark'
                                    "
                                    title="Slack"
                                >
                                    <i class="fab fa-slack fa-2x"></i>
                                    <br />
                                    Slack
                                </b-button>
                            </b-nav-item>
                            <b-nav-item
                                class="m-0 p-0"
                                href="https://github.com/Computational-Plant-Science/plantit"
                            >
                                <b-button
                                    :variant="
                                        darkMode
                                            ? 'outline-light'
                                            : 'outline-dark'
                                    "
                                    title="GitHub"
                                >
                                    <i class="fab fa-github fa-2x"></i>
                                    <br />
                                    Github
                                </b-button>
                            </b-nav-item>
                        </b-navbar-nav>
                    </b-collapse>
                </b-navbar>
                <b-row class="m-0 p-0" v-if="!loggedIn">
                    <b-col class="m-0 p-0">
                        <b-button
                            :variant="darkMode ? 'outline-light' : 'white'"
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
                <b-navbar toggleable="sm" class="m-0 p-0" v-else>
                    <b-collapse class="justify-content-center m-0 p-0" is-nav>
                        <b-navbar-nav class="m-0 p-0">
                            <b-nav-item
                                right
                                v-if="loggedIn"
                                title="Enter PlantIT"
                                style="font-size: 12pt"
                                :to="
                                    '/' +
                                        currentUserDjangoProfile.username +
                                        '/'
                                "
                            >
                                <b-button
                                    :variant="
                                        darkMode ? 'outline-light' : 'white'
                                    "
                                    block
                                >
                                    <b-img
                                        v-if="currentUserGitHubProfile"
                                        class="avatar m-0 p-0"
                                        rounded="circle"
                                        center
                                        :src="
                                            currentUserGitHubProfile
                                                ? currentUserGitHubProfile.avatar_url
                                                : ''
                                        "
                                    ></b-img>
                                    Enter
                                    <!--<b v-else
                                        >(
                                        {{
                                            currentUserCyVerseProfile
                                                ? currentUserCyVerseProfile.first_name
                                                : currentUserDjangoProfile.username
                                        }})</b
                                    >-->
                                </b-button>
                            </b-nav-item>
                        </b-navbar-nav>
                    </b-collapse>
                </b-navbar>
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
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserCyVerseProfile',
        'currentUserGitHubProfile',
        'loggedIn',
        'darkMode'
    ]),
    created: function() {
        this.crumbs = this.$route.meta.crumb;
        this.$store.dispatch('loadCurrentUser');
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
    background-blend-mode: overlay
    background-color: hsla(0, 0%, 100%, 0)
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
