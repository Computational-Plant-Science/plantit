<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="sidebar-left"
            shadow="lg"
            :bg-variant="profile.darkMode ? 'dark' : 'light'"
            :text-variant="profile.darkMode ? 'dark' : 'light'"
            no-header-close
            width="550px"
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-0">
                    <b-row
                        class="ml-4 mr-4 mb-4 mt-2 pl-0 pr-0 text-left"
                        align-v="start"
                    >
                        <b-col
                            class="ml-0 mr-0 pl-0 pr-0"
                            align-self="center"
                            md="auto"
                        >
                            <b-button
                                :variant="profile.darkMode ? 'dark' : 'light'"
                                class="text-left m-0"
                                @click="hide"
                            >
                                <i class="fas fa-arrow-left fa-1x fa-fw"></i>
                                Hide
                            </b-button>
                        </b-col>
                        <b-col class="ml-0 mr-0 pl-0 pr-0" align-self="start">
                            <b-button
                                disabled
                                block
                                size="lg"
                                :variant="profile.darkMode ? 'dark' : 'light'"
                                class="text-center m-0"
                            >
                                <b>Your Runs</b>
                            </b-button>
                        </b-col>
                        <b-col
                            md="auto"
                            class="ml-0 mr-0 pl-0 pr-0 text-right"
                            align-self="center"
                        >
                            <b-button
                                :variant="profile.darkMode ? 'dark' : 'light'"
                                class="text-right m-0"
                                @click="loadRuns(0)"
                            >
                                <i class="fas fa-sync-alt fa-1x fa-fw"></i>
                                Reload
                            </b-button>
                        </b-col>
                    </b-row>
                    <b-row
                        v-if="!loadingRuns"
                        class="m-4 mb-1 pl-0 pr-0"
                        align-v="center"
                    >
                        <b-col class="m-0 pl-0 pr-0 text-center">
                            <b-list-group class="text-left m-0 p-0">
                                <b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="run in runs"
                                    v-bind:key="run.id"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                            : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                    "
                                    @click="onRunSelected(run)"
                                >
                                    <b-img
                                        v-if="
                                            run.flow_image_url !== undefined &&
                                                run.flow_image_url !== null
                                        "
                                        rounded
                                        class="card-img-right"
                                        style="max-width: 4rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                        right
                                        :src="run.flow_image_url"
                                    ></b-img>
                                    <a
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        :href="`/run/${run.id}`"
                                        >{{ run.id }}</a
                                    >
                                    <br />
                                    <b-badge
                                        v-for="tag in run.tags"
                                        v-bind:key="tag"
                                        class="mr-1"
                                        variant="secondary"
                                        >{{ tag }}
                                    </b-badge>
                                    <br v-if="run.tags.length > 0" />
                                    <small v-if="!run.is_complete"
                                        >Running</small
                                    >
                                    <b-badge
                                        :variant="
                                            run.is_failure || run.is_timeout
                                                ? 'danger'
                                                : run.is_cancelled
                                                ? 'secondary'
                                                : 'success'
                                        "
                                        v-else
                                        >{{ run.job_status }}</b-badge
                                    >
                                    <small> on </small>
                                    <b-badge
                                        class="ml-0 mr-0"
                                        variant="secondary"
                                        >{{ run.target }}</b-badge
                                    ><small> {{ prettify(run.updated) }}</small>
                                    <br />
                                    <small class="mr-1"
                                        ><a
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                            :href="
                                                `https://github.com/${run.workflow_owner}/${run.workflow_name}`
                                            "
                                            ><i class="fab fa-github fa-fw"></i>
                                            {{ run.workflow_owner }}/{{
                                                run.workflow_name
                                            }}</a
                                        >
                                    </small>
                                </b-list-group-item>
                            </b-list-group>
                        </b-col>
                    </b-row>
                    <b-row
                        class="ml-0 mr-0 pl-0 pr-0 mt-0 mb-3 text-center"
                        align-v="start"
                    >
                        <b-col align-self="start" class="m-0 pl-0 pr-0">
                            <b-spinner
                                v-if="loadingRuns || loadingMoreRuns"
                                type="grow"
                                variant="secondary"
                            ></b-spinner>
                            <b-nav
                                v-else-if="runs.length > 0"
                                vertical
                                class="m-0 pl-0 pr-0"
                            >
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        :variant="
                                            profile.darkMode ? 'dark' : 'light'
                                        "
                                        :disabled="loadingRuns"
                                        block
                                        class="text-center m-0"
                                        @click="loadRuns(currentRunPage + 1)"
                                    >
                                        <i
                                            class="fas fa-chevron-down fa-fw"
                                        ></i>
                                        Load More
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-center text-light'
                                        : 'text-center text-dark'
                                "
                                v-else
                            >
                                You haven't run any workflows yet.
                            </p>
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
            :variant="profile.darkMode ? 'dark' : 'white'"
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
                            class="ml-3"
                            :class="
                                profile.darkMode ? 'crumb-dark' : 'crumb-light'
                            "
                        >
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'crumb-dark'
                                        : 'crumb-light'
                                "
                            >
                                Your Runs
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
                            class="ml-0 mr-0"
                        >
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'crumb-dark'
                                        : 'crumb-light'
                                "
                            >
                                {{ crumb.text }}
                            </h5>
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                </transition>
              <b-navbar-nav class="ml-auto m-0 p-0">
                    <b-nav-item
                        v-if="
                            profile.loggedIn
                                ? profile.githubProfile === null
                                : false
                        "
                        title="Log in to GitHub"
                        href="/apis/v1/idp/github_request_identity/"
                        class="ml-0 mr-0"
                    >
                        <b-button
                            class="mt-1 text-left"
                            variant="success"
                            size="sm"
                        >
                            <i class="fab fa-github"></i>
                            Log in to GitHub
                        </b-button>
                    </b-nav-item>
                    <b-nav-item-dropdown
                        right
                        v-if="profile.loggedIn"
                        :title="profile.djangoProfile.username"
                        class="p-2 m-3 dropdown-custom"
                        :menu-class="
                            profile.darkMode ? 'theme-dark' : 'theme-light'
                        "
                        style="font-size: 12pt"
                    >
                        <template #button-content>
                            <b-button
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                class="m-0 ml-0 mr-2 text-left"
                                size="sm"
                            >
                                <b-img
                                    v-if="profile.githubProfile"
                                    class="avatar m-0 mb-1 p-0 github-hover logo"
                                    style="min-width: 22px; min-height: 22px; position: relative; left: -3px; top: 1.5px; border: 1px solid white;"
                                    rounded="circle"
                                    :src="
                                        profile.githubProfile
                                            ? profile.githubProfile.avatar_url
                                            : ''
                                    "
                                ></b-img>
                                <i v-else class="far fa-user"></i>
                                {{
                                    profile.cyverseProfile
                                        ? profile.cyverseProfile.first_name
                                        : profile.djangoProfile.username
                                }}
                                <i class="fas fa-caret-down fa-fw"></i>
                            </b-button>
                        </template>
                        <b-dropdown-item
                            title="Workflows"
                            to="/workflows"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-stream fa-1x fa-fw"></i>
                            Workflows
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Servers"
                            to="/servers"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-server fa-1x fa-fw"></i>
                            Servers
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Users"
                            to="/users"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-users fa-1x fa-fw"></i>
                            Users
                        </b-dropdown-item>
                        <hr class="mt-2 mb-2" style="border-color: gray" />
                        <b-dropdown-item
                            title="Docs"
                            href="https://plantit.readthedocs.io/en/latest"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-book fa-1x fa-fw"></i>
                            Docs
                        </b-dropdown-item>
                        <b-dropdown-item
                            href="https://github.com/Computational-Plant-Science/plantit"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="GitHub"
                        >
                            <i class="fab fa-github fa-1x fa-fw"></i>
                            Github
                        </b-dropdown-item>
                        <b-dropdown-item
                            href="#"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="Slack"
                        >
                            <i class="fab fa-slack fa-1x fa-fw"></i>
                            Slack
                        </b-dropdown-item>
                        <hr class="mt-2 mb-2" style="border-color: gray" />
                        <b-dropdown-item
                            title="Profile"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            :to="
                                '/user/' + profile.djangoProfile.username + '/'
                            "
                        >
                            <i class="fas fa-user fa-1x fa-fw"></i>
                            User Profile
                        </b-dropdown-item>
                        <b-dropdown-item
                            :title="
                                `${
                                    profile.darkMode
                                        ? 'Light Mode'
                                        : 'Dark Mode'
                                }`
                            "
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            @click="toggleDarkMode"
                        >
                            <i
                                v-if="profile.darkMode"
                                class="fas fa-sun fa-1x fa-fw"
                            ></i>
                            <i v-else class="fas fa-moon fa-1x fa-fw"></i>
                            {{ profile.darkMode ? 'Light Mode' : 'Dark Mode' }}
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Log Out"
                            @click="logOut"
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
            // run status constants
            PENDING: 'PENDING',
            STARTED: 'STARTED',
            SUCCESS: 'SUCCESS',
            FAILURE: 'FAILURE',
            REVOKED: 'REVOKED',
            // websockets
            socketMessage: '',
            // user data
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
            crumbs: [],
            notFound: false,
            titleContent: 'breadcrumb',
            runs: [],
            currentRunPage: 0,
            loadingRuns: false,
            loadingMoreRuns: false,
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
                    key: 'workflow_name',
                    label: 'Workflow',
                    sortable: true
                }
            ]
        };
    },
    computed: mapGetters(['profile']),
    created: async function() {
        this.crumbs = this.$route.meta.crumb;
        await this.$store.dispatch('loadProfile');
        // TODO await this.$store.dispatch('loadRuns');

        // subscribe to run update channel
        this.sockets.subscribe('update_status', data => {
            alert(data.text);
        });
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        }
    },
    methods: {
        logOut() {
            sessionStorage.clear();
            window.location.replace('/apis/v1/idp/cyverse_logout/');
        },
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
                    id: items[0].id
                }
            });
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
            this.loadingRuns = page === 0;
            this.loadingMoreRuns = !this.loadingRuns;
            return axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/get_by_user/${page}/`
                )
                .then(response => {
                    var ids = [];
                    this.runs = this.runs.concat(response.data);
                    this.runs = this.runs.filter(function(run) {
                        if (ids.indexOf(run.id) >= 0) return false;
                        ids.push(run.id);
                        return true;
                    });
                    this.runs.sort(function(a, b) {
                        return new Date(b.updated) - new Date(a.updated);
                    });
                    this.loadingRuns = false;
                    this.loadingMoreRuns = false;
                    this.currentRunPage = page + 1;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.loadingRuns = false;
                    this.loadingMoreRuns = false;
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
  font-size: 16px
  font-weight: 200
  color: white !important
  // text-decoration: underline
  // text-decoration-color: $color-button

.dropdown-custom:hover
  background-color: transparent !important

.crumb-light
  font-size: 16px
  font-weight: 200
  color: $dark !important

a
  text-decoration: none
  text-decoration-color: $color-button

a:hover
  text-decoration: underline
  text-decoration-color: $color-button

.darkk
  background-color: #292b2c
</style>
