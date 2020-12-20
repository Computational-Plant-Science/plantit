<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="sidebar-left"
            shadow="lg"
            :bg-variant="darkMode ? 'dark' : 'light'"
            :text-variant="darkMode ? 'dark' : 'light'"
            no-header-close
            width="550px"
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-1">
                    <b-row
                        class="ml-0 mr-0 pl-0 pr-0 text-center"
                        align-v="start"
                    >
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
                                        Hide Runs
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
                    <b-row
                        v-if="!loggedIn"
                        class="ml-0 mr-0 pl-0 pr-0"
                        align-v="center"
                    >
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item class="m-0 p-0" disabled>
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
                                <b-nav-item
                                    href="https://plantit.readthedocs.io/en/latest"
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
                                        <i class="fas fa-book fa-1x fa-fw"></i>
                                        Docs
                                    </b-button>
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
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
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
                                    href="https://github.com/Computational-Plant-Science/plantit/discussions/63"
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
                    <b-row class="m-3 pl-0 pr-0" align-v="center">
                        <b-col class="ml-0 mr-0 pl-0 pr-0 text-center">
                            <!--<small
                                :class="darkMode ? 'text-light' : 'text-dark'"
                                >Recent Runs</small
                            >
                            <br />-->
                            <b-list-group class="text-left">
                                <b-list-group-item
                                    v-for="run in runs"
                                    v-bind:key="run.id"
                                    :class="
                                        darkMode
                                            ? 'text-light bg-dark'
                                            : 'text-dark bg-white'
                                    "
                                    @click="onRunSelected(run)"
                                >
                                    <small
                                        ><a
                                            :class="
                                                darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                            :href="
                                                `https://github.com/${run.flow_owner}/${run.flow_name}`
                                            "
                                            ><i class="fab fa-github fa-fw"></i>
                                            {{ run.flow_owner }}/{{
                                                run.flow_name
                                            }}</a
                                        ></small
                                    >
                                    <br />
                                    <small
                                        ><a
                                            :class="
                                                darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                            :href="
                                                `/${currentUserDjangoProfile.username}/runs/${run.id}`
                                            "
                                            >{{ run.id }}</a
                                        ></small
                                    ><b-badge
                                        class="ml-1 mr-1"
                                        :variant="
                                            run.state === 1
                                                ? 'success'
                                                : run.state === 2
                                                ? 'danger'
                                                : 'warning'
                                        "
                                        >{{
                                            statusToString(run.state)
                                        }}</b-badge
                                    ><small>
                                        <br />
                                        {{ prettify(run.updated) }}</small
                                    >
                                    <!--<hr
                                        :class="
                                            darkMode
                                                ? 'theme-secondary'
                                                : 'theme-light'
                                        "
                                    />-->
                                </b-list-group-item>
                            </b-list-group>
                        </b-col>
                    </b-row>
                    <b-row
                        class="ml-0 mr-0 pl-0 pr-0 mb-4 text-center"
                        align-v="start"
                    >
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                          <b-spinner
                                v-if="loadingRuns"
                                type="grow"
                                variant="warning"
                            ></b-spinner>
                            <b-nav v-else vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        :variant="
                                            darkMode
                                                ? 'outline-warning'
                                                : 'warning'
                                        "
                                        :disabled="loadingRuns"
                                        block
                                        class="text-left m-0"
                                        @click="loadRuns(currentRunPage + 1)"
                                    >
                                        Load More
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
            class="logo p-0"
            style="min-height: 44px; max-height: 46px; z-index: 1000"
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
                                <b-badge variant="info">Show Runs</b-badge>
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
                    <b-nav-item-dropdown
                        right
                        v-if="loggedIn"
                        :title="currentUserDjangoProfile.username"
                        class="m-0 p-0 mt-1 dropdown-custom"
                        :menu-class="darkMode ? 'theme-dark' : 'theme-light'"
                        style="font-size: 12pt; z-index: 1001;"
                    >
                        <template #button-content>
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
                                <i class="fas fa-caret-down fa-fw"></i>
                            </b-button>
                        </template>
                        <b-dropdown-item
                            v-if="loggedIn"
                            class="m-0 p-0"
                            disabled
                        >
                            <small
                                :class="darkMode ? 'text-light' : 'text-dark'"
                                >Navigation</small
                            >
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="PlantIT"
                            to="/"
                            :class="darkMode ? 'text-light' : 'text-dark'"
                            :link-class="
                                darkMode ? 'text-secondary' : 'text-dark'
                            "
                        >
                            <i class="fas fa-home fa-1x fa-fw"></i>
                            PlantIT
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Docs"
                            href="https://plantit.readthedocs.io/en/latest"
                            :class="darkMode ? 'text-light' : 'text-dark'"
                            :link-class="
                                darkMode ? 'text-secondary' : 'text-dark'
                            "
                        >
                            <i class="fas fa-book fa-1x fa-fw"></i>
                            Docs
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Users"
                            to="/users"
                            :class="darkMode ? 'text-light' : 'text-dark'"
                            :link-class="
                                darkMode ? 'text-secondary' : 'text-dark'
                            "
                        >
                            <i class="fas fa-user fa-1x fa-fw"></i>
                            Users
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Flows"
                            to="/flows"
                            :class="darkMode ? 'text-light' : 'text-dark'"
                            :link-class="
                                darkMode ? 'text-secondary' : 'text-dark'
                            "
                        >
                            <i class="fas fa-stream fa-1x fa-fw"></i>
                            Flows
                        </b-dropdown-item>
                        <b-dropdown-item
                            v-if="loggedIn"
                            class="m-0 p-0"
                            disabled
                        >
                            <small
                                :class="darkMode ? 'text-light' : 'text-dark'"
                                >User</small
                            >
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Profile"
                            :class="darkMode ? 'text-light' : 'text-dark'"
                            :link-class="
                                darkMode ? 'text-secondary' : 'text-dark'
                            "
                            :href="
                                '/' + currentUserDjangoProfile.username + '/'
                            "
                        >
                            <i class="fas fa-user fa-1x fa-fw"></i>
                            Profile
                        </b-dropdown-item>
                        <b-dropdown-item
                            :title="
                                `${darkMode ? 'Disable' : 'Enable'} Dark Mode`
                            "
                            :class="darkMode ? 'text-light' : 'text-dark'"
                            :link-class="
                                darkMode ? 'text-secondary' : 'text-dark'
                            "
                            @click="toggleDarkMode"
                        >
                            <i
                                v-if="darkMode"
                                class="fas fa-sun fa-1x fa-fw"
                            ></i>
                            <i v-else class="fas fa-moon fa-1x fa-fw"></i>
                            {{ darkMode ? 'Disable' : 'Enable' }}
                            Dark Mode
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Log Out"
                            href="/apis/v1/idp/cyverse_logout/"
                            class="text-danger"
                            link-class="text-danger"
                        >
                            <i class="fas fa-door-closed fa-1x fa-fw"></i>
                            Log Out
                        </b-dropdown-item>
                    </b-nav-item-dropdown>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';

export default {
    name: 'Navigation',
    components: {},
    data() {
        return {
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
            crumbs: [],
            notFound: false,
            titleContent: 'breadcrumb',
            runs: [],
            currentRunPage: 0,
            loadingRuns: false,
            fields: [
                {
                    key: 'id',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'state',
                    label: 'State'
                },
                {
                    key: 'created',
                    sortable: true,
                    formatter: value => {
                        return `${moment(value).fromNow()} (${moment(
                            value
                        ).format('MMMM Do YYYY, h:mm a')})`;
                    }
                },
                {
                    key: 'flow_name',
                    label: 'Workflow',
                    sortable: true
                }
            ]
        };
    },
    computed: mapGetters([
        'darkMode',
        'currentUserDjangoProfile',
        'currentUserCyVerseProfile',
        'currentUserGitHubProfile',
        'loggedIn'
    ]),
    created: async function() {
        this.crumbs = this.$route.meta.crumb;
        await this.$store.dispatch('loadCurrentUser');
        // await this.loadUser();
        await this.loadRuns(0);
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        }
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        toggleDarkMode: function() {
            this.$store.dispatch('toggleDarkMode');
        },
        onRunSelected: function(items) {
            router.push({
                name: 'run',
                params: {
                    id: items[0].id,
                    username: this.currentUserDjangoProfile.username
                }
            });
        },
        statusToString(status) {
            switch (status) {
                case 1:
                    return 'Completed';
                case 2:
                    return 'Failed';
                case 3:
                    return 'Running';
                case 4:
                    return 'Created';
            }
        },
        async loadUser() {
            return axios
                .get(
                    `/apis/v1/users/get_by_username/?username=${this.$router.currentRoute.params.username}`
                )
                .then(response => {
                    if (response.data.django_profile)
                        this.djangoProfile = response.data.django_profile;
                    if (response.data.cyverse_profile)
                        this.cyverseProfile = response.data.cyverse_profile;
                    this.githubProfile = response.data.github_profile;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async loadRuns(page) {
            this.loadingRuns = true;
            return axios
                .get(
                    `/apis/v1/runs/${this.currentUserDjangoProfile.username}/get_by_user/${page}/`
                )
                .then(response => {
                    var ids = [];
                    this.runs = this.runs.concat(response.data);
                    this.runs = this.runs.filter(function(run) {
                        if (ids.indexOf(run.id) >= 0)
                            return false;
                        ids.push(run.id);
                        return true;
                    });
                    this.loadingRuns = false;
                    this.currentRunPage = this.currentRunPage + 1;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.loadingRuns = false;
                    throw error;
                });
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

.dropdown-custom:hover
  background-color: transparent !important

.crumb-light
  font-weight: 300
  color: $dark !important

.darkk
  background-color: #292b2c
</style>
