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
                    <b-nav-item to="about">About</b-nav-item>
                    <b-nav-item>Contact</b-nav-item>
                    <b-nav-item>Public Datasets</b-nav-item>
                    <b-nav-item>FAQ</b-nav-item>
                    <b-nav-item v-if="isLoggedIn" href="/logout/?next=/">Logout</b-nav-item>
                    <b-nav-item v-else href="/login/?next=/user/dashboard">Login</b-nav-item>
                </b-navbar-nav>
                <b-navbar-nav class="ml-auto">
                    <b-nav-item class="ml-auto" to="/user/dashboard">Dashboard</b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
    </div>
</template>

<script>
    import Auth from '@/services/apiV1/Auth.js';

    export default {
        name: 'AppNavigation',
        computed: {
            isLoggedIn() {
                return Auth.isLoggedIn();
            }
        }
    };
</script>
