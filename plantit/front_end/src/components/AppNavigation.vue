<template>
    <div class="m-0 p-0">
        <b-navbar toggleable="lg" class="p-0 m-0">
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
            <b-collapse class="logo m-0 p-0" is-nav>
                <b-navbar-brand href="/" to="/" class="mr-0 ml-0 pr-0 pl-0">
                    <b-img
                        href="/"
                        width="60px"
                        :src="require('../assets/logo-right.png')"
                        alt="Plant IT"
                        style=""
                    ></b-img>
                </b-navbar-brand>
                <b-navbar-nav>
                    <b-nav-item to="/About" class="m-0 p-0">
                        <b-button variant="outline-dark">
                            <i class="fas fa-users fa-1x"></i>
                            About
                        </b-button>
                    </b-nav-item>
                    <b-nav-item to="/Guide" class="m-0 p-0">
                        <b-button variant="outline-dark">
                            <i class="fas fa-map-signs"></i>
                            Guide
                        </b-button>
                    </b-nav-item>
                    <b-nav-item to="/Documentation" class="m-0 p-0">
                        <b-button variant="outline-dark">
                            <i class="fas fa-book"></i>
                            Docs
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        href="https://github.com/Computational-Plant-Science/DIRT2_Webplatform/issues/new"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark">
                            <i class="fab fa-github fa-1x"></i>
                            Report Issue
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
                <b-navbar-nav class="ml-auto m-0 p-0">
                    <b-nav-item
                        v-if="isLoggedIn"
                        title="Dashboard"
                        to="/user/dashboard"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-home"></i>
                            Dashboard
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-if="isLoggedIn"
                        :title="this.info['username']"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark" to="/user/profile">
                            <i class="fas fa-user fa-1x"></i>
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
                            <i class="fas fa-door-closed"></i>
                            Log Out
                        </b-button>
                    </b-nav-item>
                    <b-nav-item
                        v-else
                        href="/login/?next=/user/dashboard"
                        class="m-0 p-0"
                    >
                        <b-button variant="outline-dark">
                            <i class="fas fa-door-open"></i>
                            Log In
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        <br />
    </div>
</template>

<script>
import UserApi from '@/services/apiV1/UserManager.js';
import Auth from '@/services/apiV1/Auth.js';

export default {
    name: 'AppNavigation',
    components: {},
    computed: {
        isLoggedIn() {
            return Auth.isLoggedIn();
        },
        routeName() {
            return this.$route.name;
        }
    },
    data() {
        return {
            info: {}
        };
    },
    mounted: function() {
        UserApi.getCurrentUser().then(info => (this.info = info));
    }
};
</script>

<style scoped lang="sass">
@import '../scss/_colors.sass'

img
  border-radius: 50%
  -webkit-transition: -webkit-transform .25s ease-in-out
          transition:         transform .25s ease-in-out

img:hover
  -webkit-transform: rotate(-180deg)
          transform: rotate(-180deg)
</style>
