<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="sidebar-left"
            title="Dashboard"
            shadow="lg"
            bg-variant="white"
            no-header
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-3">
                    <b-row>
                        <b-col>
                            <b-button
                                variant="outline-dark"
                                @click="hide"
                                title="Hide Sidebar"
                            >
                                <i class="fas fa-arrow-left fa-2x"></i>
                            </b-button>
                        </b-col>
                        <b-col md="auto" class="pr-0 mr-1">
                            <h1>
                                PlantIT
                            </h1>
                        </b-col>
                        <b-col md="auto" class="pl-0 ml-1">
                            <b-badge variant="dark" class="text-success">{{
                                version
                            }}</b-badge>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <p class="m-3">
                                Welcome,
                                <b
                                    >{{
                                        info.profile
                                            ? info.first_name
                                            : info.username
                                    }}.</b
                                >
                                <br />
                                <br />
                                See the
                                <b-link to="/Guide">User Guide</b-link> to learn
                                how to run workflows, or the
                                <b-link to="/Docs">Developer Docs</b-link> to
                                create and host your own.
                            </p>
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
                                        PlantIT Home
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/About" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i
                                            class="fas fa-question fa-1x fa-fw"
                                        ></i>
                                        About PlantIT
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
                                        User Guide
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item to="/Documentation" class="m-0 p-0">
                                    <b-button
                                        variant="outline-dark"
                                        block
                                        class="text-left"
                                    >
                                        <i class="fas fa-book fa-1x fa-fw"></i>
                                        Developer Docs
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                        </b-col>
                    </b-row>
                    <hr />
                    <b-row class="ml-0 mr-0 pl-0 pr-0">
                        <b-col class="ml-0 mr-0 pl-0 pr-0">
                            <b-nav vertical class="ml-0 mr-0 pl-0 pr-0">
                                <b-nav-item
                                    v-if="isLoggedIn"
                                    title="Dashboard"
                                    to="/user/dashboard"
                                    class="m-0 p-0"
                                >
                                    <b-button variant="outline-dark">
                                        <i
                                            class="fas fa-desktop fa-1x fa-fw"
                                        ></i>
                                        Dashboard
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    v-if="isLoggedIn"
                                    :title="
                                        loading
                                            ? 'Loading...'
                                            : 'Profile: ' + info['username']
                                    "
                                    class="m-0 p-0"
                                    to="/user/profile"
                                >
                                    <b-button variant="outline-dark">
                                        <i class="fas fa-user fa-1x fa-fw"></i>
                                        Profile
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    v-if="isLoggedIn"
                                    title="Log Out"
                                    to="/logout/?next=/"
                                    class="m-0 p-0"
                                >
                                    <b-button variant="outline-dark">
                                        <i
                                            class="fas fa-door-closed fa-1x fa-fw"
                                        ></i>
                                        Log Out
                                    </b-button>
                                </b-nav-item>
                                <b-nav-item
                                    v-else
                                    href="/login/?next=/user/dashboard"
                                    class="m-0 p-0"
                                >
                                    <b-button variant="outline-dark">
                                        <i
                                            class="fas fa-door-open fa-2x fa-fw"
                                        ></i>
                                        Log In
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
                                width="100px"
                                :src="require('../assets/logo.png')"
                                alt="Plant IT"
                            ></b-img>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-navbar
            toggleable="lg"
            class="logo m-0 p-0 pl-2 pr-2"
            variant="white"
        >
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
            <b-collapse class="m-0 p-0" is-nav>
                <b-navbar-nav class="m-0 p-0 pl-3">
                    <b-nav-item
                        class="m-0 p-0"
                        v-b-toggle.sidebar-left
                        title="Show Sidebar"
                    >
                        <b-button
                            class="brand-img m-0 p-0"
                            variant="white"
                            style="color: white"
                        >
                            <b-img
                                center
                                width="32px"
                                :src="require('../assets/logo.png')"
                                alt="Plant IT"
                            ></b-img>
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
                <b-navbar-brand
                    href="/"
                    class="align-middle ml-3 title"
                    title="PlantIT Home"
                    >PlantIT</b-navbar-brand
                >
                <b-navbar-nav class="ml-auto m-0 p-0">
                    <b-nav-item class="m-0 p-0" title="Slack">
                        <b-button variant="outline-dark">
                            <i class="fab fa-slack fa-2x"></i>
                        </b-button>
                    </b-nav-item>
                    <b-nav-item class="m-0 p-0" title="Github" to="https://github.com/Computational-Plant-Science/plantit">
                        <b-button variant="outline-dark">
                            <i class="fab fa-github fa-2x"></i>
                        </b-button>
                    </b-nav-item>
                    <!--<b-nav-item class="m-0 p-0" disabled>
                        <i class="fas fa-slash fa-2x text-success"></i>
                    </b-nav-item>
                    <b-nav-item to="/" class="m-0 p-0" title="PlantIT Home">
                        <b-button
                            variant="outline-dark"
                            block
                            class="text-left"
                        >
                            <i class="fas fa-home fa-2x fa-fw"></i>
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        to="/About"
                        class="m-0 p-0"
                        title="About PlantIT"
                    >
                        <b-button
                            variant="outline-dark"
                            block
                            class="text-left"
                        >
                            <i class="fas fa-question fa-2x fa-fw"></i>
                        </b-button>
                    </b-nav-item>
                    <b-nav-item to="/Guide" class="m-0 p-0" title="User Guide">
                        <b-button
                            variant="outline-dark"
                            block
                            class="text-left"
                        >
                            <i class="fas fa-map-signs fa-2x fa-fw"></i>
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        to="/Documentation"
                        class="m-0 p-0"
                        title="Developer Docs"
                    >
                        <b-button
                            variant="outline-dark"
                            block
                            class="text-left"
                        >
                            <i class="fas fa-book fa-2x fa-fw"></i>
                        </b-button>
                    </b-nav-item>-->
                    <b-nav-item class="m-0 p-0" disabled>
                        <i class="fas fa-slash fa-2x text-success"></i>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        title="Dashboard"
                        to="/user/dashboard"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-desktop fa-2x"></i>
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        :title="
                            loading
                                ? 'Loading...'
                                : 'Profile: ' + info['username']
                        "
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark" to="/user/profile">
                            <i class="fas fa-user fa-2x"></i>
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        title="Log Out"
                        to="/logout/?next=/"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-door-closed fa-2x"></i>
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-else
                        href="/login/?next=/user/dashboard"
                        class="m-0 p-0"
                        title="Log In"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-door-open fa-2x"></i>
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        <br />
        <br />
        <EditUserInfoModal
            :prompt="true"
            modal-id="editUserInfoModalNav"
            :username="this.loading ? 'Loading...' : this.info.username"
            :first_name="this.loading ? 'Loading...' : this.info.first_name"
            :last_name="this.loading ? 'Loading...' : this.info.last_name"
            :country="this.loading ? 'Loading...' : this.info.profile.country"
            :continent="
                this.loading ? 'Loading...' : this.info.profile.continent
            "
            :institution="
                this.loading ? 'Loading...' : this.info.profile.institution
            "
            :institution_type="
                this.loading ? 'Loading...' : this.info.profile.institution_type
            "
            :field_of_study="
                this.loading ? 'Loading...' : this.info.profile.field_of_study
            "
            @saveUserInfo="saveUserInfo"
        >
        </EditUserInfoModal>
    </div>
</template>

<script>
import UserApi from '@/services/apiV1/UserManager.js';
import Auth from '@/services/apiV1/Auth.js';
import EditUserInfoModal from '@/components/collections/EditUserInfoModal';

export default {
    name: 'AppNavigation',
    components: {
        EditUserInfoModal
    },
    computed: {
        isLoggedIn() {
            return Auth.isLoggedIn();
        },
        routeName() {
            return this.$route.name;
        },
        profileIncomplete() {
            return (
                !this.loading &&
                !(
                    this.info.profile.country &&
                    this.info.profile.continent &&
                    this.info.profile.institution &&
                    this.info.profile.institution_type &&
                    this.info.profile.field_of_study
                )
            );
        }
    },
    data() {
        return {
            loading: true,
            version: 'alpha',
            info: {}
        };
    },
    mounted: function() {
        this.reload();
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
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import '../scss/main.sass'
@import '../scss/_colors.sass'

.brand-img
    border-radius: 50%
    -webkit-transition: -webkit-transform .2s ease-in-out
        transition: transform .2s ease-in-out

.brand-img:hover
    color: $dark
    -webkit-transform: rotate(90deg)
        transform: rotate(90deg)

.title
    font-size: 26pt !important
    font-weight: 200
    color: $dark !important
    border: none
    border-bottom: 1px solid transparent

.title:hover
    color: $secondary !important
</style>
