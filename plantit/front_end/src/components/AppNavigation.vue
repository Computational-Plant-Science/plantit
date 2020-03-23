<template>
    <div>
        <b-navbar toggleable="lg">
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

            <b-navbar-brand href="#">
                <b-img
                        :src="require('../assets/logo.png')"
                        width="50px"
                        alt="Plant IT"
                ></b-img>
            </b-navbar-brand>

            <b-collapse class="border-bottom" is-nav>
                <b-navbar-nav>
                    <b-nav-item to="/">Home</b-nav-item>
                    <b-nav-item>Contact</b-nav-item>
                    <b-nav-item>FAQ</b-nav-item>
                </b-navbar-nav>
                <b-navbar-nav class="ml-auto">
                    <b-button
                            v-if="isLoggedIn"
                            size="md"
                            :title="this.info['username']"
                            class="user-profile"
                            to="/user/dashboard">
                        <span class="align-middle" style="vertical-align: middle">Dashboard</span>
                        <i class="fas fa-user-circle d-inline-block align-middle"></i>
                    </b-button>
                    <b-button
                            v-if="isLoggedIn"
                            size="md"
                            title="Log Out"
                            class="user-profile"
                            to="/logout/?next=/">
                        <span class="align-middle" style="vertical-align: middle">Log Out</span>
                        <i class="fas fa-sign-out-alt d-inline-block align-middle"></i>
                    </b-button>
                    <b-nav-item v-else href="/login/?next=/user/dashboard">Login</b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
    </div>
</template>

<script>
    import UserApi from '@/services/apiV1/UserManager.js';
    import Auth from '@/services/apiV1/Auth.js';

    export default {
        name: 'AppNavigation',
        computed: {
            isLoggedIn() {
                return Auth.isLoggedIn();
            },
            routeName() {
                return this.$route.name;
            }
        }, data() {
            return {
                info: {}
            };
        },
        mounted: function () {
            UserApi.getCurrentUser().then(info => (this.info = info));
        }
    };
</script>
