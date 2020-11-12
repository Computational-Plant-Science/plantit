<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="sidebar-left"
            shadow="lg"
            :bg-variant="darkMode ? 'dark' : 'light'"
            :text-variant="darkMode ? 'dark' : 'light'"
            no-header-close
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-1">
                    <b-row class="ml-0 mr-0 pl-0 pr-0" align-v="start">
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-warning'
                                                : 'warning'
                                        "
                                        block
                                        class="text-left m-0"
                                        @click="hide"
                                    >
                                        <i
                                            class="fas fa-arrow-left fa-1x fa-fw"
                                        ></i>
                                        Hide Sidebar
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        v-if="loggedIn"
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        block
                                        class="text-left m-0"
                                        @click="toggleDarkMode"
                                    >
                                        <i
                                            v-if="darkMode"
                                            class="fas fa-sun fa-1x fa-fw"
                                        ></i>
                                        <i
                                            v-else
                                            class="fas fa-moon fa-1x fa-fw"
                                        ></i>
                                        {{ darkMode ? 'Disable' : 'Enable' }}
                                        Dark Mode
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    v-if="!loggedIn"
                                    href="/apis/v1/idp/cyverse_login/"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        variant="white"
                                        block
                                        class="text-left m-0"
                                    >
                                        Log in with
                                        <b-img
                                            :src="
                                                require('../assets/sponsors/cyversebw-notext.png')
                                            "
                                            height="18px"
                                            alt="Cyverse"
                                        ></b-img>
                                        <b>CyVerse</b>
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                        </b-col>
                    </b-row>
                    <b-row class="ml-0 mr-0 pl-0 pr-0" align-v="center">
                        <b-col class="ml-0 mr-0 pl-0 pr-0" align-self="middle">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item
                                    v-if="loggedIn"
                                    class="m-0 p-0"
                                    disabled
                                >
                                    <small
                                        :class="
                                            darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Navigation</small
                                    >
                                </b-nav-item>
                                <b-nav-item to="/" class="m-0 p-0">
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-home fa-1x fa-fw"></i>
                                        PlantIT
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/guide" class="m-0 p-0">
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-map-signs fa-1x fa-fw"
                                        ></i>
                                        User Guide
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/docs" class="m-0 p-0">
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-book fa-1x fa-fw"></i>
                                        Developer Docs
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <b-nav
                                vertical
                                class="ml-0 mr-0 pl-0 pr-0"
                                v-if="loggedIn"
                            >
                                <b-nav-item class="m-0 p-0" disabled>
                                    <small
                                        :class="
                                            darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Resources</small
                                    >
                                </b-nav-item>
                                <b-nav-item
                                    title="users"
                                    to="/users"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-user fa-1x fa-fw"></i>
                                        Users
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    title="flows"
                                    to="/flows"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-stream fa-1x fa-fw"
                                        ></i>
                                        Flows
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <b-nav
                                vertical
                                class="ml-0 mr-0 pl-0 pr-0"
                                v-if="loggedIn"
                            >
                                <b-nav-item class="m-0 p-0" disabled>
                                    <small
                                        :class="
                                            darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Connect</small
                                    >
                                </b-nav-item>
                                <b-nav-item class="ml-0 mr-0 pl-0 pr-0">
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        class="text-left m-0"
                                        title="Slack"
                                        block
                                    >
                                        <i class="fab fa-slack fa-1x fa-fw"></i>
                                        Slack
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    class="ml-0 mr-0 pl-0 pr-0"
                                    href="https://github.com/Computational-Plant-Science/plantit"
                                >
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-light'
                                                : 'outline-dark'
                                        "
                                        block
                                        title="GitHub"
                                        class="text-left m-0 "
                                    >
                                        <i
                                            class="fab fa-github fa-1x fa-fw"
                                        ></i>
                                        GitHub
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
            <template v-slot:footer>
                <b-container class="p-1">
                    <b-row class="ml-0 mr-0 pl-0 pr-0" align-v="center">
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav
                                vertical
                                class="ml-0 mr-0 pl-0 pr-0 mb-2"
                                v-if="loggedIn"
                            >
                                <hr />
                                <b-nav-item
                                    title="log out"
                                    href="/apis/v1/idp/cyverse_logout/"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        variant="outline-danger"
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-door-closed fa-1x fa-fw"
                                        ></i>
                                        Log Out
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-navbar
            toggleable="sm"
            class="logo p-0 overflow-hidden"
            style="min-height: 44px; max-height: 44px; z-index: 1000"
            fixed="top"
            :variant="darkMode ? 'dark' : 'white'"
        >
            <b-collapse class="m-0 p-0" is-nav>
                <b-navbar-nav class="m-0 p-0 pl-1 mr-1">
                    <b-nav-item class="m-0 p-0" v-b-toggle.sidebar-left>
                        <b-button
                            class="brand-img m-0 p-0"
                            v-bind:class="{ 'not-found': notFound }"
                            variant="outline-white"
                            @mouseenter="titleContent = 'sidebar'"
                            @mouseleave="titleContent = 'breadcrumb'"
                        >
                            <b-img
                                class="m-0 p-0 mb-3"
                                center
                                width="39px"
                                :src="require('../assets/logo.png')"
                                alt="Plant IT"
                            ></b-img>
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
                <transition name="component-fade" mode="out-in">
                    <b-breadcrumb
                        class="m-o p-0 mt-2"
                        style="background-color: transparent;"
                        v-if="titleContent === 'sidebar'"
                    >
                        <b-breadcrumb-item
                            disabled
                            class="ml-2"
                            :class="darkMode ? 'crumb-dark' : 'crumb-light'"
                        >
                            <h5>
                                <b-badge variant="info">Sidebar</b-badge>
                            </h5>
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                    <b-breadcrumb
                        class="m-o p-0 mt-2 text-warning"
                        style="background-color: transparent"
                        v-if="titleContent === 'breadcrumb'"
                    >
                        <b-breadcrumb-item
                            v-for="crumb in crumbs"
                            :key="crumb.text"
                            :to="crumb.href"
                            :disabled="crumb.text === 'runs'"
                            :class="darkMode ? 'crumb-dark' : 'crumb-light'"
                        >
                            <h5>
                                <b-badge
                                    variant="white"
                                    :class="
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                >
                                    {{ crumb.text }}
                                </b-badge>
                            </h5>
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                </transition>
                <b-navbar-nav class="ml-auto m-0 p-0">
                    <b-nav-item
                        v-if="
                            loggedIn ? currentUserGitHubProfile === null : false
                        "
                        title="Log in to GitHub"
                        href="/apis/v1/idp/github_request_identity/"
                        class="ml-0 mr-0"
                    >
                        <b-button class="text-left" variant="success" size="sm">
                            <i class="fab fa-github"></i>
                            Log in to GitHub
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        right
                        v-if="loggedIn"
                        :title="currentUserDjangoProfile.username"
                        class="m-0 p-0 mt-1"
                        style="font-size: 12pt"
                        :href="'/' + currentUserDjangoProfile.username + '/'"
                    >
                        <b-button
                            :variant="darkMode ? 'outline-light' : 'white'"
                            class="m-0 ml-0 mr-2 text-left"
                            size="sm"
                        >
                            <b-img
                                v-if="currentUserGitHubProfile"
                                class="avatar m-0 mb-1 p-0 github-hover logo"
                                style="min-width: 22px; min-height: 22px; position: relative; left: -3px; top: 1.5px; border: 1px solid #d6df5D;"
                                rounded="circle"
                                :src="
                                    currentUserGitHubProfile
                                        ? currentUserGitHubProfile.avatar_url
                                        : ''
                                "
                            ></b-img>
                            <i v-else class="far fa-user"></i>
                            {{
                                currentUserCyVerseProfile
                                    ? currentUserCyVerseProfile.first_name
                                    : currentUserDjangoProfile.username
                            }}
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'Navigation',
    components: {},
    data() {
        return {
            crumbs: [],
            notFound: false,
            titleContent: 'breadcrumb'
        };
    },
    computed: mapGetters([
        'darkMode',
        'currentUserDjangoProfile',
        'currentUserCyVerseProfile',
        'currentUserGitHubProfile',
        'loggedIn'
    ]),
    created: function() {
        this.crumbs = this.$route.meta.crumb;
        this.$store.dispatch('loadCurrentUser');
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        }
    },
    methods: {
        toggleDarkMode: function() {
            this.$store.dispatch('toggleDarkMode');
        }
    }
};
</script>

<style scoped lang="sass">
@import '../scss/main.sass'
@import '../scss/_colors.sass'

.not-found
    color: $red
    border: 2px solid $red
    -webkit-transform: rotate(180deg)
        transform: rotate(180deg)

.not-found:hover
    color: $dark
    border: 2px solid $white
    -webkit-transform: rotate(90deg)
        transform: rotate(90deg)

.mirror
    -moz-transform: scale(-1, 1)
    -webkit-transform: scale(-1, 1)
    -o-transform: scale(-1, 1)
    -ms-transform: scale(-1, 1)
    transform: scale(-1, 1)

.breadcrumb > li
    text-align: end
    margin-top: 12px !important
    font-size: 12pt !important
    font-weight: 200
    content: " /"

.breadcrumb > li + li::marker
    margin-top: 12px !important
    font-size: 12pt !important
    font-weight: 200

.breadcrumb > li + li:before + li::marker
    margin-top: 12px !important
    font-size: 12pt !important
    font-weight: 200
    content: " /"

.component-fade-enter-active, .component-fade-leave-active
    transition: opacity .3s ease

.component-fade-enter, .component-fade-leave-to
    opacity: 0

.brand-img
    -webkit-transition: -webkit-transform .1s ease-in-out
        transition: transform .2s ease-in-out

.brand-img:hover
    border: none
    color: white
    -webkit-transform: rotate(90deg)
    transform: rotate(90deg)

.github-hover:hover
  color: $color-highlight !important
  background-color: $dark !important


.avatar
  max-height: 15px
  border: 1px solid $dark

.crumb-dark
  font-weight: 300
  color: white !important
  // text-decoration: underline
  // text-decoration-color: $color-button

.crumb-light
  font-weight: 300
  color: $dark !important

.darkk
  background-color: #292b2c
</style>
