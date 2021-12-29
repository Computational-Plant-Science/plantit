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
                :bg-variant="profile.darkMode ? 'dark' : 'white'"
                style="
                    width: 90%;
                    height: 90%;
                    padding: 0;
                    margin: 0 auto;
                    float: none;
                    margin-bottom: 10px;
                    opacity: 0.95;
                "
            >
                <b-row
                    ><b-col md="auto" align-self="center">
                        <h4
                            :class="
                                profile.darkMode ? 'text-white' : 'text-theme'
                            "
                            style="text-decoration: underline; z-index: 100"
                        >
                            plant<small
                                class="mb-3 text-success"
                                style="
                                    text-decoration: underline;
                                    text-shadow: 1px 1px 2px black;
                                    z-index: 100;
                                "
                                ><small>IT</small></small
                            >
                            <small
                                ><small
                                    ><small
                                        ><b-badge variant="success"
                                            ><span v-if="version !== 0">{{
                                                version
                                            }}</span
                                            ><i
                                                class="fas fa-spinner"
                                                v-else
                                            ></i></b-badge></small></small
                            ></small>
                        </h4>
                    </b-col>
                    <b-col md="auto" align-self="center"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-question-circle fa-1x fa-fw"></i
                            >About</span
                        ></b-col
                    >
                    <!--<b-nav-item
                            to="/beta"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="Beta Test"
                            ><span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fas fa-vial fa-1x fa-fw"></i>Beta
                                Testing</span
                            ></b-nav-item
                        >-->
                    <b-col md="auto" align-self="center"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-chart-bar fa-1x fa-fw"></i
                            >Stats</span
                        ></b-col
                    >
                    <b-col md="auto" align-self="center">
                        <b-link
                            href="https://plantit.readthedocs.io/en/latest"
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-book fa-1x fa-fw"></i>Docs</b-link
                        >
                    </b-col>
                    <b-col md="auto" align-self="center">
                        <b-link
                            href="https://github.com/Computational-Plant-Science/plantit"
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fab fa-github fa-1x fa-fw"></i
                            >Github</b-link
                        >
                    </b-col>
                    <!--<b-nav-item
                            href="#"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="Slack"
                        >
                            <span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fab fa-slack fa-1x fa-fw"></i>
                                Slack</span
                            >
                        </b-nav-item>-->
                </b-row>
                <b-row></b-row>
                <b-row class="m-0 p-0">
                    <b-col class="m-0 p-0">
                        <b-button
                            v-if="!profile.loggedIn"
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
                        <b-button
                            v-else
                            variant="white"
                            block
                            class="text-right"
                            href="/apis/v1/idp/cyverse_login/"
                        >
                            <span class="text-success">
                                <i class="fas fa-arrow-circle-right fa-fw"></i>
                                Enter</span
                            >
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
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'home-splash',
    data: function () {
        return {
            version: 0,
        };
    },
    computed: mapGetters('user', ['profile']),
    created: async function () {
        this.crumbs = this.$route.meta.crumb;
        await this.getVersion();
        // this.$store.dispatch('user/loadProfile');
    },
    methods: {
        async getVersion() {
            await axios({
                method: 'get',
                url: `https://api.github.com/repos/Computational-Plant-Science/plantit/tags`,
                headers: { 'Content-Type': 'application/json' },
            })
                .then((response) => {
                    this.version = response.data[0].name;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
    },
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
