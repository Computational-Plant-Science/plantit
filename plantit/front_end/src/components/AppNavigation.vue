<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="sidebar-left"
            title="Sidebar"
            shadow="lg"
            bg-variant="white"
            no-header
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-3">
                    <b-row class="ml-3 mr-1">
                        <b-col align-self="center">
                            Welcome,
                            <b style="text-decoration: underline;"
                                ><i v-if="loading">
                                    <b-spinner
                                        variant="secondary"
                                        type="grow"
                                        label="Loading..."
                                    ></b-spinner>
                                </i>
                                <span v-else-if="!info">guest</span>
                                <span v-else>{{ info.first_name }}</span
                                >.
                            </b>
                        </b-col>
                        <b-col class="mr-0" md="auto">
                            <b-button
                                variant="outline-dark"
                                @click="hide"
                                title="Hide Sidebar"
                            >
                                <i class="fas fa-arrow-left fa-1x"></i>
                            </b-button>
                        </b-col>
                    </b-row>
                    <b-row align-v="center">
                        <b-col align-self="center" class="mr-4 ml-4 pt-2">
                            <!--Welcome<i v-if="loading">
                                    <b-spinner
                                        variant="secondary"
                                        type="grow"
                                        label="Loading..."
                                    ></b-spinner>
                                </i>
                                <span v-else-if="!info">, guest.</span>
                                <span v-else> {{ info.first_name }}</span>-->
                        </b-col>
                    </b-row>
                    <b-row class="m-0 p-0" v-if="!info">
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item href="/login/?next=/workflows/" class="m-0 p-0">
                                    <b-button
                                        variant="white"
                                        block
                                        class="text-left m-0"
                                    >
                                        <b-img
                                            :src="
                                                require('../assets/sponsors/cyversebw-notext.png')
                                            "
                                            height="18px"
                                            alt="Cyverse"
                                        ></b-img>
                                        Log In with CyVerse
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <hr />
                        </b-col>
                    </b-row>
                    <b-row class="ml-0 mr-0 pl-0 pr-0">
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item to="/" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-home fa-1x fa-fw"></i>
                                        Home
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/About" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-seedling fa-1x fa-fw"
                                        ></i>
                                        About
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/Guide" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-map-signs fa-1x fa-fw"
                                        ></i>
                                        Guide
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/Docs" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-book fa-1x fa-fw"></i>
                                        Docs
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                            <hr />
                        </b-col>
                    </b-row>
                    <b-row class="ml-0 mr-0 pl-0 pr-0">
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item class="m-0 p-0" title="Slack">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i class="fab fa-slack fa-1x fa-fw"></i>
                                        Slack
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    class="m-0 p-0"
                                    title="Github"
                                    href="https://github.com/Computational-Plant-Science/plantit"
                                >
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
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
            <template slot="footer">
                <b-container class="p-3">
                    <b-row>
                        <b-col align-self="center">
                            <b-img
                                center
                                width="75px"
                                :src="require('../assets/logo.png')"
                                alt="Plant IT"
                            ></b-img>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col class="text-center" align-self="center">
                            <h5>
                                <b-badge
                                    variant="dark"
                                    :class="
                                        version && version.includes('alpha')
                                            ? 'text-warning'
                                            : 'text-success'
                                    "
                                    >{{ version || '...' }}
                                </b-badge>
                            </h5>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-navbar
            toggleable="sm"
            class="logo p-0 pt-4 pb-4 overflow-hidden"
            style="max-height: 60px"
            fixed="top"
        >
            <b-collapse class="m-0 p-0" is-nav>
                <b-navbar-nav class="m-0 p-0 pl-1 mr-1">
                    <b-nav-item class="m-0 p-0" v-b-toggle.sidebar-left>
                        <b-button
                            class="brand-img m-0 p-0"
                            v-bind:class="{ 'not-found': not_found }"
                            variant="outline-white"
                            @mouseenter="titleContent = 'sidebar'"
                            @mouseleave="titleContent = 'breadcrumb'"
                        >
                            <b-img
                                class="m-0 p-0 mb-4"
                                center
                                width="50px"
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
                            Show Sidebar
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
                            isLoggedIn && info.profile
                                ? info.profile.github_username === ''
                                : false
                        "
                        title="Link GitHub Account"
                        href="/apis/v1/profiles/github_request_identity/"
                        class="m-0 p-0"
                    >
                        <b-button class="text-left" variant="success">
                            <i class="fab fa-github"></i>
                            Link GitHub Account
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        title="Workflows"
                        to="/workflows"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-stream fa-1x fa-fw"></i>
                            Workflows
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        title="Runs"
                        to="/runs"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-terminal fa-1x fa-fw"></i>
                            Runs
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        title="Profile"
                        class="m-0 p-0"
                        to="/profile"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-user fa-1x"></i>
                            {{
                                info.first_name
                                    ? info.first_name
                                    : info.username
                            }}
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        title="Log Out"
                        to="/logout"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-danger">
                            <i class="fas fa-door-closed fa-1x"></i>
                            Log Out
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        <b-alert
                class="mt-5 pt-4"
            :show="reload_alert_dismiss_countdown"
            dismissible
            variant="success"
            @dismissed="reload_alert_dismiss_countdown < 0"
            @dismiss-count-down="countDownChanged"
        >
            <p>
                User information updated. Thanks,
                {{ this.info ? this.info.first_name : '' }}!
            </p>
        </b-alert>
        <EditUserInfoModal
            :v-if="!this.loading && this.profileIncomplete"
            modal-id="editUserInfoModalNav"
            :username="
                this.info
                    ? this.info.username
                    : ''
            "
            :first_name="
                this.info
                    ? this.info.first_name
                    : ''
            "
            :last_name="
                this.info
                    ? this.info.last_name
                    : ''
            "
            :country="
                this.info
                    ? this.info.profile.country
                    : ''
            "
            :institution="
                this.info
                    ? this.info.profile.institution
                    : ''
            "
            :field_of_study="
                this.info
                    ? this.info.profile.field_of_study
                    : ''
            "
            @saveUserInfo="saveUserInfo"
        >
        </EditUserInfoModal>
    </div>
</template>

<script>
import UserApi from '@/services/apiV1/UserManager.js';
import Auth from '@/services/apiV1/Auth.js';
import Version from '@/services/apiV1/VersionManager.js';
import EditUserInfoModal from '@/components/collections/EditUserInfoModal';

export default {
    name: 'AppNavigation',
    components: {
        EditUserInfoModal
    },
    computed: {
        isLoggedIn() {
            return Auth.isLoggedIn() && this.info;
        },
        routeName() {
            return this.$route.name;
        },
        profileIncomplete() {
            return (
                !this.loading &&
                this.info &&
                !(
                    this.info.profile.country &&
                    this.info.profile.institution &&
                    this.info.profile.field_of_study
                )
            );
        }
    },
    data() {
        return {
            loading: true,
            version: null,
            info: {},
            crumbs: [],
            not_found: false,
            reload_alert_dismiss_seconds: 5,
            reload_alert_dismiss_countdown: 0,
            show_reload_alert: false,
            titleContent: 'breadcrumb'
        };
    },
    mounted: function() {
        this.reload();
        this.crumbs = this.$route.meta.crumb;
        Version.getCurrentRelease().then(version => {
            this.version = version;
        });
        // this.not_found = this.$route.name === '404';
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        }
    },
    methods: {
        reload() {
            UserApi.getCurrentUser().then(info => {
                this.info = info;
                this.loading = false;
                if (this.profileIncomplete) {
                    this.$bvModal.show('editUserInfoModalNav');
                }
            });
        },
        countDownChanged(dismissCountDown) {
            this.reload_alert_dismiss_countdown = dismissCountDown;
        },
        showAlert() {
            this.reload_alert_dismiss_countdown = this.reload_alert_dismiss_seconds;
        },
        saveUserInfo(
            userName,
            firstName,
            lastName,
            country,
            continent,
            institution,
            institutionType,
            fieldOfStudy
        ) {
            UserApi.updateUserInfo(
                userName,
                firstName,
                lastName,
                country,
                continent,
                institution,
                institutionType,
                fieldOfStudy
            ).then(() => {
                this.reload();
                this.$router.go()
                // this.showAlert();
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

a
    color: $dark !important
    border: none !important

a:hover
    // color: $color-highlight !important
    text-decoration-color: $color-highlight
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
    margin-top: 14px !important
    font-size: 14pt !important
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

a
  font-weight: 300
  color: $dark // !important
  // text-decoration: underline
  // text-decoration-color: $color-button
</style>
