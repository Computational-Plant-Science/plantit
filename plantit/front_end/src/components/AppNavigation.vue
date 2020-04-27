<template>
    <div>
        <b-navbar toggleable="lg">
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

            <b-navbar-brand href="#" to="/">
                <b-img
                    :src="require('../assets/logo.png')"
                    width="35px"
                    alt="Plant IT"
                ></b-img>
            </b-navbar-brand>

            <b-collapse class="logo" is-nav>
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
        <br>
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
