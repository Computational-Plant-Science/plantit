<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="sidebar-left"
            shadow="sm"
            bg-variant="white"
            no-header-close
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-1">
                    <b-row class="ml-0 mr-0 pl-0 pr-0" align-v="center">
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item
                                    v-if="!loggedIn"
                                    href="/login/?next=/workflows/"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        variant="white"
                                        block
                                        class="text-left m-0"
                                    >
                                        log in with
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
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        variant="success"
                                        block
                                        class="text-left m-0"
                                        @click="hide"
                                        title="hide sidebar"
                                    >
                                        <i
                                            class="fas fa-arrow-left fa-1x fa-fw"
                                        ></i>
                                        hide
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <hr />
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item
                                    v-if="loggedIn"
                                    class="m-0 p-0"
                                    disabled
                                >
                                    <b-button disabled variant="white">
                                        <small>navigate</small>
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-home fa-1x fa-fw"></i>
                                        home
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/guide" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-map-signs fa-1x fa-fw"
                                        ></i>
                                        guide
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/docs" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-book fa-1x fa-fw"></i>
                                        docs
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <hr />
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item
                                    v-if="loggedIn"
                                    class="m-0 p-0"
                                    disabled
                                >
                                    <b-button disabled variant="white">
                                        <small>explore</small>
                                    </b-button>
                                </b-nav-item>
                              <b-nav-item
                                    v-if="loggedIn"
                                    title="users"
                                    to="/users"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-user fa-1x fa-fw"></i>
                                        users
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    v-if="loggedIn"
                                    title="data"
                                    to="/data"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-database fa-1x fa-fw"
                                        ></i>
                                        data
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    v-if="loggedIn"
                                    title="flows"
                                    to="/flows"
                                    class="m-0 p-0"
                                >
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-stream fa-1x fa-fw"
                                        ></i>
                                        flows
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <hr />
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item
                                    v-if="loggedIn"
                                    class="m-0 p-0"
                                    disabled
                                >
                                    <b-button disabled variant="white">
                                        <small>connect</small>
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        class="text-left"
                                        title="Slack"
                                    >
                                        <i class="fab fa-slack fa-2x fa-fw"></i>
                                    </b-button>
                                    <b-button
                                        variant="outline-dark"
                                        href="https://github.com/Computational-Plant-Science/plantit"
                                        title="GitHub"
                                        class="text-left pl-2 github-hover"
                                    >
                                        <i
                                            class="fab fa-github fa-2x fa-fw"
                                        ></i>
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <hr />
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item
                                    v-if="loggedIn"
                                    title="log out"
                                    to="/logout"
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
                                        log out
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <!--<hr />
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        variant="white"
                                        block
                                        class="text-left m-0"
                                        @click="hide"
                                        title="Hide Sidebar"
                                    >
                                        <i
                                            class="fas fa-arrow-left fa-1x fa-fw"
                                        ></i>
                                        Close Sidebar
                                    </b-button>
                                </b-nav-item>
                            </b-nav>-->
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-navbar
            toggleable="sm"
            class="logo p-0 overflow-hidden"
            style="min-height: 40px; max-height: 60px; z-index: 1000"
            fixed="top"
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
                                class="m-0 p-0 mb-1"
                                center
                                width="20px"
                                :src="require('../assets/logo.png')"
                                alt="Plant IT"
                            ></b-img>
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
                <transition name="component-fade" mode="out-in">
                    <b-breadcrumb
                        class="m-o p-0 ml-4"
                        style="background-color: transparent;"
                        v-if="titleContent === 'sidebar'"
                    >
                        <b-breadcrumb-item disabled class="ml-1">
                            show sidebar
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                    <b-breadcrumb
                        class="m-o p-0 ml-0 pl-0"
                        style="background-color: transparent"
                        v-if="titleContent === 'breadcrumb'"
                    >
                        <b-breadcrumb-item
                            v-for="crumb in crumbs"
                            :key="crumb.text"
                            class="background-transparent title mr-1"
                            :to="crumb.href"
                        >
                            {{ crumb.text }}
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                </transition>
                <b-navbar-nav class="ml-auto m-0 p-0">
                    <b-nav-item
                        v-if="
                            loggedIn
                                ? currentUserDjangoProfile.profile
                                      .github_token === ''
                                : false
                        "
                        title="Link GitHub Account"
                        href="/apis/v1/users/github_request_identity/"
                        class="m-0 p-0"
                    >
                        <b-button class="text-left" variant="success">
                            <i class="fab fa-github"></i>
                            Link GitHub Account
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        right
                        variant="dark"
                        v-if="loggedIn"
                        :title="currentUserDjangoProfile.username"
                        class="m-0 p-0"
                        style="font-size: 12pt"
                        :to="
                            '/users/' + currentUserDjangoProfile.username + '/'
                        "
                    >
                        <b-button variant="white">
                            <b-img
                                v-if="currentUserGitHubProfile"
                                class="avatar m-0 p-0"
                                rounded="circle"
                                :src="
                                    currentUserGitHubProfile
                                        ? currentUserGitHubProfile.avatar_url
                                        : ''
                                "
                            ></b-img>
                            <b v-else
                                >(
                                {{
                                    currentUserCyVerseProfile
                                        ? currentUserCyVerseProfile.first_name
                                        : currentUserDjangoProfile.username
                                }})</b
                            >
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

a
    color: $dark !important
    border: none !important


.mirror
    -moz-transform: scale(-1, 1)
    -webkit-transform: scale(-1, 1)
    -o-transform: scale(-1, 1)
    -ms-transform: scale(-1, 1)
    transform: scale(-1, 1)

.breadcrumb > li
    text-align: end
    color: $dark !important
    margin-top: 14px !important
    font-size: 14pt !important
    font-weight: 200
    content: " /"

.breadcrumb > li + li::marker
    color: $dark !important
    margin-top: 14px !important
    font-size: 14pt !important
    font-weight: 200

.breadcrumb > li + li:before + li::marker
    color: $dark !important
    margin-top: 11px !important
    font-size: 11pt !important
    font-weight: 200
    content: " /"

.component-fade-enter-active, .component-fade-leave-active
    transition: opacity .3s ease

.component-fade-enter, .component-fade-leave-to
    opacity: 0

.brand-img
    -webkit-transition: -webkit-transform .2s ease-in-out
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
  max-height: 25px
  border: 1px solid $success

a
  font-weight: 300
  color: $dark // !important
  // text-decoration: underline
  // text-decoration-color: $color-button
</style>
